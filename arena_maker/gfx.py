"""Minimal Scaleform GFX (SWF) tag editor - just enough to add custom arena rank icons, replacing the JPEXS round-trip.

The rank icon in each menu .gfx is a 1000-frame sprite (symbol "*.ArenaRank_00000_*") where frame N shows rank N:
every rank frame does RemoveObject2(depth 1) + PlaceObject3(image, depth 1). The images are
GFX DefineExternalImage2 tags pointing at subtextures (by export name) in the SB_* texture atlases.
"""
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional

TAG_END = 0
TAG_SHOW_FRAME = 1
TAG_REMOVE_OBJECT2 = 28
TAG_DEFINE_SPRITE = 39
TAG_PLACE_OBJECT3 = 70
TAG_SYMBOL_CLASS = 76
TAG_DEFINE_EXTERNAL_IMAGE2 = 1009

# Every tag whose body starts with the character ID it defines (shapes, bitmaps, text, fonts, buttons, sprites, sounds...).
CHARACTER_DEFINING_TAGS = {2, 6, 7, 10, 11, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 75, 83, 84, 90,
                           1001, TAG_DEFINE_EXTERNAL_IMAGE2}

# DefineExternalImage2 layout (per JPEXS tags/gfx/DefineExternalImage2.java):
#   u16 imageID, u16 idType, u16 bitmapFormat, u16 targetWidth, u16 targetHeight,
#   u8-length exportName, u8-length fileName, optional extraData.
# With idType == IDTYPE_NONE the imageID is a regular SWF character ID; other id types are loader-internal.
DEI2_HEADER = struct.Struct("<HHHHH")
IDTYPE_NONE = 0

# Matches the stock rank images: bitmapFormat 13, 232x128.
RANK_IMAGE_FORMAT = 13
RANK_IMAGE_WIDTH = 232
RANK_IMAGE_HEIGHT = 128
BLANK_RANK_EXPORT = "ArenaRank_00000d"


@dataclass
class Tag:
    code: int
    body: bytes
    long_form: bool = False  # Kept so unmodified tags serialize byte-identically.


def parse_tags(data: bytes, pos: int, end: int) -> List[Tag]:
    tags = []
    while pos < end:
        code_and_length = struct.unpack_from("<H", data, pos)[0]
        pos += 2
        code, length = code_and_length >> 6, code_and_length & 0x3F
        long_form = length == 0x3F
        if long_form:
            length = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        tags.append(Tag(code, data[pos:pos + length], long_form))
        pos += length
        if code == TAG_END:
            break
    return tags


def serialize_tags(tags: List[Tag]) -> bytes:
    out = bytearray()
    for tag in tags:
        if tag.long_form or len(tag.body) >= 0x3F:
            out += struct.pack("<HI", (tag.code << 6) | 0x3F, len(tag.body))
        else:
            out += struct.pack("<H", (tag.code << 6) | len(tag.body))
        out += tag.body
    return bytes(out)


def _read_string(body: bytes, pos: int):
    length = body[pos]
    return body[pos + 1:pos + 1 + length].decode("ascii"), pos + 1 + length


def _pascal(text: str) -> bytes:
    raw = text.encode("ascii")
    return bytes([len(raw)]) + raw


