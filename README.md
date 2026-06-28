# Portrait Wordcloud Skill

Create Nobel Prize style academic portrait wordclouds from a clear, at-least-half-body real portrait photo and academic paper text.

This repository contains a Codex skill that guides the user through:

- collecting a clear real portrait photo that shows at least the upper half of the body
- extracting academic keywords from paper text
- generating or obtaining a Nobel-style portrait
- composing the final protected portrait wordcloud image
- appending a bilingual footer caption to produce a 1:1 square image

## Use In Codex

Ask Codex to install the skill from this repository:

```text
Please install the portrait-wordcloud skill from:
https://github.com/JackyCodesign/portrait-wordcloud-skill
```

Then restart Codex or open a new thread and say:

```text
Use $portrait-wordcloud
```

## Direct Run

If skill installation is unavailable, use the bootstrap guide:

```text
https://raw.githubusercontent.com/JackyCodesign/portrait-wordcloud-skill/main/guide.md
```

## Requirements

The composition script requires:

- Pillow
- numpy
- scipy
- wordcloud

Check or install them with:

```bash
python3 portrait-wordcloud/scripts/check_environment.py
python3 portrait-wordcloud/scripts/check_environment.py --install
```

The final output is `wordcloud_square.png`. By default, the footer caption is:

```text
我们跃入人海，各有风雨灿烂
```

Default English:

```text
We part like rivers — each to its own storm and dawn.
```
