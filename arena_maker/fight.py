"""The fight format: a folder with a fight.json and the files it refers to (example: examples/example_fight)."""
import json
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Union

FORMAT_VERSION = 1


@dataclass
class DialogueLine:
    text: str
    audio: Optional[str] = None  # Absolute path


@dataclass
class Fight:
    folder: str
    name: str                    # name + author identify a fight in the library
    author: str
    design: str                  # Absolute paths from here on
    ac_name: str
    pilot_name: str
    description: str
    map_id: int = 9410
    first_reward: int = 1
    rematch_reward: int = 1
    bgm: int = 50000
    start_cutscene: int = 230000
    end_cutscene: int = -1
    logic_file: Optional[str] = None
    logic_id: Optional[int] = None  # Existing logic to use; with neither, the template fight's logic is kept
    emblem: Optional[str] = None
    thumbnail: Optional[str] = None
    preview: Optional[str] = None
    rank_icon: Optional[str] = None
    rank_text: Optional[str] = None
    rank_color: Optional[str] = None
    speaker: Union[int, str] = 200   # A TalkParam.talkerID (200 = ALLMIND), or a new speaker's name
    intro: List[DialogueLine] = field(default_factory=list)
    outro: List[DialogueLine] = field(default_factory=list)
    add_emblem_to_decals: bool = True
    tab: str = "CUSTOM ARENA"        # Fights with the same tab name share an arena tab
    tab_color: Optional[str] = None  # "#rrggbb"; the first fight in a tab that sets one decides


def load_fight(folder: str) -> Fight:
    with open(os.path.join(folder, "fight.json"), encoding="utf-8") as f:
        data = json.load(f)
    if data.get("format") != FORMAT_VERSION:
        raise ValueError(f"{folder}: unsupported fight format {data.get('format')!r}")

    def path(relative):
        if relative is None:
            return None
        full = os.path.join(folder, relative)
        if not os.path.isfile(full):
            raise FileNotFoundError(f"{folder}: {relative} not found")
        return full

    arena, ai, images, rank, dialogue = (data.get(key, {}) for key in ("arena", "ai", "images", "rank", "dialogue"))
    lines = {kind: [DialogueLine(line["text"], path(line.get("audio"))) for line in dialogue.get(kind, [])]
             for kind in ("intro", "outro")}
    if data.get("tabColor") is not None and not re.fullmatch(r"#[0-9a-fA-F]{6}", data["tabColor"]):
        raise ValueError(f"{folder}: tabColor must look like #ff9900")
    if not isinstance(dialogue.get("speaker", 200), (int, str)):
        raise ValueError(f"{folder}: dialogue.speaker must be a name or a speaker ID")
    if len(lines["intro"]) > 3 or len(lines["outro"]) > 2:
        raise ValueError(f"{folder}: at most 3 intro and 2 outro lines")

    return Fight(
        folder=folder,
        name=data["name"],
        author=data["author"],
        design=path(data["ac"]["design"]),
        ac_name=data["ac"]["name"],
        pilot_name=data["ac"]["pilot"],
        description=arena["description"],
        map_id=arena.get("map", 9410),
        first_reward=arena.get("firstReward", 1),
        rematch_reward=arena.get("rematchReward", 1),
        bgm=arena.get("bgm", 50000),
        start_cutscene=arena.get("startCutscene", 230000),
        end_cutscene=arena.get("endCutscene", -1),
        logic_file=path(ai.get("logic")),
        logic_id=ai.get("logicId"),
        emblem=path(images.get("emblem")),
        thumbnail=path(images.get("thumbnail")),
        preview=path(images.get("preview")),
        rank_icon=path(images.get("rankIcon")),
        rank_text=rank.get("text"),
        rank_color=rank.get("color"),
        speaker=dialogue.get("speaker", 200),
        intro=lines["intro"],
        outro=lines["outro"],
        add_emblem_to_decals=data.get("addEmblemToDecals", True),
        tab=data.get("tab", "CUSTOM ARENA"),
        tab_color=data.get("tabColor"),
    )
