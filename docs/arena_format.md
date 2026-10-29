# How an AC6 arena fight is put together

Reference for adding custom fights to the ARMORED CORE VI arena: which files, params and IDs are involved and how
they point at each other. It collects the research behind the original Arena Guide (`lugia19/AC6_Arena_Guide`) and
ArenaTool, updated for game version 1.09.1 / regulation `10910042` and the tools pinned by `arena_maker/`.

Notes are marked **verified** when they were checked against game files or in game while writing the rewrite
(2026-10), and **from the guide** when they come from the original research and weren't re-checked.

Example values are from the stock fight *"Cinder" Carla / FULL COURSE* (ArenaParam 118).

## Overview

```
ArenaParam (one row per fight)
 ├─ category ──────────────► arena tab; tab name = MenuText 258010 + category
 ├─ rankIconID ────────────► frame of the rank icon sprite in 4 menu .gfx files ─► atlas subtexture
 ├─ missionParamID ────────► arena map
 ├─ ranker_accountParamID ─► AccountParam ─┬─ nameTextID ────► TitleCharacters: AC name, pilot name (x2)
 │                                         └─ emblemImageID ─► MENU_Decal_<id> (intro emblem)
 │                                                             Decal_tmb_<id> (HP bar thumbnail)
 ├─ ranker_chrInitParamID ─► CharaInitParam ─ assemDataID ───► <id>.design in asmparam.designbnd.dcx
 │                           (its ID also picks the arena preview image MENU_Archetype_<id>)
 ├─ ranker_npcParamID ─────► NpcParam (nameId -> the AccountParam again)
 └─ ranker_thinkParamID ───► NpcThinkParam ─ logicId ────────► script/<logicId>_logic.luabnd.dcx (AI)
RankerProfile <ArenaParam ID>  = the fight's description
TalkParam 6xx/7xx IDs from the account ID = intro/outro lines (text in TalkMsg, voice in sd/enus/npc015.bnk)
```

## Params (`regulation.bin`)

Field names are the ones in the Paramdex that WitchyBND 3.0.1 ships (AC6 defs last updated for 1.07, still matching
1.09.1). The original guide and ArenaTool used older names; those are listed so old notes and fight files still
make sense. **Verified** against the unpacked 1.09.1 regulation.

### ArenaParam: one row per fight

| Field (current) | Old name | Carla | Notes |
|---|---|---|---|
| `id` | `ID` | 118 | Stock tabs: 1xx = first tab, 2xx = second. A tab lists its fights in ID order (**verified**). Custom fights use 300+. |
| `category` | `menuCategory` | 0 | The tab. Stock: 0, 10. Tab name = MenuText `258010 + category` (258010 "RECORDS", 258020 "ANALYSIS"). See Tabs. |
| `missionParamID` | `missionParamId` | 9401 | Arena map. |
| `rankIconID` | `rankTextureId` | 11 | Frame of the rank icon sprite (see Rank icons). |
| `rankTextID` | - | 258518 | Most likely unused. Stock values follow the tab and position (rows 100-128: 258500-258528, rows 200-211: 258950-258961), but 20 of the 41 IDs exist in no text file (`menu`/`item`, engus and jpnjp), and the rest only overlap `FNR_ダイアログ`'s generic arena sortie dialogs ("Begin the program?", overload warnings) or `%null%` entries (**verified**). ArenaTool copied Carla's value to every custom fight without problems. |
| `ranker_accountParamID` | `accountParamId` | 310 | |
| `ranker_chrInitParamID` | `charaInitParamId` | 11200000 | |
| `ranker_npcParamID` | `npcParamId` | 11200000 | |
| `ranker_thinkParamID` | `npcThinkParamId` | 11200000 | |
| `firstReward_cash` | `initialCoamReward` | 74000 | COAM for the first clear. |
| `rematchReward_cash` | `repeatCoamReward` | 37000 | COAM for later clears. |
| `startCutsceneId` | `introCutsceneId` | 230000 | 230000 = the generic intro. |
| `endCutsceneId` | `outroCutsceneId` | -1 | -1 = none. |
| `bgmId` | `bgmSoundId` | 50000 | |
| `rewardTokenID`, `*_osExp`, `*_reserved` | - | 0 | Copied from the template row. |

