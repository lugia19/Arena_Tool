"""Every game ID a custom fight uses, derived from its slot (permanent identity) and position (rank order).

All ranges were checked against the stock params, text and decal thumbnails for 1000 fights (docs/arena_format.md).
"""
from dataclasses import dataclass

# ArenaParam.category of custom tabs, in order of use. Tested in game: tabs are shown in category order (stock: 0 and
# 10), any value works (not just multiples of 10), 6 tabs fit. A tab's name is MenuText 258010 + category, and
# 258030-258049 are unused, so 20-39 gives 20 tabs after the stock ones without touching other arena UI text.
TAB_CATEGORIES = list(range(20, 40))
PRESET_EMBLEM_CATEGORY = 2   # PresetEmblemSpec.CategoryID of the decal tab custom emblems go in (PRESET 3)


def tab_name_text_id(category: int) -> int:
    return 258010 + category


@dataclass(frozen=True)
class FightIds:
    # The game lists a tab's fights in ArenaParam ID order and saves clears by ArenaParam ID, so this one follows the
    # list position: reordering works, and a clear stays with the position. Everything else follows the slot.
    arena: int           # ArenaParam row, RankerProfile text
    account: int         # AccountParam row; AC/pilot names are text account..account+3
    chara: int           # CharaInitParam/NpcParam/NpcThinkParam rows, logic ID, design file
    emblem: int          # MENU_Decal_/Decal_tmb_ ID; below 10000 so it can also be a player decal
    preset_emblem: int   # PresetEmblemSpec row
    rank_icon: int       # ArenaParam.rankIconID = frame of the rank icon sprite
    category: int        # ArenaParam.category = the fight's tab
    speaker: int         # TalkParam.talkerID for a speaker named in fight.json; subtitles show text speaker+3

    def intro_talk(self, line: int) -> int:
        return 600000000 + self.account * 1000 + 100 + line

    def outro_talk(self, line: int) -> int:
        return 700000000 + self.account * 1000 + line


def fight_ids(slot: int, position: int, category: int) -> FightIds:
    """slot: the fight's permanent number; position: its place in the overall build list."""
    return FightIds(
        arena=300 + position,
        account=16000 + 10 * slot,
        chara=999009800 + slot,
        emblem=4000 + slot,
        preset_emblem=5000 + slot,
        rank_icon=300 - position,  # Stock ranks use frames 0-31 and 101-113
        category=category,
        speaker=17000 + 10 * slot,
    )
