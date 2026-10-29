# Arena Maker

Arena Maker adds custom fights to the Arena in ARMORED CORE VI. You collect fights, which can come from other players
or be your own. It turns them into a mod and starts the game with it.

A fight can have:
- its own AC design and custom AI
- an emblem, HP-bar thumbnail, arena preview image and rank icon
- intro and outro dialogue with voice lines
- its own arena tab, alongside or instead of the stock fights

# Using Arena Maker

## Install

1. Download `ArenaMaker-<version>-windows.zip` from the
   [latest release](https://github.com/lugia19/Arena_Maker/releases/latest) and extract it anywhere.
2. Run `ArenaMaker.exe`. On first run it sets up Python and downloads Arena Maker and the tools it needs, which takes
   a few minutes. After that it checks for updates and installs them every time it starts.

The game is found automatically through Steam. If that fails, you'll be asked for the `Game` folder (the one with
`armoredcore6.exe`).

## Adding fights

- **Add folder…** takes a single fight folder (one with a `fight.json`) or a pack folder that holds several fights.
- **Add zip…** does the same for zip files.
- You can also drag folders and zips onto the window.

Arena Maker keeps its own copy of each fight, so you can delete the downloaded files afterwards. Adding a fight with
the same name and author as one you already have replaces that one.

The list sets each tab's order: the first fight is the lowest rank. Change the order with **▲ / ▼**, and use
**Remove** to delete a fight.

**Hide vanilla arena** removes the stock arena fights, so only your custom fights are shown.

## Using another mod as the base

To play the custom fights together with another mod, such as a balance mod, use **Choose…** next to "Base mod" and
pick that mod's folder. Pick the folder that mirrors the game's files, the one with `regulation.bin`, `msg`, and so on.

- The fights are then built on top of that mod's files, so its changes to the regulation and text are kept.
- Arena Maker's launch also loads the base mod, so its other files still apply.
- Don't load the base mod separately as well. **Build && launch** already includes it.
- **Clear** goes back to the stock game.

When you choose a mod, Arena Maker compares it with the game and warns you about anything it changes that custom fights
rely on: arena maps, the arena fights themselves, NPC and AI settings, and the menu files Arena Maker edits. Custom
fights may then play differently from what their authors intended; for example, a mod that moves the arena maps moves
them for custom fights too. You decide whether to use it anyway.

## Playing

- **Build && launch** builds the mod and starts the game.
- **Build** only builds it.

The game runs modded through [me3](https://github.com/garyttierney/me3), and Easy Anti-Cheat is off, so you play
offline.

Modded play uses a separate save, `AC6CustomArena.sl2`, so your normal save never sees the custom fights:
- The first time you launch, it starts as a copy of your normal save.
- To copy your normal save over again, delete `AC6CustomArena.sl2` from `%APPDATA%\ArmoredCore6\<your Steam ID>\`.
  The next launch makes a fresh copy.

The game saves arena clears by position in the list. If you reorder fights or remove one, the clear marks stay with the
positions, not with the fights.

**Open data folder** shows where the library and the built mod are kept: `%APPDATA%\lugia19\ac6_arena_maker`.

If something goes wrong, **Show log** displays the full build output.

# Making a fight

A fight is a folder with a `fight.json` and the files it uses. Paths in `fight.json` are relative to that folder.
[`examples/example_fight`](examples/example_fight) is a complete example to copy from.

```json
{
  "format": 1,
  "name": "Example One",
  "author": "lugia19",
  "tab": "CUSTOM ARENA",
  "ac": {"design": "example.design", "name": "Example", "pilot": "One"},
  "arena": {"description": "Something something, this is the arena description blurb.", "map": 9411},
  "ai": {"logic": "custom_logic.lua"},
  "images": {"emblem": "emblem.png", "preview": "preview.png"},
  "dialogue": {
    "intro": [{"text": "Intro 1", "audio": "intro1.wav"}],
    "outro": [{"text": "Outro 1", "audio": "outro1.wav"}]
  }
}
```

## Required fields

- `format`: always `1`.
- `name` and `author`: together they identify the fight. A fight with the same name and author replaces the older
  one in a player's library, so keep both the same when you release an update.
- `ac.design`: the AC, as a `.design` file. You can make one with
  [AC6 Design Editor](https://github.com/lugia19/AC6_Design_Editor/releases/).
- `ac.name` and `ac.pilot`: the AC and pilot names shown in the arena list and during the fight.
- `arena.description`: the profile text on the arena screen.

## Optional fields

- **Tab**: `tab` names the arena tab the fight appears in. The default is `CUSTOM ARENA`. Fights with the same tab name
  are grouped, with up to 20 custom tabs. `tabColor` (`#rrggbb`) colors the tab name; the first fight in a tab that
  sets one decides it.
- **Arena settings**:
  - `arena.map`: the arena map.
  - `firstReward` / `rematchReward`: COAM rewards.
  - `bgm`: background music.
  - `startCutscene` / `endCutscene`: cutscenes.
- **AI**:
  - `ai.logic`: a custom Lua logic script.
  - `ai.logicId`: reuses one of the game's AIs.
  - With neither, the fight uses "Cinder" Carla's AI.
- **Images**:
  - `emblem`: the emblem shown in the intro.
  - `thumbnail`: the HP-bar icon. Defaults to the emblem.
  - `preview`: the arena preview.
  - `rankIcon`: the rank icon.

  Any common image format works, and images are scaled to fit. Without a `rankIcon`, Arena Maker draws one from the
  fight's position, like `05/S`. You can override its text and color with `rank.text` and `rank.color`.
- **Dialogue**:
  - `dialogue.intro` can have up to 3 lines and `dialogue.outro` up to 2.
  - Each line has `text` and an optional `audio` file (wav, flac, ogg or mp3).
  - `dialogue.speaker` sets who the subtitles are attributed to. The default is 200, ALLMIND.
- **Decals**: `addEmblemToDecals` (default `true`) also lets players use the emblem as a decal.

The full field reference, with defaults, is in [docs/fight_format.md](docs/fight_format.md).

## Sharing fights

Zip the fight folder and share the zip. To share several fights as a pack, put each fight in its own subfolder of a
folder (or zip). Players add it with **Add folder…** / **Add zip…**.

To test a fight, add it, then use **Build && launch**. Each time you change the fight, add it again; it replaces the old
copy and keeps its place in the list.

# Development

Run from source with Python 3.11 and `pip install -r requirements.txt`:
- `python main.py` opens the window.
- `python -m arena_maker --help` gives the command-line interface (list, add, remove, move, hide-vanilla, base-mod,
  build, launch).

The tools are downloaded into `tools/` on the first start of the window.
- To assemble them yourself from local copies of the pinned versions, run `python scripts/prepare_tools.py`.
- To build a release `tools.zip`, add `--zip PATH`, then update `TOOLS_VERSION`, `TOOLS_URL` and `TOOLS_SHA256` in
  `arena_maker/tools.py`.

[docs/arena_format.md](docs/arena_format.md) documents how the game's arena works and what Arena Maker generates.
`launcher/` holds the [pygo-bootstrap](https://github.com/lugia19/pygo-bootstrap) settings and icon used for the
release launcher.

See [THIRD_PARTY.md](THIRD_PARTY.md) for the bundled tools and their licenses.
