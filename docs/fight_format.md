# Fight format

A fight is a folder with a `fight.json` and the files it refers to (paths are relative to the folder). A pack is a
folder (or zip) whose subfolders are fights. `examples/example_fight` uses every field.

A fight is identified by **author + name**: importing a fight whose author and name are already in the library
replaces the old version, keeping its place in the list.

```json
{
  "format": 1,
  "name": "Example One",
  "author": "lugia19",
  "tab": "CUSTOM ARENA",
  "tabColor": "#4fc3f7",
  "ac": {"design": "example.design", "name": "Example", "pilot": "One"},
  "arena": {"description": "...", "map": 9411, "firstReward": 1, "rematchReward": 1,
            "bgm": 50000, "startCutscene": 230000, "endCutscene": -1},
  "ai": {"logic": "custom_logic.lua"},
  "images": {"emblem": "emblem.png", "thumbnail": "thumbnail.png", "preview": "preview.png", "rankIcon": "rank_icon.png"},
  "rank": {"text": "05/S", "color": "#fff145"},
  "dialogue": {"speaker": "Arena Announcer",
               "intro": [{"text": "...", "audio": "intro1.wav"}],
               "outro": [{"text": "...", "audio": "outro1.wav"}]},
  "addEmblemToDecals": true
}
```

| Field | Required | Default | Notes |
|---|---|---|---|
| `format` | yes | | Always 1 for now. |
| `name`, `author` | yes | | Together they identify the fight. |
| `tab` | | `"CUSTOM ARENA"` | Fights with the same tab name share an arena tab (up to 20 tabs). |
| `tabColor` | | white | The tab name's color, as `#rrggbb`. The first fight in a tab that sets one decides it. |
| `ac.design` | yes | | A `.design` file (e.g. from AC6 Design Editor). |
| `ac.name`, `ac.pilot` | yes | | Shown in the arena list and during the fight. |
| `arena.description` | yes | | The arena profile text. |
| `arena.map` | | 9410 | MissionParam ID of the arena map. |
| `arena.firstReward`, `arena.rematchReward` | | 1 | COAM for the first and later clears. |
| `arena.bgm` | | 50000 | |
| `arena.startCutscene`, `arena.endCutscene` | | 230000, -1 | 230000 is the generic intro; -1 = none. |
| `ai.logic` | | | A Lua logic script (plain source works). It must define `LogicInitialSetup_<id>`; that ID is replaced. |
| `ai.logicId` | | | Use an existing game AI instead. Without either, the fight uses "Cinder" Carla's AI. |
| `images.emblem` | | | Intro emblem, scaled to 1024x1024. Without it, Carla's emblem is used. |
| `images.thumbnail` | | the emblem | HP-bar icon, scaled to 128x128. |
| `images.preview` | | | Arena preview, scaled to 2048x893. |
| `images.rankIcon` | | generated | 232x128. Otherwise an icon like "05/S" is drawn from the fight's rank in its tab. |
| `rank.text`, `rank.color` | | | Override the generated icon's text and color. |
| `dialogue.speaker` | | 200 | Who the subtitles are attributed to: a name (a new speaker is added for it), or an existing speaker's ID, i.e. an AccountParam ID like 200 (ALLMIND), 70 (Handler Walter) or 310 (Carla). |
| `dialogue.intro` / `outro` | | | Up to 3 / 2 lines: `text`, optional `audio` (wav, flac, ogg, mp3). |
| `addEmblemToDecals` | | true | Also offer the emblem as a decal in the player's decal menu. |

Images can be any format Pillow reads (png, jpg, webp, ...).
