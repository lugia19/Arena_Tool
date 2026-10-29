"""Rank icons: a SB_CustomArenaRank atlas in 01_common, and the matching frames in the 4 menu GFX files."""
import math
import os

from PIL import Image

from ...atlas import RANK_ICON_SIZE, build_atlas, render_rank_icon
from ...gfx import GfxFile
from ...witchy import add_binder_files, add_tpf_textures

FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "resources", "Jura-SemiBold.ttf")
GFX_FILES = ["menu/01_texteffect_hi.gfx", "menu/02_acarena_preparing.gfx", "menu/02_acarena_select.gfx",
             "menu/02_npcarenaresult.gfx"]
# Generated icons: share of the fights per letter (best first) and its color, as in the old tool.
TIERS = [("S", 10, "#fff145"), ("A", 15, "#83eeee"), ("B", 20, "#7744b2"), ("C", 25, "#0bc367"),
         ("D", 10, "#853322"), ("E", 10, "#e3ffff"), ("F", 10, "#e3ffff")]


def default_rank(rank_number, total):
    """"05/S"-style text and color for rank `rank_number` (1 = best) out of `total`."""
    counts = [math.ceil(share * total / 100) for _, share, _ in TIERS]
    while sum(counts) > total:
        counts[-1] -= 1
        if counts[-1] == 0:
            counts.pop()
    cumulative = 0
    for (letter, _, color), count in zip(TIERS, counts):
        cumulative += count
        if rank_number <= cumulative:
            return f"{rank_number:02d}/{letter}", color
    return f"{rank_number:02d}", "#ffffff"


def apply(ctx, fights):
    icons = {}
    for fight, ids in fights:
        if fight.rank_icon:
            with Image.open(fight.rank_icon) as image:
                icon = image.convert("RGBA").resize(RANK_ICON_SIZE, Image.LANCZOS)
        else:
            tab = [other_ids for _, other_ids in fights if other_ids.category == ids.category]  # Ranks count per tab
            text, color = default_rank(len(tab) - tab.index(ids), len(tab))
            icon = render_rank_icon(fight.rank_text or text, fight.rank_color or color, FONT)
        icons[ids.rank_icon] = icon

    names = {rank: f"CustomArenaRank_{rank:05d}" for rank in icons}
    sheet, layout = build_atlas("SB_ArenaRank", "SB_CustomArenaRank", {names[rank]: icon for rank, icon in icons.items()},
                                *RANK_ICON_SIZE)
    tpf = ctx.unpacked("menu/hi/01_common.tpf.dcx")
    layouts = ctx.unpacked("menu/hi/01_common.sblytbnd.dcx")
    ctx.texconv.save_dds(sheet, os.path.join(tpf, "SB_CustomArenaRank.dds"))
    add_tpf_textures(tpf, ["SB_CustomArenaRank.dds"])
    with open(os.path.join(layouts, "SB_CustomArenaRank.layout"), "w", encoding="utf-8", newline="") as f:
        f.write(layout.to_text())
    add_binder_files(layouts, ["SB_CustomArenaRank.layout"])

    for path in GFX_FILES:
        gfx = GfxFile(ctx.read(path))
        gfx.add_rank_icons(names)
        ctx.add_file(path, gfx.to_bytes())
