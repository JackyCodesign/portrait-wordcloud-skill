---
name: portrait-wordcloud-guide
description: Bootstrap guide for installing or running the Portrait Wordcloud skill from a single remote markdown link.
homepage: https://raw.githubusercontent.com/JackyCodesign/portrait-wordcloud-skill/main/guide.md
metadata:
  version: "0.1.0"
  skill: "portrait-wordcloud"
---

# Portrait Wordcloud Bootstrap Guide

You are helping the user create a Nobel Prize style academic portrait wordcloud from a clear real portrait photo that shows at least the upper half of the body, plus paper text.

Follow this guide as an executable task plan. If the current agent supports Codex skills, install the skill. If not, run the workflow directly from this guide and the linked resources.

Start with a short, friendly explanation before asking for any files. The user should understand what this workflow will create, what inputs are needed, and where the confirmation points are.

Suggested opening message:

```text
我可以帮你做一张“诺奖风格人像学术词云”：先把人物处理成类似诺贝尔奖官网的黑金线稿肖像，再从论文内容里提取关键词，最后把关键词排成一张以人物为中心的词云图。

整个过程我会一步步带你做，不会一次性要你准备所有东西。大概会有 4 步：
1. 先确认我这边能不能直接生成 OpenAI image2 风格图。
2. 准备人物图：如果我能用 image2，你上传至少半身、脸部清晰的真人照片；如果不能，我会给你提示词，你用 image2 生成好风格图后再传给我。
3. 你提供论文标题、摘要、正文或论文文件，我提取关键词，并先给你确认。
4. 你确认人物图和关键词后，我再合成最终词云图。

我们先从图片生成能力检查开始。
```

## Resource URLs

This guide is hosted at:

```text
https://raw.githubusercontent.com/JackyCodesign/portrait-wordcloud-skill/main
```

Use that URL as `<BASE_URL>` if you need to download the resources manually.

- Skill directory: `<BASE_URL>/portrait-wordcloud/`
- Skill file: `<BASE_URL>/portrait-wordcloud/SKILL.md`
- UI metadata: `<BASE_URL>/portrait-wordcloud/agents/openai.yaml`
- Keyword prompt: `<BASE_URL>/portrait-wordcloud/references/keyword-extraction-prompt.md`
- Nobel portrait prompt: `<BASE_URL>/portrait-wordcloud/references/nobel-portrait-prompt.md`
- Environment check script: `<BASE_URL>/portrait-wordcloud/scripts/check_environment.py`
- Composition script: `<BASE_URL>/portrait-wordcloud/scripts/run_portrait_wordcloud.py`
- Bundled font: `<BASE_URL>/portrait-wordcloud/assets/fonts/SourceHanSerifSC-Regular.otf`

## First Choice: Install As A Skill

If the agent can install skills from a GitHub repository path or URL, install `portrait-wordcloud` from the hosted skill directory.

Suggested user-facing message after install:

```text
Portrait Wordcloud 已安装。请重启 Codex 或开新线程，然后启动 Portrait Wordcloud 向导。我会先说明流程，再一步步带你准备人物图和论文内容。
```

If skill installation is not available, continue with the direct-run path below.

## Direct-Run Path

Use this path when:

- The agent does not support skills.
- The user does not want to install a skill.
- The environment is temporary and only needs a one-off result.

Create a working directory named `portrait-wordcloud-output`.

Download required resources into a local `portrait-wordcloud-runtime` folder:

```bash
mkdir -p portrait-wordcloud-runtime/references portrait-wordcloud-runtime/scripts portrait-wordcloud-runtime/assets/fonts
curl -fsSL <BASE_URL>/portrait-wordcloud/references/keyword-extraction-prompt.md -o portrait-wordcloud-runtime/references/keyword-extraction-prompt.md
curl -fsSL <BASE_URL>/portrait-wordcloud/references/nobel-portrait-prompt.md -o portrait-wordcloud-runtime/references/nobel-portrait-prompt.md
curl -fsSL <BASE_URL>/portrait-wordcloud/scripts/check_environment.py -o portrait-wordcloud-runtime/scripts/check_environment.py
curl -fsSL <BASE_URL>/portrait-wordcloud/scripts/run_portrait_wordcloud.py -o portrait-wordcloud-runtime/scripts/run_portrait_wordcloud.py
curl -fsSL <BASE_URL>/portrait-wordcloud/assets/fonts/SourceHanSerifSC-Regular.otf -o portrait-wordcloud-runtime/assets/fonts/SourceHanSerifSC-Regular.otf
chmod +x portrait-wordcloud-runtime/scripts/check_environment.py portrait-wordcloud-runtime/scripts/run_portrait_wordcloud.py
```

If the agent cannot run shell commands, read the remote resources and proceed manually.

## Guided Workflow

Run this as a step-by-step wizard.

### 1. Check Image Generation Capability

Before asking the user to upload a real portrait photo, determine the current agent's image generation/editing capability:

- If the capability is provided by OpenAI and supports the `image2` model, use `image2` later to generate the Nobel-style portrait inside the agent.
- If there is no image generation/editing capability, or if the available capability is from another provider, tell the user this workflow recommends OpenAI `image2` for the Nobel-style portrait. Show the exact prompt from `references/nobel-portrait-prompt.md`, ask the user to generate the Nobel-style portrait externally with `image2` if possible, then upload that generated style image back to the agent. Do not ask for the original real portrait photo in this path unless the user still needs help preparing the external generation.

Suggested message when OpenAI `image2` is available:

```text
我这边可以直接使用 OpenAI image2 来生成诺奖风格肖像。接下来你只需要先上传一张至少半身、脸部清晰的真人照片。照片越清楚，后面的人物线稿和肩部轮廓会越稳。
```

Suggested message when OpenAI `image2` is not available:

```text
我这边暂时不能直接调用 OpenAI image2。为了让最终词云效果更稳定，我建议先用 image2 把真人照片生成一张诺奖风格肖像，再把生成后的风格图发给我。

没关系，我会把人物图提示词给你。你用支持 image2 的工具生成好之后，把那张生成图上传回来，我就可以继续帮你提取论文关键词并合成词云。
```

### 2. Ask For Inputs

Ask for the next missing input only:

1. If OpenAI `image2` is available, a clear real portrait photo that shows at least the upper half of the body.
2. If OpenAI `image2` is not available, an externally generated and approved Nobel-style portrait image.
3. Paper titles, abstracts, body text, or a paper file.

Use when OpenAI `image2` is available:

```text
请先上传一张至少半身、脸部清晰的真人照片。最好能看到头部、肩膀和上半身轮廓。上传后，我会继续让你提供论文标题、摘要、正文或论文文件。
```

Use when OpenAI `image2` is not available:

```text
请先上传一张已经用 OpenAI image2 生成好的诺奖风格肖像图。上传后，我会继续让你提供论文标题、摘要、正文或论文文件。
```

### 3. Extract Keywords

Read `references/keyword-extraction-prompt.md`, insert the user's paper text between the `<<<` and `>>>` markers, and produce a flat JSON dictionary.

Save:

- Candidate: `portrait-wordcloud-output/keywords.candidate.json`
- Approved: `portrait-wordcloud-output/keywords.json`

Stop for confirmation after the candidate:

```text
我已经从论文内容里提取出关键词候选集，共 N 个。下面是权重最高的 20 个。

你先帮我看一眼：这组关键词可以用于词云吗？如果有不合适的词，你可以直接告诉我要删除、增加，或者把某些词调大/调小。
```

Do not continue until the user approves or edits the keywords.

### 4. Generate Or Obtain Nobel-Style Portrait

Read `references/nobel-portrait-prompt.md`.

If OpenAI image generation/editing with the `image2` model is available, use the user's photo and the prompt to generate a Nobel Prize style portrait with `image2`.

If OpenAI `image2` is not available, or if only another provider's image generation/editing is available, tell the user:

```text
我这边暂时不能直接调用 OpenAI image2。这个流程推荐用 image2 先生成诺奖风格肖像，这样最终词云会更接近预期效果。

下面是人物图提示词。请你用 image2 生成风格图后，把生成结果上传给我；我会继续处理关键词和最终合成。
```

Then show the exact Nobel portrait prompt.

Save:

- Candidate: `portrait-wordcloud-output/nobel_portrait.candidate.png`
- Approved: `portrait-wordcloud-output/nobel_portrait.png`

Stop for confirmation after the candidate:

```text
这是生成的人物图。你看这个版本可以进入词云合成吗？如果你觉得人物不像、线条太重、金色太多，或者构图不合适，我们可以先调整，不急着进入最后一步。
```

Do not continue until the user approves the portrait image.

### 5. Check Environment

Run:

```bash
python3 portrait-wordcloud-runtime/scripts/check_environment.py
```

If packages are missing, the script prints the exact install command. Ask whether to install them. Do not install packages without user approval.

Suggested user-facing message when packages are missing:

```text
合成词云需要几个本地 Python 依赖。当前环境还缺少下面这些包。我可以在你确认后帮你安装；如果你不想安装，我们也可以换到已有这些依赖的环境里运行。
```

After user approval, run:

```bash
python3 portrait-wordcloud-runtime/scripts/check_environment.py --install
```

Use `--user` to install into the current user's site-packages, or `--upgrade` when a fresh package version is needed.

### 6. Compose Final Image

Run:

```bash
python3 portrait-wordcloud-runtime/scripts/run_portrait_wordcloud.py \
  --portrait portrait-wordcloud-output/nobel_portrait.png \
  --keywords-json portrait-wordcloud-output/keywords.json \
  --out-dir portrait-wordcloud-output
```

Expected output files:

- `portrait-wordcloud-output/portrait_mask.png`
- `portrait-wordcloud-output/portrait_mask_preview.png`
- `portrait-wordcloud-output/wordcloud_layer.png`
- `portrait-wordcloud-output/wordcloud_preview.png`

Show `wordcloud_preview.png` to the user when possible.

Suggested completion message:

```text
做好了，这是最终的人像学术词云图。人物区域我已经做了保护，关键词主要分布在背景里。

最终图片：portrait-wordcloud-output/wordcloud_preview.png
关键词文件：portrait-wordcloud-output/keywords.json
人物风格图：portrait-wordcloud-output/nobel_portrait.png
```

## Recovery Rules

Resume from the latest approved file:

- `keywords.json` means keyword extraction is complete.
- `nobel_portrait.png` means portrait generation is complete.
- `wordcloud_preview.png` means final composition exists.

Never overwrite approved files silently. Write candidates first and replace approved files only after confirmation.

## Quality Tuning

If words cover the face, hair, glasses, or shoulders, rerun composition with:

```bash
--portrait-padding 26
```

If background words are too blurry:

```bash
--far-blur 0.35 --far-blur-scale 0.25
```

If background words are too faint:

```bash
--far-alpha 76
```

If layout balance is poor, change:

```bash
--random-state 41
```

## Completion Message

When done, return:

- Final image path.
- Keyword JSON path.
- Nobel portrait path.
- Any tuning options used.

Use a concise final message in the user's language.