### Tabs, order and hiding the stock fights

**Verified in game**:

- Every `category` value used by some row becomes a tab, shown in category order; values don't have to be multiples
  of 10 (21 worked) and at least 6 tabs fit. `category` is an s8.
- Tab names are MenuText `258010 + category`. 258030-258049 are unused, so categories 20-39 give 20 custom tabs after
  the stock ones; 40, 50, 90 and 100 would overwrite other arena UI text ("MATCH INFO", "REWARD", "RANK", ...).
- Within a tab, fights are listed in ArenaParam ID order. Clears are also saved by ArenaParam ID (see Saves), so the
  list order and the clear tracking can't be separated.
- ArenaParam has no "enabled" field, but removing the stock rows (categories 0 and 10, keeping the empty row 0)
  hides the stock tabs; the arena keeps working with only custom tabs.

### AccountParam: name and emblem

| Field | Old name | Carla | Notes |
|---|---|---|---|
| `nameTextID` | `fmgId` | 310 | TitleCharacters (`NPC名`) entries `n, n+1, n+2, n+3` = AC name, pilot name, AC name, pilot name. **Verified**: 310-313 = "FULL COURSE", "\"Cinder\" Carla", "FULL COURSE", "\"Cinder\" Carla". |
| `emblemImageID` | `menuDecalId` | 12 | Picks `MENU_Decal_<id:08>` (intro emblem) and `Decal_tmb_<id:08>` (HP bar thumbnail). Below 10000 if it should also be a player decal (see Emblem IDs). |

The account ID also drives the talk IDs (below). ArenaTool gives each fight account `16000 + 10 * index` and uses
the same number for `nameTextID` and `emblemImageID`.

### CharaInitParam, NpcParam, NpcThinkParam

