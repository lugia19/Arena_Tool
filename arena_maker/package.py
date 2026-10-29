"""ME3 output: building a package folder (game-relative file layout) and the .me3 profile that loads it.

A package mirrors the game's file layout (regulation.bin, msg/engus/..., menu/hi/..., sd/enus/..., sd/wem/...);
ME3 serves any file in it instead of the game's own. Only final files go in: no unpacked folders or manifests.
"""
import os
import shutil
import subprocess
from typing import Iterable, List, Optional, Tuple

ME3_GAME = "armoredcore6"


class PackageBuilder:
    """Builds a package in a staging folder and only replaces the real one if the build succeeds:

        with PackageBuilder(packages_dir, "CustomArena") as package:
            package.write("regulation.bin", data)
            package.copy("menu/hi/01_common.tpf.dcx", built_file)
    """

    def __init__(self, packages_dir: str, name: str, keep_failed: bool = False):
        self.final_dir = os.path.join(packages_dir, name)
        self.staging_dir = self.final_dir + ".staging"
        self.keep_failed = keep_failed  # Leave the staging folder behind on failure, for debugging.

    def __enter__(self) -> "PackageBuilder":
        shutil.rmtree(self.staging_dir, ignore_errors=True)
        os.makedirs(self.staging_dir)
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            if not self.keep_failed:
                shutil.rmtree(self.staging_dir, ignore_errors=True)
            return False
        old_dir = self.final_dir + ".old"
        shutil.rmtree(old_dir, ignore_errors=True)
        if os.path.exists(self.final_dir):
            os.rename(self.final_dir, old_dir)
        os.rename(self.staging_dir, self.final_dir)
        shutil.rmtree(old_dir, ignore_errors=True)
        return False

    def path(self, relative_path: str) -> str:
        """Absolute path for a game-relative path inside the package (parent folders are created)."""
        relative_path = relative_path.replace("\\", "/").lstrip("/")
        if ".." in relative_path.split("/"):
            raise ValueError(f"Package paths must stay inside the package: {relative_path}")
        full = os.path.join(self.staging_dir, *relative_path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        return full

    def write(self, relative_path: str, data: bytes):
        with open(self.path(relative_path), "wb") as f:
            f.write(data)

    def copy(self, relative_path: str, source: str):
        shutil.copy2(source, self.path(relative_path))

    def files(self) -> List[str]:
        """Game-relative paths of everything in the package so far."""
        found = []
        for root, _, names in os.walk(self.staging_dir):
            found += [os.path.relpath(os.path.join(root, n), self.staging_dir).replace("\\", "/") for n in names]
        return sorted(found)


def _toml_string(value: str) -> str:
    # Literal strings (single quotes) avoid having to escape Windows backslashes, as ME3's own docs do.
    if "'" in value or "\n" in value:
        raise ValueError(f"Can't write {value!r} as a TOML literal string")
    return f"'{value}'"


def write_profile(profile_path: str, packages: Iterable[Tuple[str, str]], natives: Iterable[str] = (),
                  savefile: Optional[str] = None):
    """Writes an ME3 profile. packages: (id, folder) in load order; natives: DLL paths.
    Paths inside the profile's folder are written relative to it (ME3 resolves them from there), others absolute."""
    profile_dir = os.path.dirname(os.path.abspath(profile_path))

    def relative(path: str) -> str:
        path = os.path.abspath(path)
        try:
            inside = os.path.commonpath([path, profile_dir]) == profile_dir
        except ValueError:  # Different drive
            inside = False
        return os.path.relpath(path, profile_dir) if inside else path

    lines = ['profileVersion = "v1"', ""]
    if savefile:
        lines += [f"savefile = {_toml_string(savefile)}", ""]
    lines += ["[[supports]]", f'game = "{ME3_GAME}"', ""]
    for package_id, folder in packages:
        lines += ["[[packages]]", f"id = {_toml_string(package_id)}", f"path = {_toml_string(relative(folder))}", ""]
    for native in natives:
        lines += ["[[natives]]", f"path = {_toml_string(relative(native))}", ""]
    os.makedirs(profile_dir, exist_ok=True)
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def launch(me3_exe: str, profile_path: str) -> subprocess.Popen:
    """Starts the game through ME3 with the given profile (EAC-free)."""
    return subprocess.Popen([me3_exe, "launch", "-p", os.path.abspath(profile_path)],
                            cwd=os.path.dirname(os.path.abspath(me3_exe)))
