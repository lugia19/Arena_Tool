"""What a base mod changes that ArenaTool also edits or relies on. Nothing is corrected automatically: the player
sees the list and decides whether to build on top of that mod anyway."""
import os
import tempfile
from typing import List

from .build.context import BuildContext
from .build.steps import music, ranks, text, voice

# The params the build edits, plus MissionParam (the fights' maps)
CHECKED_PARAMS = ["ArenaParam", "MissionParam", "AccountParam", "CharaInitParam", "NpcParam", "NpcThinkParam",
                  "TalkParam", "PresetEmblemSpec"]
NAME_FIELDS = {"name", "paramdexName"}  # Row names: a mod's regulation often embeds them, the stock one doesn't
EDITED_FILES = (ranks.GFX_FILES + voice.BANKS + [f"msg/{language}/{bnd}.msgbnd.dcx" for language in text.LANGUAGES
                                                 for bnd in ("menu", "item")]
                + ["menu/hi/00_solo.tpfbdt", "menu/hi/01_common.tpf.dcx", "menu/hi/01_common.sblytbnd.dcx",
                   "param/asmparam/asmparam.designbnd.dcx", "script/aicommon.luabnd.dcx", music.INIT_BANK,
                   music.MUSIC_BANK])


def _rows(param) -> dict:
    return {row.get("id"): {k: v for k, v in param.values(row).items() if k not in NAME_FIELDS} for row in param.rows}


def _ids(ids: List[str]) -> str:
    ids = sorted(ids, key=int)
    return ", ".join(ids[:8]) + (f" and {len(ids) - 8} more" if len(ids) > 8 else "")


def find_overlaps(game_dir: str, base_mod: str) -> List[str]:
    """One line per param or group of files where the base mod differs from the stock game in something we touch."""
    overlaps = []
    if os.path.isfile(os.path.join(base_mod, "regulation.bin")):
        with tempfile.TemporaryDirectory() as work:
            stock = BuildContext(game_dir, os.path.join(work, "stock"))
            base = BuildContext(game_dir, os.path.join(work, "base"), [base_mod])
            for name in CHECKED_PARAMS:
                stock_rows, base_rows = _rows(stock.param(name)), _rows(base.param(name))
                added = [i for i in base_rows if i not in stock_rows]
                removed = [i for i in stock_rows if i not in base_rows]
                changed = [i for i in base_rows if i in stock_rows and base_rows[i] != stock_rows[i]]
                for kind, ids in (("adds", added), ("removes", removed), ("changes", changed)):
                    if ids:
                        overlaps.append(f"{name}: {kind} {len(ids)} rows ({_ids(ids)})")
    files = [path for path in EDITED_FILES if os.path.isfile(os.path.join(base_mod, *path.split("/")))]
    if files:
        overlaps.append("Also edits " + ", ".join(files))
    return overlaps