| Param | Field | Old name | Carla | Notes |
|---|---|---|---|---|
| CharaInitParam | `assemDataID` | `acDesignId` | 11200000 | The `.design` file (the AC build). The row ID also selects the preview image `MENU_Archetype_<id>`. |
| NpcParam | `nameId` | `accountParamId` | 310 | Points at the AccountParam (from the guide; Carla's value matches her account). Sets the in-fight name. |
| NpcThinkParam | `logicId` | `logicId` | 11200000 | The AI script. |

Everything else is copied from a template fight. ArenaTool uses Carla's rows (`11200000` everywhere) as the
template because all her IDs are the same number.

### TalkParam: intro and outro lines

| Field | Old name | Carla 1st intro | Notes |
|---|---|---|---|
| `msgId` | `msgId` | 600310100 | TalkMsg (`会話`) entry, the subtitle. |
| `voiceId` | `voiceId` | 600310100 | The `Play_v<voiceId>` event in the soundbank. |
| `talkerID` | `characterNameTextId` | 200 | Speaker: an AccountParam row; the subtitle shows NpcName text `nameTextID + 3` of that row (200 -> 203 "ALLMIND", 70 -> 73 "Handler Walter"). A talkerID without an AccountParam row shows no speaker (**verified**). A named speaker gets AccountParam row 17000 + 10 * slot, cloned from 200, with its name at +3. |

Talk IDs come from the AccountParam ID (from the guide, matches all stock arena lines):

- intro lines: `600000000 + accountID * 1000 + 100 + i`, i = 0..2
- outro lines: `700000000 + accountID * 1000 + i`, i = 0..1

Use the same number for the TalkParam ID, `msgId` and `voiceId`.

## Text (`msg/<language>/*.msgbnd.dcx`)

FMG files inside the msgbnds, by their Japanese names (as unpacked by WitchyBND):

| Use | msgbnd | FMG | ID |
|---|---|---|---|
| Tab name | `menu.msgbnd.dcx` | `FNR_メニューテキスト` (MenuText) | `258010 + category` |
| Fight description | `menu.msgbnd.dcx` | `ランカープロフィール` (RankerProfile) | ArenaParam ID |
| Intro/outro subtitles | `menu.msgbnd.dcx` | `会話` (TalkMsg) | talk ID |
| AC and pilot names | `item.msgbnd.dcx` | `NPC名` (TitleCharacters) | `nameTextID` .. `+3` |

Languages (`msg/<x>/`): araae, common, deude, engus, frafr, itait, jp, jpnjp, korkr, polpl, porbr, rusru, spaar,
spaes, thath, zhocn, zhotw. ArenaTool only ever edited `engus`; anyone playing in another language sees missing
text for custom fights unless the entries are copied into their language too.

## AC builds (`param/asmparam/asmparam.designbnd.dcx`)

A BND4 of `<id>.design` files. Add `<assemDataID>.design` to the unpacked folder and list it in `_witchy-bnd4.xml`
(next free ID). `.design` files can be made with AC6 Design Editor (`lugia19/AC6_Design_Editor`). From the guide:
changing `DataName`/`AcName` inside the design is optional.

## AI (`script/<logicId>_logic.luabnd.dcx`)

A BND4 with two files. ArenaTool builds it from scratch; the layout below is **verified** against the stock
`11200000_logic.luabnd.dcx`:

| ID | File | Content |
|---|---|---|
| 1000 | `<logicId>_logic.lua` | The logic script. Plain-text Lua source works (from the original tool); it doesn't have to be compiled. |
| 1000000 | `<logicId>_logic.luagnl` | Global function names: `LogicInitialSetup_<logicId>`, `InterruptCallBack_<logicId>`. |

Manifest root: `W:\FNR\data\Target\INTERROOT_win64\script\ai\out\each\<logicId>_logic`, DCX_KRAK, BND4 version
`07D7R6`. The script itself contains its logic ID (in those function names), so a copied script needs every
occurrence of the old ID replaced.

Stock logic files are compiled Lua 5.0 bytecode (header `1B 4C 75 61 50`: ESC "Lua" + version byte 0x50);
DSLuaDecompiler (ElaDiDu's fork names more variables) turns them back into source. `Research/EZOP Research/AC6_EZOP_writeup.md` documents how the AC AI picks
actions.

`script/aicommon.luabnd.dcx` holds the shared AI code. ArenaTool shipped a copy whose `EZOP_SystemFunc.lua` was
replaced with decompiled source plus a `Log()` helper (writes to `debug-logs/`, off by default) that custom scripts
may call. The game's Lua has `io` and `os` available; that's how the logger works.

## Images

### Intro emblem and arena preview (`menu/hi/00_solo.tpfbhd` + `.tpfbdt`)

A split binder (BXF4) of one-texture TPFs. **Verified** stock formats:

| File | Picked by | Texture |
|---|---|---|
| `MENU_Decal_<emblemImageID:08>.tpf.dcx` | AccountParam `emblemImageID` | 1024x1024, BC7_UNORM, 1 mip |
| `MENU_Archetype_<CharaInitParam ID>.tpf.dcx` | CharaInitParam row ID | 2048x1024, BC7_UNORM, 1 mip |

ArenaTool scales preview images to 2048x893 and pads them to 1024 high. Each TPF holds one `<name>.dds`, TPF
format code 102 (BC7), DCX_KRAK. New TPFs are added to the binder by listing them in `_witchy-bxf4.xml`; WitchyBND
rebuilds the `.tpfbhd` itself.

### Texture atlases (`menu/hi/01_common.tpf.dcx` + `menu/hi/01_common.sblytbnd.dcx`)

Small menu images live in atlases: a DDS in the TPF plus a `.layout` (XML `TextureAtlas`) of the same name in the
layout binder. Subtexture names end in `.png`; GFX files and the game refer to them without it. **Verified**:

- 41 stock layouts. Most give the atlas `width`/`height`; `SB_NamePlate` and `SB_PieceCategory` don't.
- Sheets are BC7_UNORM without mipmaps (55 of 62; the rest DXT1).
- Cells sit on a grid with a 4 px gap (128 px thumbnails at a 132 px pitch, 232x128 rank icons at 236x132), so every
  cell starts on a multiple of 4 and BC7's 4x4 blocks never mix two cells. (The guide describes this as a 2 px border
  per cell.)
- `imagePath` is the artists' source path (`W:\FNR\data\Menu\ScaleForm\Tif\01_Common\<group>\Hi\exp\<name>.png`).

### HP bar thumbnail (`SB_DecalThumbnails`)

128x128 subtexture `Decal_tmb_<emblemImageID:08>.png` (with `half="0"`, like the stock entries). The stock sheet is
2048x2048 with 160 thumbnails on a 15x15 grid, 65 cells free. ArenaTool added custom thumbnails to this sheet.

Unlike rank icons, the menus don't reference single thumbnails: seven GFX files (`01_000_fe`, `01_texteffect_hi`,
`02_acarena_preparing`, `02_acarena_select`, `02_decal_deleteimageselect`, `02_marking_imageselect`,
`02_npcarenaresult`) define the whole `SB_DecalThumbnails` sheet as one external image, and the game finds a
thumbnail by looking up `Decal_tmb_<emblemImageID:08>.png` in the layout. So custom thumbnails have to go into that
sheet; a separate atlas won't be found.

