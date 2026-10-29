"""Builds an ME3 package + profile from a list of fights."""
import os
import shutil
from typing import Callable, List, Optional, Tuple

from ..fight import Fight
from ..ids import TAB_CATEGORIES, fight_ids
from ..package import PackageBuilder, write_profile
from .context import BuildContext
from .steps import ai, designs, images, music, ranks, regulation, text, voice

PACKAGE_NAME = "CustomArena"
BASE_PACKAGE_NAME = "BaseMod"
PROFILE_NAME = "custom_arena.me3"
SAVEFILE = "AC6CustomArena.sl2"  # ME3 copies the player's save to this on first launch
STEPS = [regulation, text, designs, ai, images, ranks, voice, music]


def build(fights: List[Tuple[Fight, int]], game_dir: str, out_dir: str, base_mod: Optional[str] = None,
          hide_vanilla_arena: bool = False, log: Callable[[str], None] = print) -> str:
    """fights: (fight, slot) in arena list order, weakest first (like the stock tabs). Returns the profile path.

    base_mod: another mod's package folder. The fights are added on top of its files, and the profile loads it before
    our package, so its other files still apply and ours win where both have a file."""
    if base_mod and not os.path.isdir(base_mod):
        raise FileNotFoundError(f"The base mod folder doesn't exist: {base_mod}")
    work_dir = os.path.join(out_dir, "work")
    shutil.rmtree(work_dir, ignore_errors=True)
    ctx = BuildContext(game_dir, work_dir, [base_mod] if base_mod else [], hide_vanilla_arena)
    tabs = list(dict.fromkeys(fight.tab for fight, _ in fights))  # In order of first use
    if len(tabs) > len(TAB_CATEGORIES):
        raise ValueError(f"At most {len(TAB_CATEGORIES)} tabs are supported, got {len(tabs)}: {tabs}")
    with_ids = [(fight, fight_ids(slot, position, TAB_CATEGORIES[tabs.index(fight.tab)]))
                for position, (fight, slot) in enumerate(fights)]
    for step in STEPS:
        log(f"Building: {step.__name__.rsplit('.', 1)[-1]}")
        step.apply(ctx, with_ids)
    log("Repacking")
    with PackageBuilder(out_dir, PACKAGE_NAME) as package:
        ctx.finish(package)
    profile = os.path.join(out_dir, PROFILE_NAME)
    packages = [(BASE_PACKAGE_NAME, base_mod)] if base_mod else []  # me3: a later package overrides earlier ones
    packages.append((PACKAGE_NAME, os.path.join(out_dir, PACKAGE_NAME)))
    write_profile(profile, packages, savefile=SAVEFILE)
    return profile
