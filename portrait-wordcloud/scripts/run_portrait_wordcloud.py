#!/usr/bin/env python3
from __future__ import annotations

import argparse
import colorsys
import json
import os
import random
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "portrait-wordcloud-matplotlib"))

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from scipy import ndimage
from wordcloud import WordCloud


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_FONT_PATHS = [
    SKILL_DIR / "assets/fonts/SourceHanSerifSC-Regular.otf",
    SKILL_DIR / "assets/fonts/SourceHanSerifSC-Heavy.otf",
    Path("fonts/SourceHanSerifSC-Regular.otf"),
    Path("fonts/SourceHanSerifSC-Heavy.otf"),
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
]
DEFAULT_LATIN_FONT_PATHS = [
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path("/System/Library/Fonts/Supplemental/Avenir Next.ttc"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
DEFAULT_CAPTION_CN = "我们跃入人海，各有风雨灿烂"
DEFAULT_CAPTION_EN = "We part like rivers — each to its own storm and dawn."
DEFAULT_CAPTION_FONT_PATHS = [
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Supplemental/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Supplemental/Heiti.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    SKILL_DIR / "assets/fonts/SourceHanSerifSC-Heavy.otf",
    SKILL_DIR / "assets/fonts/SourceHanSerifSC-Regular.otf",
]


def disk(radius: int) -> np.ndarray:
    y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return (x * x + y * y) <= radius * radius


def largest_components(mask: np.ndarray, min_area: int = 700) -> np.ndarray:
    labels, count = ndimage.label(mask)
    if count == 0:
        return mask

    areas = np.bincount(labels.ravel())
    keep = np.zeros(count + 1, dtype=bool)
    height, width = mask.shape
    center_x = width / 2

    for idx in range(1, count + 1):
        ys, xs = np.where(labels == idx)
        if xs.size == 0:
            continue
        near_center = abs(xs.mean() - center_x) < width * 0.32
        if areas[idx] >= min_area and near_center:
            keep[idx] = True

    return keep[labels]


def estimate_ink(rgb: np.ndarray) -> np.ndarray:
    rgbf = rgb.astype(np.float32)
    luminance = rgbf @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    border = np.concatenate(
        [
            rgbf[:30].reshape(-1, 3),
            rgbf[-30:].reshape(-1, 3),
            rgbf[:, :30].reshape(-1, 3),
            rgbf[:, -30:].reshape(-1, 3),
        ],
        axis=0,
    )
    paper = np.median(border, axis=0)
    color_distance = np.linalg.norm(rgbf - paper, axis=2)
    gold = (rgbf[:, :, 0] > rgbf[:, :, 2] + 18) & (rgbf[:, :, 1] > rgbf[:, :, 2] + 10)
    dark = luminance < 215
    saturated = color_distance > 34
    return dark | (gold & saturated)


def build_mask(image: Image.Image, portrait_padding: int) -> Image.Image:
    rgb = np.array(image.convert("RGB"))
    height, width = rgb.shape[:2]

    ink = estimate_ink(rgb)
    ink = ndimage.binary_opening(ink, structure=disk(1))
    ink = ndimage.binary_dilation(ink, structure=disk(3), iterations=1)
    ink = largest_components(ink)

    ys, xs = np.where(ink)
    if xs.size == 0:
        raise RuntimeError("No portrait ink detected.")

    row_counts = np.bincount(ys, minlength=height)
    valid_rows = np.where(row_counts >= 4)[0]
    left = np.full(height, np.nan)
    right = np.full(height, np.nan)
    for y in valid_rows:
        row_x = xs[ys == y]
        left[y] = np.percentile(row_x, 2)
        right[y] = np.percentile(row_x, 98)

    y0 = max(0, int(valid_rows.min()) - 10)
    y1 = min(height - 1, int(valid_rows.max()) + 14)
    rows = np.arange(y0, y1 + 1)
    known = rows[~np.isnan(left[rows]) & ~np.isnan(right[rows])]
    left_i = np.interp(rows, known, left[known])
    right_i = np.interp(rows, known, right[known])

    left_i = ndimage.median_filter(left_i, size=31)
    right_i = ndimage.median_filter(right_i, size=31)
    left_i = ndimage.gaussian_filter1d(left_i, sigma=7)
    right_i = ndimage.gaussian_filter1d(right_i, sigma=7)

    envelope = np.zeros((height, width), dtype=bool)
    margin = 24
    for offset, y in enumerate(rows):
        lx = max(0, int(left_i[offset]) - margin)
        rx = min(width - 1, int(right_i[offset]) + margin)
        if rx - lx >= 24:
            envelope[y, lx : rx + 1] = True

    line_halo = ndimage.binary_dilation(ink, structure=disk(16), iterations=1)
    portrait = envelope | line_halo
    portrait = ndimage.binary_closing(portrait, structure=disk(8), iterations=1)
    portrait = ndimage.binary_fill_holes(portrait)
    portrait = ndimage.binary_opening(portrait, structure=disk(2), iterations=1)

    bottom_start = int(valid_rows.max() - height * 0.2)
    bottom_rows = np.arange(max(0, bottom_start), min(height, int(valid_rows.max() + 95)))
    if bottom_rows.size:
        bottom_band = np.zeros((height, width), dtype=bool)
        for y in bottom_rows:
            active_x = np.where(portrait[y])[0]
            if active_x.size:
                progress = (y - bottom_rows[0]) / max(1, bottom_rows[-1] - bottom_rows[0])
                loosen = int(24 + 68 * progress)
                lx = max(0, int(active_x.min()) - loosen)
                rx = min(width - 1, int(active_x.max()) + loosen)
                bottom_band[y, lx : rx + 1] = True
        portrait |= ndimage.binary_dilation(bottom_band, structure=disk(24), iterations=1)

    portrait = ndimage.binary_dilation(portrait, structure=disk(portrait_padding), iterations=1)
    mask = Image.fromarray((portrait.astype(np.uint8) * 255), "L")
    return mask.filter(ImageFilter.GaussianBlur(radius=1.2))


def save_mask_preview(image: Image.Image, mask: Image.Image, out_dir: Path) -> None:
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (220, 24, 50, 0))
    overlay.putalpha(mask.point(lambda p: int(p * 0.38)))
    preview = Image.alpha_composite(base, overlay)
    inverse = Image.eval(mask, lambda p: 255 - p)

    mask.save(out_dir / "portrait_mask.png")
    inverse.save(out_dir / "wordcloud_background_mask.png")
    preview.save(out_dir / "portrait_mask_preview.png")


def pick_font(font_path: str | None = None) -> str:
    if font_path:
        path = Path(font_path).expanduser()
        if path.exists():
            return str(path)
        raise FileNotFoundError(f"Font does not exist: {path}")

    for path in DEFAULT_FONT_PATHS:
        if path.exists():
            return str(path)
    raise FileNotFoundError("No usable CJK font found.")


def pick_latin_font(font_path: str | None = None) -> str:
    if font_path:
        path = Path(font_path).expanduser()
        if path.exists():
            return str(path)
        raise FileNotFoundError(f"Font does not exist: {path}")

    for path in DEFAULT_LATIN_FONT_PATHS:
        if path.exists():
            return str(path)
    return pick_font(None)


def pick_caption_font(font_path: str | None = None) -> str:
    if font_path:
        path = Path(font_path).expanduser()
        if path.exists():
            return str(path)
        raise FileNotFoundError(f"Font does not exist: {path}")

    for path in DEFAULT_CAPTION_FONT_PATHS:
        if path.exists():
            return str(path)
    return pick_font(None)


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def adjust_color(rgb: tuple[int, int, int], lightness_delta: float, saturation_scale: float) -> tuple[int, int, int]:
    r, g, b = [channel / 255 for channel in rgb]
    h, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    lightness = min(1.0, max(0.0, lightness + lightness_delta))
    saturation = min(1.0, max(0.0, saturation * saturation_scale))
    rr, gg, bb = colorsys.hls_to_rgb(h, lightness, saturation)
    return int(rr * 255), int(gg * 255), int(bb * 255)


def load_keywords(path: Path) -> dict[str, int]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        raise ValueError("Keyword JSON must be a non-empty flat dictionary.")

    cleaned: dict[str, int] = {}
    for word, weight in data.items():
        if not isinstance(word, str) or not word.strip():
            continue
        if not isinstance(weight, (int, float)):
            raise ValueError(f"Weight for {word!r} must be numeric.")
        cleaned[word.strip()] = int(weight)
    if not cleaned:
        raise ValueError("Keyword JSON contains no valid terms.")
    return dict(sorted(cleaned.items(), key=lambda item: item[1], reverse=True))


def layout_frequencies(keywords: dict[str, int]) -> dict[str, float]:
    weights = np.array(list(keywords.values()), dtype=np.float32)
    low, high = weights.min(), weights.max()
    if high == low:
        return {word: 1.0 for word in keywords}
    return {
        word: 0.82 + 0.18 * ((weight - low) / (high - low))
        for word, weight in keywords.items()
    }


def safe_wordcloud_mask(mask: Image.Image, safe_edge: int) -> np.ndarray:
    expanded_mask = mask.convert("L").filter(ImageFilter.MaxFilter(21))
    wc_mask = np.array(expanded_mask)
    wc_mask[:safe_edge, :] = 255
    wc_mask[-safe_edge:, :] = 255
    wc_mask[:, :safe_edge] = 255
    wc_mask[:, -safe_edge:] = 255
    return wc_mask


def build_dense_layout(
    image: Image.Image,
    mask: Image.Image,
    keywords: dict[str, int],
    args: argparse.Namespace,
) -> WordCloud:
    width, height = image.size
    return WordCloud(
        width=width,
        height=height,
        background_color=None,
        mode="RGBA",
        mask=safe_wordcloud_mask(mask, args.safe_edge),
        font_path=pick_font(args.font),
        max_words=args.max_words,
        min_font_size=args.min_font_size,
        max_font_size=args.max_font_size,
        prefer_horizontal=1.0,
        relative_scaling=args.relative_scaling,
        repeat=True,
        collocations=False,
        contour_width=0,
        color_func=lambda *args_, **kwargs: args.word_color,
        random_state=args.random_state,
        margin=args.margin,
        font_step=1,
    ).generate_from_frequencies(layout_frequencies(keywords))


def text_layer(
    size: tuple[int, int],
    word: str,
    font_size: int,
    position: tuple[int, int],
    color: tuple[int, int, int, int],
    font_path: str | None,
) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(pick_font(font_path), font_size)
    row, col = position
    draw.text((col, row), word, fill=color, font=font)
    return layer


def render_depth_wordcloud(
    image: Image.Image,
    mask: Image.Image,
    layout: WordCloud,
    keywords: dict[str, int],
    args: argparse.Namespace,
) -> Image.Image:
    size = image.size
    base_rgb = hex_to_rgb(args.word_color)
    weights = np.array(list(keywords.values()), dtype=np.float32)
    low, high = weights.min(), weights.max()
    denominator = max(1.0, float(high - low))
    rng = random.Random(args.random_state + 20)

    far = Image.new("RGBA", size, (0, 0, 0, 0))
    middle = Image.new("RGBA", size, (0, 0, 0, 0))
    front = Image.new("RGBA", size, (0, 0, 0, 0))

    for (word_data, font_size, position, orientation, _color) in sorted(layout.layout_, key=lambda item: item[1]):
        word, _layout_weight = word_data
        original_weight = keywords[word]
        importance = float((original_weight - low) / denominator)
        jitter = rng.uniform(-0.05, 0.05)

        if importance + jitter < 0.32 or font_size <= 28:
            rgb = adjust_color(base_rgb, lightness_delta=0.12, saturation_scale=0.55)
            alpha = int(args.far_alpha + 34 * importance)
            layer = text_layer(size, word, font_size, position, (*rgb, alpha), args.font)
            blur_radius = args.far_blur + args.far_blur_scale * (1 - importance)
            if blur_radius > 0:
                layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            far = Image.alpha_composite(far, layer)
        elif importance + jitter < 0.68 or font_size <= 58:
            rgb = adjust_color(base_rgb, lightness_delta=0.05, saturation_scale=0.8)
            alpha = int(126 + 42 * importance)
            layer = text_layer(size, word, font_size, position, (*rgb, alpha), args.font)
            middle = Image.alpha_composite(middle, layer)
        else:
            rgb = adjust_color(base_rgb, lightness_delta=-0.05, saturation_scale=1.12)
            alpha = int(188 + 52 * importance)
            layer = text_layer(size, word, font_size, position, (*rgb, alpha), args.font)
            front = Image.alpha_composite(front, layer)

    cloud = Image.alpha_composite(far, middle)
    cloud = Image.alpha_composite(cloud, front)

    allowed = Image.eval(mask.convert("L").filter(ImageFilter.MaxFilter(19)), lambda p: 255 - p)
    allowed = allowed.filter(ImageFilter.GaussianBlur(0.6))
    cloud.putalpha(Image.composite(cloud.getchannel("A"), Image.new("L", size, 0), allowed))
    return cloud


def soften_background(image: Image.Image, mask: Image.Image) -> Image.Image:
    base = image.convert("RGBA")
    paper = Image.new("RGBA", base.size, (248, 244, 235, 255))
    soft = Image.blend(base, paper, 0.22)
    inverse = Image.eval(mask.convert("L"), lambda p: 255 - p).filter(ImageFilter.GaussianBlur(2))
    return Image.composite(soft, base, inverse)


def restore_portrait(original: Image.Image, composed: Image.Image, mask: Image.Image) -> Image.Image:
    portrait_alpha = mask.convert("L").filter(ImageFilter.GaussianBlur(0.6))
    portrait = original.convert("RGBA")
    return Image.composite(portrait, composed.convert("RGBA"), portrait_alpha)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text_by_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if not text:
        return []

    if " " in text:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if text_width(draw, candidate, font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    lines = []
    current = ""
    for char in text:
        candidate = current + char
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def fit_font_size(
    font_path: str,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    probe = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    for size in range(start_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text_by_width(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines

    font = ImageFont.truetype(font_path, min_size)
    return font, wrap_text_by_width(draw, text, font, max_width)[:max_lines]


def line_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    sample = text or "Ag"
    bbox = draw.textbbox((0, 0), sample, font=font)
    return bbox[3] - bbox[1]


def load_caption_font(font_path: str, size: int, face_index: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(font_path, size, index=face_index)
    except TypeError:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.truetype(font_path, size)


def fit_caption_font_size(
    font_path: str,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int,
    max_lines: int,
    face_index: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    probe = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    for size in range(start_size, min_size - 1, -2):
        font = load_caption_font(font_path, size, face_index)
        lines = wrap_text_by_width(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines

    font = load_caption_font(font_path, min_size, face_index)
    return font, wrap_text_by_width(draw, text, font, max_width)[:max_lines]


def append_square_caption(image: Image.Image, args: argparse.Namespace) -> Image.Image:
    width, height = image.size
    if args.no_square_caption or height >= width:
        return image.convert("RGBA")

    footer_height = width - height
    output = Image.new("RGBA", (width, width), hex_to_rgb(args.caption_bg) + (255,))
    output.alpha_composite(image.convert("RGBA"), (0, 0))

    draw = ImageDraw.Draw(output)
    max_text_width = int(width * 0.92)
    cn_font_path = pick_caption_font(args.caption_font)
    en_font_path = pick_latin_font(args.caption_latin_font)
    cn_start = max(34, int(width * args.caption_cn_scale))
    en_start = max(20, int(width * args.caption_en_scale))

    cn_font, cn_lines = fit_caption_font_size(
        cn_font_path,
        args.caption_cn,
        max_text_width,
        cn_start,
        max(20, int(width * 0.03)),
        args.caption_cn_max_lines,
        args.caption_font_index,
    )
    en_font, en_lines = fit_caption_font_size(
        en_font_path,
        args.caption_en,
        max_text_width,
        en_start,
        max(14, int(width * 0.018)),
        args.caption_en_max_lines,
        args.caption_latin_font_index,
    )

    cn_gap = int(footer_height * 0.08)
    en_gap = int(footer_height * 0.12)
    cn_heights = [line_height(draw, line, cn_font) for line in cn_lines]
    en_heights = [line_height(draw, line, en_font) for line in en_lines]
    total_text_height = sum(cn_heights) + max(0, len(cn_lines) - 1) * cn_gap
    if en_lines:
        total_text_height += en_gap + sum(en_heights) + max(0, len(en_lines) - 1) * int(en_gap * 0.55)

    y = height + max(0, (footer_height - total_text_height) // 2) + int(footer_height * args.caption_vertical_bias)
    y = min(y, height + max(0, footer_height - total_text_height - int(footer_height * 0.08)))
    primary = hex_to_rgb(args.caption_primary_color) + (255,)
    secondary = hex_to_rgb(args.caption_secondary_color) + (255,)

    for idx, line in enumerate(cn_lines):
        x = (width - text_width(draw, line, cn_font)) // 2
        draw.text((x, y), line, fill=primary, font=cn_font)
        y += cn_heights[idx] + cn_gap

    if en_lines:
        y += max(0, en_gap - cn_gap)
        en_line_gap = int(en_gap * 0.55)
        for idx, line in enumerate(en_lines):
            x = (width - text_width(draw, line, en_font)) // 2
            draw.text((x, y), line, fill=secondary, font=en_font)
            y += en_heights[idx] + en_line_gap

    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose a Nobel-style portrait wordcloud image.")
    parser.add_argument("--portrait", required=True, type=Path, help="Approved Nobel-style portrait image.")
    parser.add_argument("--keywords-json", required=True, type=Path, help="Approved flat keyword-weight JSON.")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"), help="Output directory.")
    parser.add_argument("--font", default=None, help="Optional font path.")
    parser.add_argument("--word-color", default="#A69A6C")
    parser.add_argument("--random-state", type=int, default=32)
    parser.add_argument("--max-words", type=int, default=720)
    parser.add_argument("--min-font-size", type=int, default=18)
    parser.add_argument("--max-font-size", type=int, default=104)
    parser.add_argument("--relative-scaling", type=float, default=0.32)
    parser.add_argument("--margin", type=int, default=1)
    parser.add_argument("--safe-edge", type=int, default=58)
    parser.add_argument("--portrait-padding", type=int, default=18)
    parser.add_argument("--far-blur", type=float, default=0.65)
    parser.add_argument("--far-blur-scale", type=float, default=0.45)
    parser.add_argument("--far-alpha", type=int, default=62)
    parser.add_argument("--contrast", type=float, default=1.08)
    parser.add_argument("--caption-cn", default=DEFAULT_CAPTION_CN, help="Chinese caption for the square footer.")
    parser.add_argument("--caption-en", default=DEFAULT_CAPTION_EN, help="English caption for the square footer.")
    parser.add_argument("--caption-bg", default="#551D21", help="Footer background color.")
    parser.add_argument("--caption-primary-color", default="#F1D3A1", help="Chinese caption color.")
    parser.add_argument("--caption-secondary-color", default="#E4CDC8", help="English caption color.")
    parser.add_argument("--caption-font", default=None, help="Optional CJK font path for the square footer.")
    parser.add_argument("--caption-latin-font", default=None, help="Optional Latin font path for the square footer.")
    parser.add_argument("--caption-font-index", type=int, default=8, help="TTC face index for the CJK caption font.")
    parser.add_argument("--caption-latin-font-index", type=int, default=0, help="TTC face index for the Latin caption font.")
    parser.add_argument("--caption-cn-scale", type=float, default=0.06, help="Chinese caption font size relative to image width.")
    parser.add_argument("--caption-en-scale", type=float, default=0.024, help="English caption font size relative to image width.")
    parser.add_argument("--caption-cn-max-lines", type=int, default=2)
    parser.add_argument("--caption-en-max-lines", type=int, default=2)
    parser.add_argument("--caption-vertical-bias", type=float, default=0.02, help="Move footer text downward relative to vertical center.")
    parser.add_argument("--no-square-caption", action="store_true", help="Skip the square footer output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(args.out_dir / ".matplotlib"))

    image = Image.open(args.portrait).convert("RGBA")
    keywords = load_keywords(args.keywords_json)

    mask = build_mask(image, portrait_padding=args.portrait_padding)
    save_mask_preview(image, mask, args.out_dir)

    layout = build_dense_layout(image, mask, keywords, args)
    cloud = render_depth_wordcloud(image, mask, layout, keywords, args)
    cloud = ImageEnhance.Contrast(cloud).enhance(args.contrast)

    background = soften_background(image, mask)
    composed = Image.alpha_composite(background, cloud)
    result = restore_portrait(image, composed, mask)

    cloud.save(args.out_dir / "wordcloud_layer.png")
    result.save(args.out_dir / "wordcloud_preview.png")
    square = append_square_caption(result, args)
    square.save(args.out_dir / "wordcloud_square.png")

    print(f"saved: {args.out_dir / 'portrait_mask.png'}")
    print(f"saved: {args.out_dir / 'wordcloud_background_mask.png'}")
    print(f"saved: {args.out_dir / 'portrait_mask_preview.png'}")
    print(f"saved: {args.out_dir / 'wordcloud_layer.png'}")
    print(f"saved: {args.out_dir / 'wordcloud_preview.png'}")
    print(f"saved: {args.out_dir / 'wordcloud_square.png'}")


if __name__ == "__main__":
    main()
