---
name: portrait-wordcloud
description: Use when the user wants to turn a clear, at-least-half-body real portrait photo plus academic paper text into a Nobel Prize laureate style portrait wordcloud image. This skill guides intake, uses a bundled keyword-extraction prompt, uses a bundled Nobel portrait image prompt, requires confirmation after keyword extraction and after portrait generation, then composes a final image with a protected portrait and layered academic wordcloud background.
---

# Portrait Wordcloud

## Overview

Create a Nobel Prize style academic portrait wordcloud from a clear real portrait photo that shows at least the upper half of the body, plus academic paper text. The agent should run this as a guided workflow with two mandatory confirmation gates: one after keyword extraction and one after Nobel-style portrait generation.

## Operating Mode

Use a stateful intake. Do not ask the user for everything at once when a next concrete step is obvious.

Before asking the user to upload a real portrait photo, determine the current agent's image generation/editing capability:

- If the capability is provided by OpenAI and supports the `image2` model, plan to generate the Nobel-style portrait inside the agent with `image2`.
- If there is no image generation/editing capability, or the available capability is from another provider, tell the user that this workflow recommends OpenAI `image2` for the Nobel-style portrait. Ask the user to generate the Nobel-style portrait with `image2` externally if possible, then upload that generated style image back to the agent. In this path, do not ask for the original real portrait photo unless the user still wants the prompt or needs help preparing the external generation.

Then continue the intake:

1. If OpenAI `image2` is available and no portrait photo is available, ask for one clear real portrait photo that shows at least the upper half of the body.
2. If OpenAI `image2` is not available and no approved Nobel-style portrait is available, show the exact Nobel portrait prompt and ask the user to upload the externally generated Nobel-style portrait.
3. If no paper text is available, ask for paper titles, abstracts, body text, or a paper file.
4. If both approved portrait input and paper text are available, begin keyword extraction immediately.
5. If the user already provides an approved keyword JSON, skip extraction confirmation only if they explicitly say it is approved.
6. If the user already provides an approved Nobel-style portrait, skip image generation confirmation only if they explicitly say it is approved.

Create a working output directory named `portrait-wordcloud-output` unless the user gives a location. Save durable intermediate files there so the workflow can resume.

Use the bundled prompts without asking the user to provide them:

- `references/keyword-extraction-prompt.md`
- `references/nobel-portrait-prompt.md`

## Workflow

### 1. Keyword Extraction

Use `references/keyword-extraction-prompt.md` with the supplied paper text.

Requirements:

- Produce a flat JSON dictionary sorted by descending weight.
- Prefer 80-120 terms when the source text is rich enough.
- Save the candidate dictionary as `keywords.candidate.json`.
- Present a concise preview to the user: total term count plus the top 20 terms.
- Stop and ask for approval before any final composition.

Suggested confirmation prompt:

```text
我已提取出关键词候选集，共 N 个。下面是权重最高的 20 个。你确认这组关键词可以用于词云吗？也可以直接告诉我要删除、增加或调权重的词。
```

After approval, save the final dictionary as `keywords.json`.

### 2. Nobel-Style Portrait

Use `references/nobel-portrait-prompt.md` with the user's clear at-least-half-body real portrait photo.

Preferred path:

- If OpenAI image generation/editing with the `image2` model is available, generate the Nobel-style portrait inside the agent with `image2`.
- Save the candidate image as `nobel_portrait.candidate.png` or the native image format produced by the tool.
- Show the generated image to the user.
- Stop and ask for approval before composition.

Fallback path:

- If no image editing/generation capability is available, or if the available image generation/editing capability is from another provider, tell the user this workflow recommends OpenAI `image2` for the Nobel-style portrait.
- Show the exact prompt from `references/nobel-portrait-prompt.md`.
- Ask the user to generate the image externally with `image2` if possible and upload the generated Nobel-style portrait.
- Once uploaded, show it back and ask for approval.

Suggested confirmation prompt:

```text
这是生成的人物图。请确认是否保留这个版本进入词云合成；如果需要，我可以让你重新生成或换一张已生成图片。
```

After approval, save the final portrait as `nobel_portrait.png`.

### 3. Environment Check

Before composition, run:

