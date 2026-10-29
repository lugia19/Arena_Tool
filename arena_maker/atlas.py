"""Scaleform texture atlases: .layout files (in the SB layout binder) + their DDS sheets (in the TPF).

Stock conventions (menu/hi/01_common): BC7_UNORM, no mipmaps, cells on a grid with a 4 px gap
(e.g. 128x128 thumbnails at a 132 px pitch), so every cell starts on a multiple of 4 and no BC7 4x4 block
mixes two cells. Subtextures are named "<name>.png"; GFX files refer to them by "<name>".
"""
import math
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from xml.sax.saxutils import quoteattr

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

from .witchy import file_version

TEXCONV_VERSION = "2024.6.5.1"
DDS_FORMAT = "BC7_UNORM"
TPF_FORMAT_BC7 = "102"  # TPF texture format code the menu textures use for BC7
CELL_GAP = 4

# Stock layouts point at the artists' source files; the game only uses the atlas name from this path.
IMAGE_PATH_TEMPLATE = r"W:\FNR\data\Menu\ScaleForm\Tif\01_Common\{group}\Hi\exp\{name}.png"


# region Layout files
@dataclass
class SubTexture:
    name: str  # e.g. "Decal_tmb_00009900.png"
    x: int
    y: int
    width: int
    height: int
    extra: Dict[str, str] = field(default_factory=dict)  # e.g. half="0" on decal thumbnails


@dataclass
class Layout:
    image_path: str
    width: Optional[int]  # A couple of stock layouts (SB_NamePlate, SB_PieceCategory) leave the size out.
    height: Optional[int]
    subtextures: List[SubTexture]

    @classmethod
    def parse(cls, text: str) -> "Layout":
        atlas = re.search(r"<TextureAtlas\s([^>]*)>", text)
        if not atlas:
            raise ValueError("Not a TextureAtlas layout")
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', atlas.group(1)))
        subtextures = []
        for match in re.finditer(r"<SubTexture\s([^>]*?)/?>", text):
            sub = dict(re.findall(r'(\w+)="([^"]*)"', match.group(1)))
            subtextures.append(SubTexture(sub.pop("name"), int(sub.pop("x")), int(sub.pop("y")),
                                          int(sub.pop("width")), int(sub.pop("height")), sub))
        width, height = attrs.get("width"), attrs.get("height")
        return cls(attrs["imagePath"], int(width) if width else None, int(height) if height else None, subtextures)

    def to_text(self) -> str:
        size = f' width="{self.width}" height="{self.height}"' if self.width is not None else ""
        lines = [f'<TextureAtlas imagePath={quoteattr(self.image_path)}{size}>']
        for sub in self.subtextures:
            extra = "".join(f" {key}={quoteattr(value)}" for key, value in sub.extra.items())
            lines.append(f'\t<SubTexture name={quoteattr(sub.name)} x="{sub.x}" width="{sub.width}" '
                         f'y="{sub.y}" height="{sub.height}"{extra}/>')
        lines.append("</TextureAtlas>")
        return "\r\n".join(lines) + "\r\n"
# endregion


# region Packing
def _round_up(value: int, multiple: int = 4) -> int:
    return (value + multiple - 1) // multiple * multiple


def _check_sizes(images: Dict[str, Image.Image], width: int, height: int):
    for name, image in images.items():
        if image.size != (width, height):
            raise ValueError(f"{name} is {image.size[0]}x{image.size[1]}, expected {width}x{height}")