The sheet can grow. **Verified in game**: with the sheet grown to 2048x2108 and the GFX files untouched, a thumbnail
whose cell crosses the old 2048 px edge showed completely, both next to the HP bar and in the decal selection menu.
The target sizes the GFX files declare don't matter: they disagree with each other (2048x2048, 2048x1024, 1024x4096)
and with the real sheet.

### Emblem IDs and the player's decal list

Emblem IDs are shared with the player's decals: the arena emblems (e.g. 11 and 12, Nosaac's and Carla's) are also
selectable decal images. **Verified in game**:

- The player's preset image list is `PresetEmblemSpec`: one row per image, `PieceID` (u16) = emblem ID,
  `CategoryID` (u8) = tab (1 = PRESET 2; Carla and Nosaac are rows 1250 and 1270 there). Rows are listed in ID order.
- An emblem with a thumbnail but no `PresetEmblemSpec` row doesn't appear in the list. Adding a row (e.g. 1271,
  between stock rows 1270 and 1280) makes it appear in that spot.
- IDs below 10000 are game images (`Decal_tmb_<id>`). IDs from 10000 up are the player's own saved decals: 10000
  showed a decal the player had made, 16001 and 65535 showed blank slots, even with a `Decal_tmb_` thumbnail present.

The arena itself (intro emblem, HP bar thumbnail) looks emblems up by name whatever the ID: ArenaTool used the
account ID (16000 + 10 per fight) as the emblem ID and those showed fine (from the original tool). The 10000 limit
only matters for the player's decal list. Custom emblems that should be selectable by the player need IDs below 10000
that avoid the stock ones (151 IDs: mostly 1-3046, plus 9998 and 9999); 4000-9997 is free. `PresetEmblemSpec.PieceID`
is 16-bit, so list entries can't go above 65535 anyway.

### Rank icons

`ArenaParam.rankIconID` is a frame number in the rank icon sprite, which exists in four menu files:
`menu/01_texteffect_hi.gfx`, `menu/02_acarena_preparing.gfx`, `menu/02_acarena_select.gfx`,
`menu/02_npcarenaresult.gfx`. **Verified**, all four:

