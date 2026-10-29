"""Builds an ME3 package + profile from a list of fights."""
import os
import shutil
from typing import Iterable, List, Tuple

from ..fight import Fight
from ..ids import TAB_CATEGORIES, fight_ids
from ..package import PackageBuilder, write_profile
from .context import BuildContext
from .steps import ai, designs, images, ranks, regulation, text, voice

PACKAGE_NAME = "CustomArena"
PROFILE_NAME = "custom_arena.me3"
SAVEFILE = "AC6CustomArena.sl2"  # ME3 copies the player's save to this on first launch
STEPS = [regulation, text, designs, ai, images, ranks, voice]


def build(fights: List[Tuple[Fight, int]], game_dir: str, out_dir: str, sources: Iterable[str] = (),
          hide_vanilla_arena: bool = False) -> str:
    """fights: (fight, slot) in arena list order, weakest first (like the stock tabs). Returns the profile path."""
    work_dir = os.path.join(out_dir, "work")
    shutil.rmtree(work_dir, ignore_errors=True)
    ctx = BuildContext(game_dir, work_dir, sources, hide_vanilla_arena)
    tabs = list(dict.fromkeys(fight.tab for fight, _ in fights))  # In order of first use
    if len(tabs) > len(TAB_CATEGORIES):
        raise ValueError(f"At most {len(TAB_CATEGORIES)} tabs are supported, got {len(tabs)}: {tabs}")
    with_ids = [(fight, fight_ids(slot, position, TAB_CATEGORIES[tabs.index(fight.tab)]))
                for position, (fight, slot) in enumerate(fights)]
    for step in STEPS:
        print(f"Building: {step.__name__.rsplit('.', 1)[-1]}")
        step.apply(ctx, with_ids)
    print("Repacking")
    with PackageBuilder(out_dir, PACKAGE_NAME) as package:
        ctx.finish(package)
    profile = os.path.join(out_dir, PROFILE_NAME)
    write_profile(profile, [(PACKAGE_NAME, os.path.join(out_dir, PACKAGE_NAME))], savefile=SAVEFILE)
    return profile