```bash
python3 <skill-dir>/scripts/check_environment.py
```

If dependencies are missing, the script prints the exact install command. Tell the user the missing packages and ask whether to install them or run the composition in another environment.

After user approval, run:

```bash
python3 <skill-dir>/scripts/check_environment.py --install
```

Use `--user` if the environment should avoid system site-packages, or `--upgrade` if a fresh package version is needed. Do not run `--install` without user approval.

### 4. Composition

Run:

```bash
python3 <skill-dir>/scripts/run_portrait_wordcloud.py \
  --portrait <output-dir>/nobel_portrait.png \
  --keywords-json <output-dir>/keywords.json \
  --out-dir <output-dir>
```

Inspect `wordcloud_preview.png` and `portrait_mask_preview.png`.

If words overlap the face, hair, glasses, or shoulders:

- Increase `--portrait-padding` by 6-12.
- Regenerate once.

If the background words are too blurred or too faint:

- Lower `--far-blur`.
- Raise `--far-alpha` slightly.

If the composition feels unbalanced:

- Change `--random-state`.
- Regenerate once or twice, then choose the best preview.

Return the final image path and show the image when the interface supports it.

## Composition Script

`scripts/run_portrait_wordcloud.py` creates:

- `portrait_mask.png`
- `wordcloud_background_mask.png`
- `portrait_mask_preview.png`
- `wordcloud_layer.png`
- `wordcloud_preview.png`

Useful options:

- `--word-color "#A69A6C"` controls the word color.
- `--random-state 32` changes placement while keeping deterministic output.
- `--max-words 720` controls density.
- `--safe-edge 58` blocks words near the image border.
- `--portrait-padding 18` increases or decreases protected space around portrait strokes.
- `--far-blur 0.65` controls background word softness.
- `--far-alpha 62` controls background word visibility.

Use the bundled font at `assets/fonts/SourceHanSerifSC-Regular.otf` unless a better local CJK font is available.

## Resume Rules

If the workflow is interrupted, resume from the latest approved artifact:

- `keywords.json` means keyword extraction is complete.
- `nobel_portrait.png` means portrait generation is complete.
- `wordcloud_preview.png` means composition is complete.

Never silently overwrite approved files. Write candidates as `*.candidate.*` and replace the approved file only after user confirmation.

## Quality Checks

Before finishing, verify:

- The final image uses the approved generated portrait, not the original real photo.
- The portrait face, hair, glasses, and shoulders remain clear and are not covered by words.
- Background words are readable but visually secondary to the portrait and largest keywords.
- Keywords reflect the confirmed dictionary.
- The final output is a 4:3 horizontal composition when the generated portrait allows it.

## Capability Fallbacks

This skill must remain usable across agents with different tool access.

- Before asking for the original real portrait photo, check whether OpenAI image generation/editing with the `image2` model is available.
- If OpenAI `image2` is available, generate the Nobel-style portrait inside the agent.
- If OpenAI `image2` is unavailable, even when another provider's image generation is available, explain that this workflow recommends `image2`, show `references/nobel-portrait-prompt.md`, and ask the user to generate the Nobel-style portrait externally with `image2` if possible, then upload that generated image.
- If the agent cannot process uploaded paper files directly, ask the user to paste the relevant title, abstract, or body text.
- If the local Python environment lacks required packages (`Pillow`, `numpy`, `scipy`, `wordcloud`), use `scripts/check_environment.py` to print the missing packages and install command. Only run `scripts/check_environment.py --install` after user approval.

## User Experience Rules

- Start by briefly explaining what the workflow creates, the main steps, and the two confirmation gates before asking for uploads.
- Keep the user oriented with one next action at a time.
- Do not expose implementation details unless the user asks.
- Do not continue past keyword extraction without confirmation.
- Do not continue past Nobel-style portrait generation without confirmation.
- If the user says "looks good", "确认", "可以", or equivalent after a candidate preview, treat that candidate as approved.
- If the user asks to adjust keywords or regenerate the portrait, update only that stage and continue from there.

## Distribution Note

This skill is designed for GitHub link installation. Users can ask Codex to install a skill from the repository path that contains this `SKILL.md`, then restart Codex or open a new thread to use it.