class GfxFile:
    def __init__(self, data: bytes):
        if data[:3] != b"GFX":
            raise ValueError("Only uncompressed GFX files are supported")  # All the arena menus are uncompressed.
        rect_bits = data[8] >> 3
        self.header_end = 8 + (5 + 4 * rect_bits + 7) // 8 + 4  # signature/version/length, RECT, frame rate+count
        self.header = data[:self.header_end]
        self.tags = parse_tags(data, self.header_end, len(data))

    def to_bytes(self) -> bytes:
        body = serialize_tags(self.tags)
        header = bytearray(self.header)
        struct.pack_into("<I", header, 4, len(header) + len(body))
        return bytes(header) + body

    # region Queries
    def symbol_names(self) -> Dict[int, str]:
        names = {}
        for tag in self.tags:
            if tag.code == TAG_SYMBOL_CLASS:
                count = struct.unpack_from("<H", tag.body, 0)[0]
                pos = 2
                for _ in range(count):
                    character_id = struct.unpack_from("<H", tag.body, pos)[0]
                    end = tag.body.index(b"\0", pos + 2)
                    names[character_id] = tag.body[pos + 2:end].decode("utf-8")
                    pos = end + 1
        return names

    def external_images(self) -> Dict[str, int]:
        """export name -> character ID, for DefineExternalImage2 tags that are regular characters."""
        images = {}
        for tag in self.tags:
            if tag.code == TAG_DEFINE_EXTERNAL_IMAGE2:
                image_id, id_type = DEI2_HEADER.unpack_from(tag.body, 0)[:2]
                if id_type == IDTYPE_NONE:
                    images[_read_string(tag.body, DEI2_HEADER.size)[0]] = image_id
        return images

    def max_character_id(self) -> int:
        highest = 0
        for tag in self.tags:
            if tag.code not in CHARACTER_DEFINING_TAGS:
                continue
            if tag.code == TAG_DEFINE_EXTERNAL_IMAGE2 and DEI2_HEADER.unpack_from(tag.body, 0)[1] != IDTYPE_NONE:
                continue
            highest = max(highest, struct.unpack_from("<H", tag.body, 0)[0])
        return highest

    def find_rank_sprite(self) -> int:
        """Index (in self.tags) of the rank icon sprite."""
        names = self.symbol_names()
        for index, tag in enumerate(self.tags):
            if tag.code == TAG_DEFINE_SPRITE:
                sprite_id = struct.unpack_from("<H", tag.body, 0)[0]
                name = names.get(sprite_id, "")
                if ".ArenaRank_" in name:
                    return index
        raise ValueError("No ArenaRank sprite in this GFX file")
    # endregion

    def add_rank_icons(self, icons: Dict[int, str]):
        """icons: rank number (sprite frame) -> export name of the subtexture in the atlas, e.g. {300: "CustomArenaRank_00300"}."""
        existing = self.external_images()
        if BLANK_RANK_EXPORT not in existing:
            raise ValueError(f"{BLANK_RANK_EXPORT} not found")

        # New images go right after the last stock rank image, so they're defined before the sprite uses them.
        last_rank_image = max(i for i, t in enumerate(self.tags) if t.code == TAG_DEFINE_EXTERNAL_IMAGE2
                              and _read_string(t.body, DEI2_HEADER.size)[0].startswith("ArenaRank"))
        next_id = (self.max_character_id() // 100 + 1) * 100
        character_ids = {}
        new_tags = []
        for rank, export_name in sorted(icons.items()):
            character_ids[rank] = next_id
            body = DEI2_HEADER.pack(next_id, IDTYPE_NONE, RANK_IMAGE_FORMAT, RANK_IMAGE_WIDTH, RANK_IMAGE_HEIGHT)
            body += _pascal(export_name) + _pascal(export_name + ".tga")
            new_tags.append(Tag(TAG_DEFINE_EXTERNAL_IMAGE2, body))
            next_id += 1
        self.tags[last_rank_image + 1:last_rank_image + 1] = new_tags

        sprite_index = self.find_rank_sprite()
        sprite = self.tags[sprite_index]
        sprite_id, frame_count = struct.unpack_from("<HH", sprite.body, 0)
        subtags = parse_tags(sprite.body, 4, len(sprite.body))

        # Template: an existing depth-1 placement. Only the character ID (bytes 4-5) differs between ranks.
        template = next(t for t in subtags if t.code == TAG_PLACE_OBJECT3 and struct.unpack_from("<H", t.body, 2)[0] == 1)
        if not template.body[0] & 0x02 or not template.body[1] & 0x10:
            raise ValueError("Unexpected PlaceObject3 layout in the rank sprite")

        def placement(character_id: int) -> List[Tag]:
            body = bytearray(template.body)
            struct.pack_into("<H", body, 4, character_id)
            return [Tag(TAG_REMOVE_OBJECT2, struct.pack("<H", 1)), Tag(TAG_PLACE_OBJECT3, bytes(body), long_form=True)]

        additions: Dict[int, List[Tag]] = {rank: placement(cid) for rank, cid in character_ids.items()}
        # Frames after the last custom rank go back to the blank icon, same as the stock sprite does after rank 112.
        after_last = max(icons) + 1
        if after_last < frame_count and after_last not in additions:
            additions[after_last] = placement(existing[BLANK_RANK_EXPORT])
        if max(additions) >= frame_count:
            raise ValueError(f"Rank {max(additions)} doesn't fit in the {frame_count}-frame rank sprite")

        result, frame = [], 0
        for tag in subtags:
            if tag.code == TAG_SHOW_FRAME:
                result.extend(additions.get(frame, []))
                frame += 1
            result.append(tag)
        sprite.body = sprite.body[:4] + serialize_tags(result)
        sprite.long_form = True
