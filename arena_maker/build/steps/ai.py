"""Custom AI: a script/<logic ID>_logic.luabnd.dcx per fight with a logic file, made from Carla's as a template.

The game runs plain Lua source, so the fight's script goes in as-is, with its own logic ID (found in its
LogicInitialSetup_<id> function) replaced by the fight's. aicommon gets the EZOP_SystemFunc.lua with the Log()
helper that custom scripts may use.
"""
import os
import re

TEMPLATE_LOGIC_ID = "11200000"
RESOURCES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "resources")


def apply(ctx, fights):
    custom = [(fight, ids) for fight, ids in fights if fight.logic_file]
    if not custom:
        return

    aicommon = ctx.unpacked("script/aicommon.luabnd.dcx")
    with open(os.path.join(RESOURCES, "EZOP_SystemFunc.lua"), encoding="utf-8") as f:
        system_func = f.read()
    with open(os.path.join(aicommon, "EZOP_SystemFunc.lua"), "w", encoding="utf-8") as f:
        f.write(system_func)

    template = ctx.read(f"script/{TEMPLATE_LOGIC_ID}_logic.luabnd.dcx")
    for fight, ids in custom:
        new_id = str(ids.chara)
        with open(fight.logic_file, encoding="utf-8") as f:
            script = f.read()
        old_id = re.search(r"LogicInitialSetup_(\d+)", script)
        if not old_id:
            raise ValueError(f"{fight.logic_file}: no LogicInitialSetup_<id> function found")
        script = script.replace(old_id.group(1), new_id)

        # Unpack the template under the new name; its contents (lua, luagnl, manifest) still use the template's ID.
        path = ctx.work_path(f"script/{new_id}_logic.luabnd.dcx")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(template)
        ctx.witchy.unpack(path, recursive=True)
        folder = os.path.join(os.path.dirname(path), f"{new_id}_logic-luabnd-dcx")
        for name in os.listdir(folder):
            file_path = os.path.join(folder, name)
            if name.endswith(".luagnl"):
                os.remove(file_path)  # Rebuilt from the .luagnl.xml
                continue
            if name.endswith(".lua"):
                content = script
            else:
                with open(file_path, encoding="utf-8-sig") as f:
                    content = f.read().replace(TEMPLATE_LOGIC_ID, new_id)
            os.remove(file_path)
            with open(os.path.join(folder, name.replace(TEMPLATE_LOGIC_ID, new_id)), "w", encoding="utf-8") as f:
                f.write(content)
        # A recursive repack doesn't recreate the deleted .luagnl, so convert it explicitly first.
        ctx.witchy.repack(os.path.join(folder, f"{new_id}_logic.luagnl.xml"))
        ctx.witchy.repack(folder)
        with open(path, "rb") as f:
            ctx.add_file(f"script/{new_id}_logic.luabnd.dcx", f.read())