- Uncompressed Scaleform GFX v11 (SWF with a `GFX` signature).
- The sprite is the one exported as `*.ArenaRank_00000_*`: 1000 frames, frame N = rank icon N.
- Each rank frame is `RemoveObject2(depth 1)` + `PlaceObject3(image, depth 1)` with the same matrix
  (translate -116, -64 px).
- The images are `DefineExternalImage2` tags (code 1009): `u16 imageID, u16 idType (0 = imageID is a character ID),
  u16 bitmapFormat (13), u16 width (232), u16 height (128), u8-length exportName, u8-length fileName (".tga")`.
  The export name matches an atlas subtexture (`ArenaRank_00011` -> `ArenaRank_00011.png` in `SB_ArenaRank`).
- Stock frames used: 0-31 and 101-113; frame 113 shows `ArenaRank_00000d`, the blank icon, so higher ranks show
  nothing. After the last custom rank, put `ArenaRank_00000d` back the same way.

ArenaTool numbers custom ranks from 300 downward and puts them in their own atlas, `SB_CustomArenaRank`
(subtextures `CustomArenaRank_<rank:05>.png`), added to the same TPF and layout binder. This works in game (from the
original tool). `arena_maker/gfx.py` writes the sprite changes without JPEXS.

## Voice lines (`sd/enus/npc015.bnk`)

`npc015.bnk` is ALLMIND's bank and is loaded when the arena lines play (from the guide). Per line, **verified** on the
stock bank:

```
Event "Play_v<talkId>" ─► Action (Play) ─► Sound ─ child of an ActorMixer
Event "Stop_v<talkId>" ─► Action (Stop) ─► same Sound
```

- Wwise IDs are 32-bit FNV-1 hashes of the lowercased name (`Play_v600310100` = 1326246027). ArenaTool names its
  objects `Sound_v<id>`, `Play_Action_v<id>`, `Stop_Action_v<id>`, and uses the talk ID itself as the media
  (source) ID, i.e. the audio file is `<talkId>.wem`.
- Media IDs must stay small: every stock one is below 2^30, and in game a streamed source with an ID above 2^31 is
  never requested at all (**verified**: hashed source IDs like 2731632413 stayed silent while 494648092 played).
- ActorMixer child lists are kept sorted ascending.
- 38 accounts have arena lines in the bank. 37 have all five; Carla (account 310) only has the 1st intro and 2nd outro
  line. Nosaac (account 160, ArenaParam 103) has all five, so it's a good fight for testing.
- Stock lines are Vorbis. The stock arena intros are `PrefetchStreaming` (start embedded in the bank, full file loose
  in `sd/enus/<sourceId>.wem`); the outros and the regular voice lines are `Streaming` (nothing in the bank).

