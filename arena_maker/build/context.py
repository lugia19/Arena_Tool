"""Shared state of one build: where game files come from, the tools, and everything unpacked so far.

Steps ask the context for params, text files and unpacked binders; it unpacks each game file once into the work
folder (mirroring the game's layout) and repacks everything that was touched in finish().
"""
import os
from typing import Dict, Iterable, List, Tuple

from .. import tools
from ..atlas import Texconv
from ..fmg import FmgXml
from ..game_archives import GameArchives
from ..package import PackageBuilder
from ..params import ParamXml
from ..soundbank import Bnk2Json
from ..witchy import Witchy


class BuildContext:
    def __init__(self, game_dir: str, work_dir: str, sources: Iterable[str] = ()):
        self.game_dir = game_dir
        self.work_dir = work_dir
        self.sources = list(sources)  # Other mods' package folders, read before the game
        self.archives = GameArchives(game_dir)
        self.witchy = Witchy(tools.WITCHYBND, game_dir)
        self.bnk2json = Bnk2Json(tools.BNK2JSON)
        self.texconv = Texconv(tools.TEXCONV)
        self._unpacked: Dict[str, Tuple[str, bool]] = {}  # game path -> (unpacked folder, recursive)
        self._params: Dict[str, ParamXml] = {}
        self._fmgs: List[FmgXml] = []
        self._files: Dict[str, bytes] = {}  # Extra package files: game path -> content

    # region Reading game files
    def _source_path(self, game_path: str):
        for source in self.sources:
            path = os.path.join(source, game_path)
            if os.path.isfile(path):
                return path
        if game_path == "regulation.bin":  # The only file that isn't in the archives
            return os.path.join(self.game_dir, game_path)
        return None

    def exists(self, game_path: str) -> bool:
        return self._source_path(game_path) is not None or self.archives.exists(game_path)

    def read(self, game_path: str) -> bytes:
        path = self._source_path(game_path)
        if path:
            with open(path, "rb") as f:
                return f.read()
        return self.archives.read(game_path)

    def work_path(self, game_path: str) -> str:
        return os.path.join(self.work_dir, *game_path.split("/"))

    def extract(self, game_path: str) -> str:
        path = self.work_path(game_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.read(game_path))
        return path
    # endregion

    # region Things steps edit
    def unpacked(self, game_path: str, recursive: bool = False) -> str:
        """The unpacked folder of a game binder, unpacked on first use. Repacked in finish()."""
        if game_path not in self._unpacked:
            path = self.extract(game_path)
            if game_path.endswith(".tpfbdt"):  # Split binder: WitchyBND needs the header next to it
                self.extract(game_path[:-3] + "bhd")
            self.witchy.unpack(path, recursive=recursive)
            folder = os.path.join(os.path.dirname(path), os.path.basename(path).replace(".", "-"))
            self._unpacked[game_path] = (folder, recursive)
        return self._unpacked[game_path][0]

    def param(self, name: str) -> ParamXml:
        """A regulation param as editable XML (only params asked for get converted, see witchy.py)."""
        if name not in self._params:
            if "regulation.bin" not in self._unpacked:
                path = self.extract("regulation.bin")
                self.witchy.unpack(path)
                self._unpacked["regulation.bin"] = (os.path.join(self.work_dir, "regulation-bin"), False)
            folder = self._unpacked["regulation.bin"][0]
            self.witchy.unpack(os.path.join(folder, name + ".param"))
            self._params[name] = ParamXml(os.path.join(folder, name + ".param.xml"))
        return self._params[name]

    def fmg(self, msgbnd_path: str, fmg_name: str) -> FmgXml:
        """A text file inside a msgbnd (e.g. "msg/engus/menu.msgbnd.dcx", "会話") as editable XML."""
        path = os.path.join(self.unpacked(msgbnd_path, recursive=True), fmg_name + ".fmg.xml")
        for fmg in self._fmgs:
            if fmg.path == path:
                return fmg
        fmg = FmgXml(path)
        self._fmgs.append(fmg)
        return fmg

    def add_file(self, game_path: str, data: bytes):
        """A file that goes into the package as-is (e.g. a loose .wem or an edited .gfx)."""
        self._files[game_path] = data
    # endregion

    def finish(self, package: PackageBuilder):
        """Saves and repacks everything that was edited and puts the results in the package."""
        for fmg in self._fmgs:
            fmg.save()
        if self._params:
            for param in self._params.values():
                param.save()
            self.witchy.repack(*[param.path for param in self._params.values()])
        for game_path, (folder, recursive) in self._unpacked.items():
            self.witchy.repack(folder, recursive=recursive)
            package.copy(game_path, self.work_path(game_path))
            if game_path.endswith(".tpfbdt"):
                package.copy(game_path[:-3] + "bhd", self.work_path(game_path[:-3] + "bhd"))
        for game_path, data in self._files.items():
            package.write(game_path, data)
