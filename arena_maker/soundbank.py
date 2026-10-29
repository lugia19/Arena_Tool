"""Soundbank editing through a pinned rewwise bnk2json (v0.3.2), plus adding voice lines and arena music.

bnk2json quirks worth knowing:
- It reads dictionary.txt from the *working directory* and, if present, uses it instead of its built-in name
  dictionary, so we always run it from an empty temporary directory.
- Every error is a panic (exit code 101) with no other signal.
- Sizes and counts in soundbank.json are recalculated on repack; real values (like in_memory_media_size) aren't.
"""
import copy
import hashlib
import json
import os
import struct
import subprocess
import tempfile
from typing import Dict, List, Optional, Union

from .audio import fnv_hash

BNK2JSON_VERSION = "0.3.2"
BNK2JSON_SHA256 = "033fb979b93ad46b9d1607a0b53a293113851b4c1e7048c08772c3d283fb4eaf"


class Bnk2JsonError(RuntimeError):
    pass


class Bnk2Json:
    def __init__(self, exe_path: str):
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"bnk2json not found at {exe_path}")
        with open(exe_path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest != BNK2JSON_SHA256:
            raise Bnk2JsonError(f"{exe_path} is not rewwise bnk2json {BNK2JSON_VERSION}")
        self.exe_path = exe_path

    def _run(self, path: str):
        with tempfile.TemporaryDirectory() as clean_dir:
            result = subprocess.run([self.exe_path, os.path.abspath(path)], cwd=clean_dir, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace",
                                    creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            raise Bnk2JsonError(f"bnk2json failed (exit {result.returncode}) on {path}" + (f"\n{output}" if output else ""))

    def unpack(self, bnk_path: str) -> str:
        """foo.bnk -> foo/ (soundbank.json + <id>.wem files). Returns the folder."""
        folder = os.path.splitext(os.path.abspath(bnk_path))[0]
        self._run(bnk_path)
        if not os.path.exists(os.path.join(folder, "soundbank.json")):
            raise Bnk2JsonError(f"bnk2json produced no soundbank.json for {bnk_path}")
        return folder

    def repack(self, folder: str) -> str:
        """foo/ -> foo.created.bnk. Returns the created file."""
        created = os.path.abspath(folder).rstrip("\\/") + ".created.bnk"
        if os.path.exists(created):
            os.remove(created)
        self._run(folder)
        if not os.path.exists(created):
            raise Bnk2JsonError(f"bnk2json produced no bank for {folder}")
        return created


def object_hash(object_id: Dict) -> int:
    """HIRC object ids are either {"Hash": n} or, when bnk2json's dictionary knows the name, {"String": name}."""
    return object_id["Hash"] if "Hash" in object_id else fnv_hash(object_id["String"])


class Soundbank:
    """An unpacked soundbank folder (soundbank.json + wems)."""

    def __init__(self, folder: str):
        self.folder = folder
        with open(os.path.join(folder, "soundbank.json"), encoding="utf-8") as f:
            self.data = json.load(f)
        hirc = next(s["body"]["HIRC"] for s in self.data["sections"] if "HIRC" in s["body"])
        self.objects = hirc["objects"]
        self._by_hash = {object_hash(o["id"]): o for o in self.objects}

    def get(self, name_or_hash: Union[str, int]) -> Optional[Dict]:
        return self._by_hash.get(fnv_hash(name_or_hash) if isinstance(name_or_hash, str) else name_or_hash)

    def _insert_before(self, new_object: Dict, anchor: Dict):
        self.objects.insert(self.objects.index(anchor), new_object)
        self._by_hash[object_hash(new_object["id"])] = new_object

    def _ensure(self, name: str, template: Dict, as_string: bool = False) -> Dict:
        existing = self.get(name)
        if existing is not None:
            return existing
        new_object = copy.deepcopy(template)
        new_object["id"] = {"String": name} if as_string else {"Hash": fnv_hash(name)}
        self._insert_before(new_object, template)
        return new_object

    def save(self):
        with open(os.path.join(self.folder, "soundbank.json"), "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


class VoiceLineAdder:
    """Adds talk voice lines (Play_v<talkId>/Stop_v<talkId> events) to a bank, cloned from an existing line.

    Per line: Event Play_v<id> -> Action Play_Action_v<id> -> Sound Sound_v<id> (child of the template's ActorMixer),
    plus the matching Stop event/action. The audio is streamed from a loose sd/wem/<talkId>.wem rather than embedded,
    so the bank doesn't grow with every line (PCM is ~5 MB/min, and Wwise keeps whole banks in memory).

    The talk ID doubles as the media (source) ID. Every stock media ID is below 2^30, and in game a streamed source
    with an ID above 2^31 is never requested (tested 2026-10-29: hashed IDs like 2731632413 stayed silent).

    Tested in game through ME3 (2026-10-29): Streaming + PCM plays fully with in_memory_media_size set to the PCM
    header size (or 0); the full file size cuts playback short. With source_flags 0 (not language-specific) ME3 serves
    the file from sd/wem/<id>.wem for every voice language; with 1 the game also looks in sd/<language>/.
    """

    def __init__(self, bank: Soundbank, template_talk_id: int):
        self.bank = bank
        self.play_event = self._require(f"Play_v{template_talk_id}")
        self.stop_event = self._require(f"Stop_v{template_talk_id}")
        self.play_action = self._require(self.play_event["body"]["Event"]["actions"][0])
        self.stop_action = self._require(self.stop_event["body"]["Event"]["actions"][0])
        self.sound = self._require(self.play_action["body"]["Action"]["external_id"])
        self.mixer = self._require(self.sound["body"]["Sound"]["node_base_params"]["direct_parent_id"])

    def _require(self, name_or_hash):
        found = self.bank.get(name_or_hash)
        if found is None:
            raise KeyError(f"{name_or_hash} not found in soundbank {self.bank.folder}")
        return found

    def add(self, talk_id: int, wem: bytes) -> str:
        """Adds or replaces the line. Returns the package-relative path the wem must be written to."""
        source_id = talk_id

        sound = self.bank._ensure(f"Sound_v{talk_id}", self.sound)
        source = sound["body"]["Sound"]["bank_source_data"]
        source["plugin"] = "PCM"
        source["source_type"] = "Streaming"
        source["media_information"]["source_id"] = source_id
        source["media_information"]["in_memory_media_size"] = wem_header_size(wem)
        source["media_information"]["source_flags"] = 0
        sound_hash = object_hash(sound["id"])

        children = self.mixer["body"]["ActorMixer"]["children"]["items"]
        if sound_hash not in children:
            children.append(sound_hash)
            children.sort()  # Wwise keeps child id lists in ascending order.

        for prefix, event_template, action_template in (("Play", self.play_event, self.play_action),
                                                         ("Stop", self.stop_event, self.stop_action)):
            action = self.bank._ensure(f"{prefix}_Action_v{talk_id}", action_template)
            action["body"]["Action"]["external_id"] = sound_hash
            event = self.bank._ensure(f"{prefix}_v{talk_id}", event_template, as_string=True)
            event["body"]["Event"]["actions"] = [object_hash(action["id"])]
        return f"sd/wem/{source_id}.wem"


def wem_header_size(wem: bytes) -> int:
    """Offset of the "data" chunk in a RIFF .wem (56 for audio.pcm_wem, 44 for audio.adpcm_wem): the in-memory size
    that lets a streamed source play in full (tested in game for both)."""
    offset = 12
    while offset + 8 <= len(wem):
        chunk_id, size = wem[offset:offset + 4], struct.unpack_from("<I", wem, offset + 4)[0]
        if chunk_id == b"data":
            return offset
        offset += 8 + size + (size & 1)
    raise ValueError("No data chunk in wem")


# region Arena music
# ArenaParam.bgmId reaches Wwise as the game parameter BGM_ID. init.bnk maps it through a table of points to a value
# of the switch group BGM_ID, and cs_smain.bnk's arena music switch picks a playlist from that value and the fight
# phase. Unknown numbers snap to a neighbouring table point. See docs/arena_format.md (Music).
BGM_ID_GROUP = 3012934567           # fnv_hash("BGM_ID"): the switch group, driven by the game parameter of the same ID
BGM_KEY_PREFIX_STATE = 1870080928   # FNV-1 state after the (unknown) prefix of every BGM_ID switch value
ARENA_BGM_SWITCH = 945903041        # MusicSwitchContainer: * / BGM_ID / phase / * / * / *
TEMPLATE_TRACK, TEMPLATE_SEGMENT, TEMPLATE_PLAYLIST = 60422897, 684054416, 409791442  # "Analysis" (21000)'s loop
SILENT_DEATH_SEGMENT = 933200949    # 4.9 s of silence: most stock songs stop when the player dies
DEATH_PHASE = fnv_hash("death")


def bgm_switch_value(number: int) -> int:
    """The BGM_ID switch value for a bgmId: FNV-1 of <prefix> + the number, continued from the prefix's state."""
    value = BGM_KEY_PREFIX_STATE
    for byte in str(number).encode():
        value = ((value * 16777619) & 0xFFFFFFFF) ^ byte
    return value


def add_bgm_points(init_bank: Soundbank, numbers: List[int]):
    """Adds BGM_ID table points (number -> its switch value) to init.bnk, keeping the table sorted."""
    stmg = next(s["body"]["STMG"] for s in init_bank.data["sections"] if "STMG" in s["body"])
    group = next(g for g in stmg["switch_groups"] if g["id"] == BGM_ID_GROUP)
    points = [p for p in group["graph_points"] if p["rtpc_value"] not in {float(n) for n in numbers}]
    points += [{"rtpc_value": float(n), "switch": bgm_switch_value(n), "curve_shape": 9} for n in numbers]
    group["graph_points"] = sorted(points, key=lambda p: p["rtpc_value"])
    group["graph_point_count"] = len(points)


class MusicAdder:
    """Adds songs to cs_smain.bnk's arena music switch, cloned from the stock "Analysis" objects.

    Per song: an intro segment (played once) and a loop segment (forever), both trimmed from the same streamed .wem,
    in one playlist; optionally a death playlist (a segment played once). Tested in game (2026-10-29), ADPCM and PCM.
    """

    def __init__(self, bank: Soundbank):
        self.bank = bank
        self.switch = bank.get(ARENA_BGM_SWITCH)["body"]["MusicSwitchContainer"]
        self.templates = [bank.get(i) for i in (TEMPLATE_TRACK, TEMPLATE_SEGMENT, TEMPLATE_PLAYLIST)]
        self.new_objects = []

    def _id(self, name: str) -> int:
        value = fnv_hash(f"ArenaMaker_bgm_{name}") & 0x7FFFFFFF  # bnk2json reads some ID fields as i32
        if self.bank.get(value) is not None:
            raise ValueError(f"Soundbank object ID {value} ({name}) is already taken")
        return value

    def _segment(self, name: str, wem: bytes, wem_id: int, duration_ms: float, start_ms: float, end_ms: float,
                 playlist_id: int) -> int:
        track, segment = copy.deepcopy(self.templates[0]), copy.deepcopy(self.templates[1])
        track_id, segment_id = self._id(f"track_{name}"), self._id(f"segment_{name}")

        track["id"] = {"Hash": track_id}
        body = track["body"]["MusicTrack"]
        source = body["sources"][0]
        source["plugin"] = "ADPCM" if struct.unpack_from("<H", wem, 20)[0] == 0x0002 else "PCM"  # fmt tag
        source["source_type"] = "Streaming"
        source["media_information"] = {"source_id": wem_id, "in_memory_media_size": wem_header_size(wem),
                                       "source_flags": 0}
        body["playlist"] = [{"track_id": 0, "source_id": wem_id, "event_id": 0, "play_at": -start_ms,
                             "begin_trim_offset": start_ms, "end_trim_offset": end_ms - duration_ms,
                             "source_duration": duration_ms}]  # Same layout as the stock trimmed tracks
        body["playlist_item_count"] = 1
        body["clip_items"], body["clip_item_count"] = [], 0  # No fades
        body["node_base_params"]["direct_parent_id"] = segment_id

        segment["id"] = {"Hash": segment_id}
        body = segment["body"]["MusicSegment"]
        body["duration"] = end_ms - start_ms
        entry, exit_marker = copy.deepcopy(body["markers"][0]), copy.deepcopy(body["markers"][-1])
        entry["position"], exit_marker["position"] = 0.0, end_ms - start_ms  # Playlists move on at the exit marker
        body["markers"], body["marker_count"] = [entry, exit_marker], 2
        params = body["music_node_params"]
        params["children"] = {"count": 1, "items": [track_id]}
        params["node_base_params"]["direct_parent_id"] = playlist_id
        self.new_objects += [track, segment]
        return segment_id

    def _playlist(self, name: str, parts: List[tuple], group_loops: int) -> int:
        """parts: (segment name, wem, wem ID, duration, start, end, loops); loops 0 = forever, 1 = once."""
        playlist = copy.deepcopy(self.templates[2])
        playlist_id = self._id(f"playlist_{name}")
        playlist["id"] = {"Hash": playlist_id}
        body = playlist["body"]["MusicRandomSequenceContainer"]
        template_group, template_item = body["playlist_items"][0], body["playlist_items"][-1]
        items = [dict(copy.deepcopy(template_group), playlist_item_id=self._id(f"group_{name}"),
                      child_count=len(parts), loop_base=group_loops)]
        segment_ids = []
        for part_name, wem, wem_id, duration_ms, start_ms, end_ms, loops in parts:
            segment_id = self._segment(part_name, wem, wem_id, duration_ms, start_ms, end_ms, playlist_id)
            segment_ids.append(segment_id)
            items.append(dict(copy.deepcopy(template_item), segment_id=segment_id,
                              playlist_item_id=self._id(f"item_{part_name}"), loop_base=loops))
        body["playlist_items"], body["playlist_item_count"] = items, len(items)
        params = body["music_trans_node_params"]["music_node_params"]
        params["children"] = {"count": len(segment_ids), "items": sorted(segment_ids)}
        params["node_base_params"]["direct_parent_id"] = ARENA_BGM_SWITCH
        self.new_objects.append(playlist)
        return playlist_id

    def add(self, bgm: int, wem: bytes, wem_id: int, duration_ms: float, loop_start_ms: float, loop_end_ms: float,
            death=None):
        """death: None = the music stops (stock silence), "keep" = it keeps playing, or (wem, wem ID, duration).
        New object IDs are hashed from the bgmId, so they're stable per fight."""
        parts = [(f"intro_{bgm}", wem, wem_id, duration_ms, 0.0, loop_start_ms, 1)] if loop_start_ms > 0 else []
        parts.append((f"loop_{bgm}", wem, wem_id, duration_ms, loop_start_ms, loop_end_ms, 0))
        phases = [(0, self._playlist(f"{bgm}", parts, 0))]
        new_playlists = [phases[0][1]]
        if death is None:
            phases.append((DEATH_PHASE, SILENT_DEATH_SEGMENT))
        elif death != "keep":
            death_wem, death_wem_id, death_ms = death
            new_playlists.append(self._playlist(f"death_{bgm}", [
                (f"death_{bgm}", death_wem, death_wem_id, death_ms, 0.0, death_ms, 1)], 1))
            phases.append((DEATH_PHASE, new_playlists[-1]))

        def node(key, children=(), node_id=0):
            return {"key": key, "node_id": node_id, "first_child_index": 0, "child_count": 0, "weight": 50,
                    "probability": 100, "children": list(children)}

        # * / BGM_ID=bgm / phase / * / * / * -> target (every tree level is sorted by key)
        branch = node(bgm_switch_value(bgm), [node(key, [node(0, [node(0, [node(0, node_id=target)])])])
                                             for key, target in sorted(phases)])
        siblings = self.switch["tree"]["children"][0]["children"]
        siblings[:] = sorted([c for c in siblings if c["key"] != branch["key"]] + [branch], key=lambda c: c["key"])
        children = self.switch["music_trans_node_params"]["music_node_params"]["children"]
        children["items"] = sorted(set(children["items"]) | set(new_playlists))
        children["count"] = len(children["items"])

    def save(self):
        switch_object = self.bank.get(ARENA_BGM_SWITCH)
        index = self.bank.objects.index(switch_object)
        self.bank.objects[index:index] = self.new_objects  # Children before parents, as in the stock bank
        self.switch["tree_size"] = _layout_tree(self.switch["tree"]) * 12
        self.bank.save()


def _layout_tree(root: Dict) -> int:
    """Sets first_child_index/child_count the way Wwise stores the tree: a node's children are contiguous, followed
    by each child's subtree in order (reproduces the stock layout exactly). Returns the node count."""
    next_index = 1

    def place(node):
        nonlocal next_index
        if node.get("children"):
            node["first_child_index"], node["child_count"] = next_index, len(node["children"])
            next_index += len(node["children"])
            for child in node["children"]:
                place(child)

    place(root)
    return next_index
# endregion