**Verified in game** through ME3 (Nosaac's fight): custom lines work as `Streaming` PCM sounds with
`in_memory_media_size = 56` (the PCM header, up to the `data` chunk; 0 also works, the full file size cuts the line
short) and `source_flags = 0`, with the audio at `sd/wem/<sourceId>.wem` in the mod. With `source_flags = 1`
(language-specific) the game also looks in `sd/<language>/`, so 0 serves every voice language. The bank stays its
original size; embedding PCM instead grows it by about 5 MB per minute of audio.

PCM `.wem`: RIFF/WAVE, `fmt ` tag `0xFFFE`, 24-byte fmt chunk ending in the Wwise channel config `0x3102` (2 channels,
standard, front L+R), a 4-byte `JUNK` chunk, then 16-bit samples. Stereo only: mono input has to be duplicated to
two channels (the old converter wrote a stereo channel config into mono files).

## Music (`sd/init.bnk`, `sd/cs_smain.bnk`)

All music is in `cs_smain.bnk` (not `cs_main`). Everything below is **verified in game** (2026-10-29) unless noted.

```
ArenaParam.bgmId (e.g. 21000)
  ─► Wwise game parameter BGM_ID = 21000.0
  ─► init.bnk STMG: switch group BGM_ID (3012934567 = fnv("BGM_ID")) is driven by that parameter through a table of
     points (rtpc_value ─► switch value), constant curve: a value between points snaps to a neighbouring point
  ─► cs_smain.bnk MusicSwitchContainer 945903041, decision tree over 6 groups:
       State 3898567437 / Switch BGM_ID / State 2176308960 (phase: normal, in_combat, heat_up_1-5, death) /
       State 969773702 / State 2354612607 / State 3568898208      ("*" = any value; BestMatch)
  ─► playlist (MusicRandomSequenceContainer) ─► segments (MusicSegment) ─► MusicTrack ─► streamed .wem
```

- **The table** has 67 points: 0-9, 9000, the 60 numbers with arena music (12000-13010, 21000-24300, 33000,
  40000-43000, 50000-50030, 60000-60010, 90001), plus 21210, 50010, 60020, 90000, 90002 (no arena music) and
  100000 ─► none. Nothing lies between 60020 and 90000. A number that isn't a point snaps to a neighbour: 77700 played
  60020's (silent) entry until it got its own point.
- **Switch values** are FNV-1 of an unknown prefix + the number. Every stock value continues the hash from the same
  state, 1870080928, so the value for any number can be computed without the prefix (`soundbank.bgm_switch_value`).
- **Unknown switch values** hit the tree's catch-all, a silent 4.9 s segment.
- **Stock songs** are one long Vorbis .wem cut into an intro segment (played once) and a loop segment (forever) in
  a playlist; e.g. 21000 "Analysis" = playlist 409791442 (segments 619349637 then 684054416, both from wem
  798507079). 50000, the default arena music, is "Cinder" Carla's "Rough and Decent" (wem 209111615).
- **Death**: most numbers route `death` to a silent 4.9 s segment (933200949 or 1070742183), so the music stops; a few
  (e.g. 50000) have a real piece played once.
- **21xxx is special-cased by the game**: new numbers 21004, 21005 and 21012 played mission music (wem 374197011 from
  the mission switch 375664304, which switches on map areas and mission states) even with chart entries and a
  rerouted catch-all. An exe function maps 21000-21011 to small values, but 21012 behaves the same, so the cause is
  still open. Custom numbers stay out of this range.

**Custom music** (`build/steps/music.py`, `soundbank.MusicAdder`), per fight with a slot:

- bgmId `70000 + slot`, added as a table point in `init.bnk` (points kept sorted, `graph_point_count` updated).
- A branch `* / BGM_ID=<bgmId> / {*: playlist, death: silent segment / custom playlist / none} / * / * / *` in
  945903041's tree. Every level is sorted by key; nodes are 12 bytes (`tree_size` = nodes × 12) and stored as "a
  node's children contiguously, then each child's subtree in order", which reproduces the stock layout exactly
  (bnk2json recalculates counts but not `first_child_index`). New playlists are added to 945903041's sorted child
  list.
- Track/segment/playlist objects cloned from "Analysis"'s loop part, inserted before 945903041 (children before
  parents). Intro segment = track trimmed to [0, loopStart], loop segment = [loopStart, loopEnd] (`play_at =
  -begin_trim`, like the stock trimmed tracks), exit markers at each segment's end; playlist items loop once (1) or
  forever (0). A custom death piece is its own playlist with the group and item looping once, like Carla's.
- New object IDs are hashed names masked below 2^31: bnk2json reads some ID fields (`playlist_item_id`) as i32.
- Audio: streamed, `source_flags` 0, at `sd/wem/<id>.wem`, IDs `1100000000 + 10 × slot (+1 for death)`: every stock
  .wem ID is below 2^30, the game streams IDs up to 2^31, so this range can't clash with stock audio (lower ranges
  can: stock `800028120.wem` exists).

