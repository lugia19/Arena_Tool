"""AC builds: each fight's .design file goes into asmparam.designbnd as <chara ID>.design (CharaInitParam.assemDataID)."""
import os
import shutil

from ...witchy import add_binder_files


def apply(ctx, fights):
    folder = ctx.unpacked("param/asmparam/asmparam.designbnd.dcx")
    for fight, ids in fights:
        shutil.copy(fight.design, os.path.join(folder, f"{ids.chara}.design"))
    add_binder_files(folder, [f"{ids.chara}.design" for _, ids in fights])
