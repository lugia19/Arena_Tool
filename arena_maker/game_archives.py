"""Read individual files straight out of AC6's Data*.bdt / sd.bdt archives, without a UXM unpack.

Format reference: SoulsFormats BHD5.cs (Elden Ring/AC6 variant) and UXM Selective Unpack.
- *.bhd is RSA-"encrypted" (raw RSA with a public key, 256 byte blocks -> 255 byte blocks), then a BHD5 header.
- Files are looked up by a 64-bit hash of their lowercased path.
- File data in *.bdt may have AES-128-ECB encrypted ranges.
"""
import os
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Public keys from UXM Selective Unpack (ArchiveKeys.ArmoredCore6Keys).
ARCHIVE_KEYS = {
    "Data0": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEA7F43Ss9kroawBSUW6GBhSUo6GtxYtUV8zCPkcHhSJLGPASHhwsaX
zMRrd+Ul9qB3oYchb4xYtdMWKFe0/ZDi9vgYXvF3rlWaZKAu1k/F6RwVAd//I3Kj
JsYlhayskInKqB3BvB/KL2Ga8QBsZ/G9cLlUYsqIj3as9oqbfEXVmGVeuhg0I+NQ
NL+2sThqp5eOQstfXQgqduOt0ixd/r9e5VjLhyj2z4hCEF2TVsDw9wGEBem1TkcO
C/E8obl9fTHwEK7l2i8a4HafY7flU220r8y4UwQ+9Aq94xUYT2xdcTjdyBIaZtyS
YmR86B680OyL9oiEonEFhh4cor/84PSmNQIFAOHX27k=
-----END RSA PUBLIC KEY-----""",
    "Data1": """-----BEGIN RSA PUBLIC KEY-----
MIIBCwKCAQEAsM5QTi6Fo1li23fkvP7jXqFlanR61VS1znElmsZH0Ez4LtuM7WUC
QnZyi9u15T89WmIKCGpfgHZBgJEVFqW9FMhBxrA5/gXcqnGESjc+NNF71rfug/qg
Ue7B9tXlq18/bdD7qPEjYY02H5fh4Z/g0+oClSNyZR46G/MXZSw8KMV4QHikCAxJ
N40Nxd+MpQcpc3J5SXfsXxi9gNSxHO1+KzGwRrEh1/9d7bPyd4jBuTR+SEd+ZDHR
3jTbbRNUypB/x780KXuJnGrC8UfB6ttxfBmLs7nmhteO6R1rr5zWuHJBry7Of9t4
JEQRDwb2VT3fpQ2oHgOc5zDYMOdObdX/tQIEZYdnGQ==
-----END RSA PUBLIC KEY-----""",
    "Data2": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEApvNV8cCaxTBtW6kB94Gd5/+NuQnVLxRo6b0QUSSXh8KGWCRNPjpq
LEyu0kuHCTG5xfomzB5vlq9INu0odZAWZu+NWvz+YydnIQO+UPDF9J/wE92SMzBj
n7d4uEglevPswQLiJVQThCtrl1B8dCz7vFvlSknx23jdUQ/0hfxVnLvP2GpNW/v5
iDK+J2RJFxpd8td9FpHMF+OMxT3pvQyOBleWgEcmiaA1O6AxZA3YGWaL7qnKgx4M
Pi5Ex1Cjnw66+A25kc34UvDA4pteJHC+AwTvjLN3nF2jr3l61jEcXULCWpA4rdWT
dm77dL2KwxXDiYxNAecEFVuG/PRV7J8hHQIFAP3yuSk=
-----END RSA PUBLIC KEY-----""",
    "Data3": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEAvS4XXheufoQvvfTksJhO7JrH1ykMa2ogHtqHhAOZXorLLXvsWfVO
Q+enFY7kBjKyVbUOlqj3M6Ho2S8QgJTO/Xz3DhD3YlHva59RnIXI2gmSyvrTB0Z/
GopmJzVfc9o7763CMy/27tS4/dBM9qKs+csvjE6fG470Z025yECgtTtXzltg4pht
GkjV5+tNjrFt5+wxIydNB56Xow9QCxtpZJ4TstdZvbgq1K06mpLrRTRDxpLPgdDA
9KKwyewYliU2tl78bU5jcgL3s78KbiJ2VSrlOL2AxI6TpID+kFcDy055JsMkKR2V
nRPreV08oQchzQ5miTezWUAk7mIcZoFHwwIFAP////8=
-----END RSA PUBLIC KEY-----""",
    "sd/sd": """-----BEGIN RSA PUBLIC KEY-----
MIIBCwKCAQEAvbz2HnG3JaP3imwnZJMWCyzW9ZjrgzgxZ/EtzFrzpeYPFdYGmBim
XFfBarWpREW7M4y6Z7iy4UAbNmF9SLDp6RLiKauI9AxQK3ICYf+2UuDaXO6QeeXM
JgwQhIugkQFobZOnJLpGT4ynWvH0iR2LO/aFivAPry+bkKXCX9y5zfod2at6j0Ri
7jJ+SECnWs7rDxsBo/98aJpmoyl+Z24yvBU+sknUVn7giaFPTOet9YvBzNmAing4
6fBFXV6T4sX+hyCY2Qs2arnH+TSDTUcxK/3lobC7lSy+B+sTinqN0a+SWeaCACYe
viCKV6AQNxb8J1CHev0OJv9r+bMSy+1kxwIEILt78w==
-----END RSA PUBLIC KEY-----""",
}

# Paths inside the sound archive are relative to sd/ (e.g. "/enus/npc015.bnk" -> Game/sd/enus/npc015.bnk).
SOUND_ARCHIVE = "sd/sd"
SOUND_PREFIX = "/sd/"


def path_hash(path: str) -> int:
    hashable = path.strip().replace("\\", "/").lower()
    if not hashable.startswith("/"):
        hashable = "/" + hashable
    value = 0
    for char in hashable:
        value = (value * 0x85 + ord(char)) & 0xFFFFFFFFFFFFFFFF
    return value


def decrypt_bhd(data: bytes, pem_key: str) -> bytes:
    numbers = serialization.load_pem_public_key(pem_key.encode()).public_numbers()
    in_size = (numbers.n.bit_length() + 7) // 8
    out_size = (numbers.n.bit_length() - 1) // 8
    output = bytearray()
    for offset in range(0, len(data), in_size):
        block = int.from_bytes(data[offset:offset + in_size], "big")
        output += pow(block, numbers.e, numbers.n).to_bytes(out_size, "big")
    return bytes(output)


@dataclass
class FileEntry:
    archive: str
    padded_size: int
    unpadded_size: int
    offset: int
    aes_key: Optional[bytes]
    aes_ranges: List[Tuple[int, int]]


def parse_bhd5(data: bytes, archive: str) -> Dict[int, FileEntry]:
    if data[:4] != b"BHD5":
        raise ValueError(f"{archive}.bhd did not decrypt to a BHD5 header")
    # Same detection as SoulsFormats: the 64-bit layout has zeroed high dwords at 0x14 and 0x1C.
    # AC6 currently uses the 32-bit one (int32 count/offset, buckets are (count, offset)).
    is_64bit = struct.unpack_from("<i", data, 0x14)[0] == 0 and struct.unpack_from("<i", data, 0x1C)[0] == 0
    if is_64bit:
        bucket_count, buckets_offset = struct.unpack_from("<qq", data, 0x10)
    else:
        bucket_count, buckets_offset = struct.unpack_from("<ii", data, 0x10)
    entries = {}
    for bucket in range(bucket_count):
        if is_64bit:
            header_count, _, headers_offset = struct.unpack_from("<iiq", data, buckets_offset + bucket * 16)
        else:
            header_count, headers_offset = struct.unpack_from("<ii", data, buckets_offset + bucket * 8)
        for i in range(header_count):
            name_hash, padded, unpadded, offset, _sha_offset, aes_offset = \
                struct.unpack_from("<QiiqqQ", data, headers_offset + i * 40)
            aes_key, ranges = None, []
            if aes_offset:
                aes_key = data[aes_offset:aes_offset + 16]
                range_count = struct.unpack_from("<i", data, aes_offset + 16)[0]
                for r in range(range_count):
                    start, end = struct.unpack_from("<qq", data, aes_offset + 20 + r * 16)
                    if start != -1 and end != -1 and start != end:
                        ranges.append((start, end))
            entries[name_hash] = FileEntry(archive, padded, unpadded, offset, aes_key, ranges)
    return entries


class GameArchives:
    """Read access to the packed game files. Paths look like the unpacked layout: "menu/hi/01_common.tpf.dcx"."""

    def __init__(self, game_dir: str):
        self.game_dir = game_dir
        self._entries: Dict[str, Dict[int, FileEntry]] = {}

    def _archive_entries(self, archive: str) -> Dict[int, FileEntry]:
        if archive not in self._entries:
            with open(os.path.join(self.game_dir, archive + ".bhd"), "rb") as f:
                raw = f.read()
            data = raw if raw[:4] == b"BHD5" else decrypt_bhd(raw, ARCHIVE_KEYS[archive])
            self._entries[archive] = parse_bhd5(data, archive)
        return self._entries[archive]

    def _find(self, path: str) -> Optional[FileEntry]:
        normalized = "/" + path.replace("\\", "/").lstrip("/")
        if normalized.lower().startswith(SOUND_PREFIX):
            return self._archive_entries(SOUND_ARCHIVE).get(path_hash(normalized[len(SOUND_PREFIX) - 1:]))
        name_hash = path_hash(normalized)
        for archive in ARCHIVE_KEYS:
            if archive == SOUND_ARCHIVE:
                continue
            entry = self._archive_entries(archive).get(name_hash)
            if entry:
                return entry
        return None

    def exists(self, path: str) -> bool:
        return self._find(path) is not None

    def read(self, path: str) -> bytes:
        entry = self._find(path)
        if entry is None:
            raise FileNotFoundError(f"{path} is not in the game archives")
        with open(os.path.join(self.game_dir, entry.archive + ".bdt"), "rb") as f:
            f.seek(entry.offset)
            data = bytearray(f.read(entry.padded_size))
        if entry.aes_key:
            decryptor = Cipher(algorithms.AES(entry.aes_key), modes.ECB()).decryptor()
            for start, end in entry.aes_ranges:
                data[start:end] = decryptor.update(bytes(data[start:end]))
        size = entry.unpadded_size if entry.unpadded_size > 0 else entry.padded_size
        return bytes(data[:size])

    def extract(self, path: str, destination: str) -> str:
        os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
        with open(destination, "wb") as f:
            f.write(self.read(path))
        return destination
