"""Soundbank editing through a pinned rewwise bnk2json (v0.3.2), plus adding voice lines to a bank.

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
from typing import Dict, Optional, Union

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
                                    text=True, encoding="utf-8", errors="replace")
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
    plus the matching Stop event/action. The audio is streamed from a loose sd/wem/<fnv("Source_v<id>")>.wem rather
    than embedded, so the bank doesn't grow with every line (PCM is ~5 MB/min, and Wwise keeps whole banks in memory).

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
        source_id = fnv_hash(f"Source_v{talk_id}")

        sound = self.bank._ensure(f"Sound_v{talk_id}", self.sound)
        source = sound["body"]["Sound"]["bank_source_data"]
        source["plugin"] = "PCM"
        source["source_type"] = "Streaming"
        source["media_information"]["source_id"] = source_id
        source["media_information"]["in_memory_media_size"] = pcm_wem_header_size(wem)
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


def pcm_wem_header_size(wem: bytes) -> int:
    """Offset of the "data" chunk in a RIFF .wem: 56 for the files audio.pcm_wem writes, the value tested in game."""
    offset = 12
    while offset + 8 <= len(wem):
        chunk_id, size = wem[offset:offset + 4], struct.unpack_from("<I", wem, offset + 4)[0]
        if chunk_id == b"data":
            return offset
        offset += 8 + size + (size & 1)
    raise ValueError("No data chunk in wem")