**Wwise IMA ADPCM** (`audio.adpcm_wem`), about 4× smaller than PCM: `fmt ` tag `0x0002`, 24-byte fmt chunk (block
align 0x24 × channels, 4 bits per sample, cbSize 6, 64 samples per block, channel config), then per channel 0x24-byte
blocks, channel-interleaved: s16 first sample, s8 step index, a reserved byte, 32 bytes of nibbles (low nibble first)
= 64 samples, the last nibble unused (vgmstream's `decode_wwise_ima`). Bank source plugin `ADPCM`,
`in_memory_media_size` = header size (44). Every stock .wem is Vorbis, but this Wwise version plays IMA ADPCM. Wwise's
own Vorbis variant (stripped headers, codebooks referenced from a built-in table) would need a bit-level reencoder.

## Tools and their quirks

| Tool | Version | Used for | Notes |
|---|---|---|---|
| WitchyBND | 3.0.1.0 | params, FMGs, BNDs, TPFs | See below. |
| rewwise bnk2json | 0.3.2 | soundbanks | Reads `dictionary.txt` from the working directory and then ignores its built-in names. Errors are panics (exit 101). Recalculates sizes/counts on repack, not real values like `in_memory_media_size`. |
| texconv | 2024.6.5.1 | PNG <-> DDS | `-f BC7_UNORM -m 1` matches the stock textures (texconv makes full mip chains by default). |
| ME3 | 0.13.0 | loading the mod | Packages mirror the game layout. Its Wwise hook serves `.bnk` and `.wem` overrides on AC6 (log: `assets:wwise: applied asset override hook`; hits are logged as `override=<path>`). |

WitchyBND 3.0.1 with AC6, **verified**:

- It refuses to repack a regulation newer than `Assets/Paramdex/AC6/Upgrader/version.txt` (`1_07_2_0018L`). The
  defs still match 1.09.1, so raising that file to the regulation's version is enough.
- The 1.07 defs are out of date in places: a full XML round trip clears flag bits in every `ThrustersParam_NPC` row.
  Only convert the params you edit; leave the rest as binary `.param` files.
- `ParamDefaultValueThreshold: 0` breaks repacking for 78 of 257 params. At the default 0.8, param XML has a
  `<defaults>` section and rows leave out fields that match it.
- New TPF manifests need `WitchyVersion="2170000"` on the root element.
- It prints nothing when its output is captured, and exits 0 on files it doesn't recognize; check outputs instead.
- User settings in `%APPDATA%\WitchyBND\appsettings.user.json` apply unless overridden by
  `appsettings.override.json` next to the exe.
- Oodle level 9 (the stock level) takes ~50 s for `01_common.tpf.dcx`; level 4 takes ~1.5 s for a ~3% bigger file.

Reading game files without UXM: the `Data0-3.bdt`/`sd/sd.bdt` archives can be read directly (see
`arena_maker/game_archives.py`). Their `.bhd` indexes are RSA-encrypted with known public keys; AC6 uses the 32-bit
BHD5 layout with 64-bit path hashes (`hash = hash * 0x85 + char` over the lowercased path with a leading `/`); files
in `sd.bdt` are hashed relative to `sd/`. `regulation.bin` is a loose file. `sd/sd.bdt` and `sd/sd.bhd` are also
loose files in the game folder: don't delete them when cleaning up an unpack.

## Saves

Arena progress is stored per ArenaParam ID. In the decrypted save, `USER_DATA000` has an `NpcArena` chunk (version 0)
whose body is `int count; int arenaIds[count]`: the IDs of the cleared fights (**verified**: a save with every stock
fight cleared lists exactly 100-128 and 200-211). See `010-templates/Formats/SL2/USER_DATA000.bt` in AC6_tools.

So a custom fight's clear status follows its ArenaParam ID: if fights get renumbered (e.g. by reordering), clears
move to whichever fight now has that ID. Since a tab is also ordered by ArenaParam ID, ArenaTool numbers fights by
list position (reordering works, a clear stays with its position) and ties all their other IDs to the fight itself.

## Open questions

- Custom BGM.
