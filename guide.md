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
2. 准备人物图：如果我能用 image2，你上传至少半身、脸部清晰的真人照片；如果不能，我会给你两个选择：推荐你外部用 image2 生成风格图后传回来，或者走一个备用方案先试。
3. 你提供论文标题、摘要、正文或论文文件，我提取关键词，并先给你确认。
4. 你确认人物图和关键词后，我会让你确认底部文案，再合成 1:1 正方形词云图。

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
- If OpenAI `image2` is not exposed, tell the user this workflow recommends `image2` for the Nobel-style portrait and offer two choices before asking for any image:
  1. Recommended: the agent shows the Nobel portrait prompt, the user generates the Nobel-style portrait externally with OpenAI `image2`, then uploads that generated style image back to the agent.
  2. Backup: if another image tool is available, the user may choose to let the agent try that tool once; if no image tool is available, the user may upload an already-generated Nobel-style portrait from another source. Explain that this may be less faithful than `image2` and the user will still confirm the portrait before composition.

Suggested message when OpenAI `image2` is available:

```text
我这边可以直接使用 OpenAI image2 来生成诺奖风格肖像。接下来你只需要先上传一张至少半身、脸部清晰的真人照片。照片越清楚，后面的人物线稿和肩部轮廓会越稳。
```

Suggested message when OpenAI `image2` is not available:

```text
我这边暂时没有暴露出 OpenAI image2。为了让最终词云效果更稳定，我更推荐用 image2 先把真人照片生成一张诺奖风格肖像。

你可以选一种方式继续：
1. 推荐：我把人物图提示词给你，你用 OpenAI image2 生成好诺奖风格肖像后，把生成图上传回来。
2. 备用：如果你愿意，我也可以用当前可用的图像工具先试一次；如果当前没有图像工具，你也可以上传一张已经生成好的诺奖风格肖像图。这个方案效果可能不如 image2，我们会先确认人物图，再进入词云合成。

你想选哪一种？
```

### 2. Ask For Inputs

Ask for the next missing input only:

1. If OpenAI `image2` is available, a clear real portrait photo that shows at least the upper half of the body.
2. If OpenAI `image2` is not available, first ask the user to choose the recommended external `image2` path or the backup path. Then ask for either the externally generated Nobel-style portrait image, or the image needed for the user-approved backup tool attempt.
3. Paper titles, abstracts, body text, or a paper file.

Use when OpenAI `image2` is available:

```text
请先上传一张至少半身、脸部清晰的真人照片。最好能看到头部、肩膀和上半身轮廓。上传后，我会继续让你提供论文标题、摘要、正文或论文文件。
```

Use when OpenAI `image2` is not available:

```text
如果你选择推荐方案，请先上传一张已经用 OpenAI image2 生成好的诺奖风格肖像图。上传后，我会继续让你提供论文标题、摘要、正文或论文文件。
```

Use after the user chooses the backup path:

```text
好的，我们走备用方案。请上传你希望尝试处理的人像图，或者直接上传一张已经生成好的诺奖风格肖像图。我会先让你确认人物图效果，确认后才会继续合成词云。
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

If OpenAI `image2` is not available, or if only another provider's image generation/editing is available, give the user the same two choices before generating or asking for an upload:

```text
我这边暂时没有暴露出 OpenAI image2。这个流程推荐用 image2 先生成诺奖风格肖像，这样最终词云会更接近预期效果。

你有两个选择：
1. 推荐：我把人物图提示词给你，你用 OpenAI image2 生成风格图后，把生成结果上传给我。
2. 备用：如果你愿意，我可以用当前可用的图像工具先试一次；如果当前没有图像工具，你也可以上传一张已经生成好的诺奖风格肖像图。

我们会先确认人物图效果，再继续处理关键词和最终合成。
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

### 6. Ask For Footer Caption

Before composing the final image, ask whether the user wants to customize the bottom caption. The user only needs to provide Chinese. Translate it into natural English yourself and pass both strings to the composition script.

Default Chinese caption:

```text
我们跃入人海，各有风雨灿烂
```

Default English translation:

```text
We part like rivers — each to its own storm and dawn.
```

Suggested user-facing message:

```text
最后我会在词云图底部拼接一个深酒红色文案区，把整张图补成 1:1 正方形。底部中英文会居中排版：中文优先用偏粗的苹方，没有苹方就用黑体兜底；英文使用常规字重，不加粗。整体在文案区里垂直居中但稍微靠下。默认文案是：

我们跃入人海，各有风雨灿烂

如果你想换一句，只需要给我中文就好，我会帮你翻译成英文并一起排到图片底部。
```

### 7. Compose Final Image

Run:

```bash
python3 portrait-wordcloud-runtime/scripts/run_portrait_wordcloud.py \
  --portrait portrait-wordcloud-output/nobel_portrait.png \
  --keywords-json portrait-wordcloud-output/keywords.json \
  --out-dir portrait-wordcloud-output \
  --caption-cn "<用户确认的中文文案>" \
  --caption-en "<Agent 翻译后的英文文案>"
```

Expected output files:

- `portrait-wordcloud-output/portrait_mask.png`
- `portrait-wordcloud-output/portrait_mask_preview.png`
- `portrait-wordcloud-output/wordcloud_layer.png`
- `portrait-wordcloud-output/wordcloud_preview.png`
- `portrait-wordcloud-output/wordcloud_square.png`

Show `wordcloud_square.png` to the user when possible. `wordcloud_preview.png` is the original horizontal image without the footer.

Suggested completion message:

```text
做好了，这是最终的 1:1 人像学术词云图。人物区域我已经做了保护，底部也加上了中英文文案。

最终图片：portrait-wordcloud-output/wordcloud_square.png
横版词云：portrait-wordcloud-output/wordcloud_preview.png
关键词文件：portrait-wordcloud-output/keywords.json
人物风格图：portrait-wordcloud-output/nobel_portrait.png
```

## Recovery Rules

Resume from the latest approved file:

- `keywords.json` means keyword extraction is complete.
- `nobel_portrait.png` means portrait generation is complete.
- `wordcloud_square.png` means final 1:1 composition exists.
- `wordcloud_preview.png` means the horizontal wordcloud composition exists but the square footer may still need to be checked.

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
