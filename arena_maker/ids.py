"""Every game ID a custom fight uses, derived from its slot (permanent identity) and position (rank order).

All ranges were checked against the stock params, text and decal thumbnails for 1000 fights (docs/arena_format.md).
"""
from dataclasses import dataclass

TAB_CATEGORY = 20            # ArenaParam.category of the custom tab (stock tabs are 0 and 10)
TAB_NAME_TEXT_ID = 258030    # MenuText entry for the tab name: 258010 + category
PRESET_EMBLEM_CATEGORY = 2   # PresetEmblemSpec.CategoryID of the decal tab custom emblems go in (PRESET 3)


@dataclass(frozen=True)
class FightIds:
    arena: int           # ArenaParam row, RankerProfile text
    account: int         # AccountParam row; AC/pilot names are text account..account+3
    chara: int           # CharaInitParam/NpcParam/NpcThinkParam rows, logic ID, design file
    emblem: int          # MENU_Decal_/Decal_tmb_ ID; below 10000 so it can also be a player decal
    preset_emblem: int   # PresetEmblemSpec row
    rank_icon: int       # ArenaParam.rankIconID = frame of the rank icon sprite

    def intro_talk(self, line: int) -> int:
        return 600000000 + self.account * 1000 + 100 + line

    def outro_talk(self, line: int) -> int:
        return 700000000 + self.account * 1000 + line


def fight_ids(slot: int, position: int) -> FightIds:
    return FightIds(
        arena=300 + slot,
        account=16000 + 10 * slot,
        chara=999009800 + slot,
        emblem=4000 + slot,
        preset_emblem=5000 + slot,
        rank_icon=300 - position,  # Stock ranks use frames 0-31 and 101-113
    )