def build_atlas(group: str, name: str, images: Dict[str, Image.Image], cell_width: int, cell_height: int,
                extra: Optional[Dict[str, str]] = None) -> Tuple[Image.Image, Layout]:
    """A new, roughly square atlas. images: subtexture name (without .png) -> image of exactly cell size."""
    _check_sizes(images, cell_width, cell_height)
    count = max(len(images), 1)
    columns = math.ceil(math.sqrt(count * cell_height / cell_width))  # square in pixels, not in cells
    rows = math.ceil(count / columns)
    pitch_x, pitch_y = cell_width + CELL_GAP, cell_height + CELL_GAP
    width, height = _round_up(columns * pitch_x - CELL_GAP), _round_up(rows * pitch_y - CELL_GAP)
    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    layout = Layout(IMAGE_PATH_TEMPLATE.format(group=group, name=name), width, height, [])
    for index, (sub_name, image) in enumerate(images.items()):
        x, y = (index % columns) * pitch_x, (index // columns) * pitch_y
        sheet.paste(image.convert("RGBA"), (x, y))
        layout.subtextures.append(SubTexture(sub_name + ".png", x, y, cell_width, cell_height, dict(extra or {})))
    return sheet, layout


def add_to_atlas(sheet: Image.Image, layout: Layout, images: Dict[str, Image.Image], cell_width: int,
                 cell_height: int, extra: Optional[Dict[str, str]] = None) -> Tuple[Image.Image, Layout]:
    """Adds cell-sized images to an existing grid atlas: free grid cells first, then new rows at the bottom.
    Existing subtextures with the same name are replaced in place."""
    _check_sizes(images, cell_width, cell_height)
    if layout.width is None or layout.height is None:
        raise ValueError("Can only add to layouts that declare their atlas size")
    pitch_x, pitch_y = cell_width + CELL_GAP, cell_height + CELL_GAP
    columns = (layout.width + CELL_GAP) // pitch_x
    by_name = {sub.name: sub for sub in layout.subtextures}
    used = {(sub.x // pitch_x, sub.y // pitch_y) for sub in layout.subtextures}
    free = sorted(((cx, cy) for cx in range(columns) for cy in range((layout.height + CELL_GAP) // pitch_y)
                   if (cx, cy) not in used), key=lambda cell: (cell[1], cell[0]))

    placements = []
    next_row = (layout.height + CELL_GAP) // pitch_y
    for sub_name, image in images.items():
        existing = by_name.get(sub_name + ".png")
        if existing:
            placements.append((existing.x, existing.y, image))
            continue
        if not free:
            free = [(cx, next_row) for cx in range(columns)]
            next_row += 1
        cx, cy = free.pop(0)
        sub = SubTexture(sub_name + ".png", cx * pitch_x, cy * pitch_y, cell_width, cell_height, dict(extra or {}))
        layout.subtextures.append(sub)
        placements.append((sub.x, sub.y, image))

    new_height = max(layout.height, _round_up(max(y for _, y, _ in placements) + cell_height)) if placements else layout.height
    if new_height != layout.height:
        grown = Image.new("RGBA", (layout.width, new_height), (0, 0, 0, 0))
        grown.paste(sheet, (0, 0))
        sheet, layout.height = grown, new_height
    else:
        sheet = sheet.copy()
    for x, y, image in placements:
        sheet.paste(image.convert("RGBA"), (x, y))
    return sheet, layout
# endregion


# region DDS (texconv)
class Texconv:
    def __init__(self, exe_path: str):
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"texconv not found at {exe_path}")
        if file_version(exe_path) != TEXCONV_VERSION:
            raise RuntimeError(f"Expected texconv {TEXCONV_VERSION}, found {file_version(exe_path)} at {exe_path}")
        self.exe_path = exe_path

    def _convert(self, source: str, output_dir: str, args: List[str]):
        result = subprocess.run([self.exe_path, "-nologo", "-y", "-o", output_dir, *args, source],
                                capture_output=True, text=True, errors="replace",
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            raise RuntimeError(f"texconv failed on {source}:\n{(result.stdout + result.stderr).strip()}")

    def save_dds(self, image: Image.Image, dds_path: str):
        """BC7_UNORM, single mip level, like the stock menu textures."""
        with tempfile.TemporaryDirectory() as work:
            stem = os.path.splitext(os.path.basename(dds_path))[0]
            png = os.path.join(work, stem + ".png")
            image.convert("RGBA").save(png)
            self._convert(png, work, ["-f", DDS_FORMAT, "-m", "1"])
            os.makedirs(os.path.dirname(os.path.abspath(dds_path)), exist_ok=True)
            shutil.move(os.path.join(work, stem + ".dds"), dds_path)

    def load_dds(self, dds_path: str) -> Image.Image:
        with tempfile.TemporaryDirectory() as work:
            stem = os.path.splitext(os.path.basename(dds_path))[0]
            shutil.copy(dds_path, os.path.join(work, stem + ".dds"))
            self._convert(os.path.join(work, stem + ".dds"), work, ["-ft", "png", "-f", "R8G8B8A8_UNORM"])
            with Image.open(os.path.join(work, stem + ".png")) as image:
                return image.convert("RGBA").copy()
# endregion


# region Rank icons
RANK_ICON_SIZE = (232, 128)


def render_rank_icon(text: str, color: str, font_path: str) -> Image.Image:
    """Generated arena rank icon (e.g. "05/S"): text stretched into a fixed box with a glow, as in the old tool."""
    text_size = (180, 55) if len(text.split("/")[0]) > 2 else (155, 55)
    glow_size, glow_iterations, font_size = 20, 3, 70
    rgb = ImageColor.getcolor(color, mode="RGB")
    font = ImageFont.truetype(font_path, font_size)

    scratch = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    ImageDraw.Draw(scratch).text((0, 0), text, font=font, fill=rgb)
    glyphs = scratch.crop(scratch.getbbox()).resize(text_size, Image.LANCZOS)

    text_layer = Image.new("RGBA", RANK_ICON_SIZE, (0, 0, 0, 0))
    text_layer.paste(glyphs, ((RANK_ICON_SIZE[0] - text_size[0]) // 2, (RANK_ICON_SIZE[1] - text_size[1]) // 2))
    icon = Image.new("RGBA", RANK_ICON_SIZE, (0, 0, 0, 0))
    glow = text_layer.copy()
    for _ in range(glow_iterations):
        glow = glow.filter(ImageFilter.GaussianBlur(glow_size / glow_iterations))
        glow = Image.composite(Image.new("RGBA", RANK_ICON_SIZE, rgb + (0,)), glow, glow)
        icon = Image.alpha_composite(icon, glow)
    return Image.alpha_composite(icon, text_layer)
# endregion
