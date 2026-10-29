"""Emblems (MENU_Decal_), arena previews (MENU_Archetype_) and HP-bar thumbnails (Decal_tmb_)."""
import os
import shutil

from PIL import Image, ImageOps

from ...atlas import Layout, add_to_atlas
from ...witchy import add_binder_files, new_single_texture_tpf

EMBLEM_SIZE = (1024, 1024)
PREVIEW_SIZE = (2048, 893)  # Padded at the bottom to 2048x1024, like the stock previews
THUMBNAIL_SIZE = (128, 128)


def open_image(path, size):
    with Image.open(path) as image:
        return image.convert("RGBA").resize(size, Image.LANCZOS)


def apply(ctx, fights):
    textures = {}  # 00_solo texture name -> image
    thumbnails = {}
    for fight, ids in fights:
        if fight.emblem:
            textures[f"MENU_Decal_{ids.emblem:08d}"] = open_image(fight.emblem, EMBLEM_SIZE)
            thumbnails[f"Decal_tmb_{ids.emblem:08d}"] = open_image(fight.thumbnail or fight.emblem, THUMBNAIL_SIZE)
        if fight.preview:
            preview = ImageOps.expand(open_image(fight.preview, PREVIEW_SIZE), (0, 0, 0, 1024 - PREVIEW_SIZE[1]))
            textures[f"MENU_Archetype_{ids.chara}"] = preview

    if textures:
        solo = ctx.unpacked("menu/hi/00_solo.tpfbdt")
        for name, image in textures.items():
            folder = new_single_texture_tpf(solo, name)
            ctx.texconv.save_dds(image, os.path.join(folder, name + ".dds"))
            ctx.witchy.repack(folder)
            shutil.rmtree(folder)
        add_binder_files(solo, [name + ".tpf.dcx" for name in textures])

    if thumbnails:
        tpf = ctx.unpacked("menu/hi/01_common.tpf.dcx")
        layouts = ctx.unpacked("menu/hi/01_common.sblytbnd.dcx")
        sheet_path, layout_path = os.path.join(tpf, "SB_DecalThumbnails.dds"), os.path.join(layouts, "SB_DecalThumbnails.layout")
        with open(layout_path, encoding="utf-8-sig") as f:
            layout = Layout.parse(f.read())
        sheet, layout = add_to_atlas(ctx.texconv.load_dds(sheet_path), layout, thumbnails, *THUMBNAIL_SIZE, extra={"half": "0"})
        ctx.texconv.save_dds(sheet, sheet_path)
        with open(layout_path, "w", encoding="utf-8", newline="") as f:
            f.write(layout.to_text())
