"""Audio helpers: Wwise FNV hashes, and PCM and IMA ADPCM .wem files (replacing fnv-hash.exe and wem_converter.exe)."""
import struct
from typing import Tuple

import numpy
import soundfile


def fnv_hash(name: str) -> int:
    """Wwise's 32-bit FNV-1 hash of a lowercased name, used for object/event/source IDs (e.g. "Play_v600310100")."""
    value = 2166136261
    for byte in name.lower().encode("utf-8"):
        value = (value * 16777619) & 0xFFFFFFFF
        value ^= byte
    return value


# Wwise AkChannelConfig, packed as numChannels (8 bits) | configType (4 bits) | channelMask (20 bits).
STEREO_CHANNEL_CONFIG = 2 | (1 << 8) | (0x3 << 12)  # standard config, front left + front right


def pcm_wem(samples: numpy.ndarray, sample_rate: int) -> bytes:
    """Builds a PCM .wem (Wwise's RIFF container) from int16 stereo samples shaped (frames, 2).

    Byte-for-byte what wem_converter.exe produced for stereo input, which is the only PCM .wem known to work in game
    (every stock AC6 .wem is Vorbis). That includes its avgBytesPerSec of rate * 2 rather than rate * blockAlign.
    """
    if samples.dtype != numpy.int16 or samples.ndim != 2 or samples.shape[1] != 2:
        raise ValueError("Expected int16 stereo samples shaped (frames, 2)")
    data = samples.astype("<i2").tobytes()
    channels, bits = 2, 16
    block_align = channels * bits // 8
    fmt = struct.pack("<HHIIHHHHI", 0xFFFE, channels, sample_rate, sample_rate * 2, block_align, bits,
                      6, 0, STEREO_CHANNEL_CONFIG)
    chunks = (b"fmt " + struct.pack("<I", len(fmt)) + fmt
              + b"JUNK" + struct.pack("<I", 4) + bytes(4)
              + b"data" + struct.pack("<I", len(data)) + data)
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def read_stereo(path: str) -> Tuple[numpy.ndarray, int]:
    """Reads any format libsndfile supports (wav, flac, ogg, mp3...) as int16 stereo samples shaped (frames, 2)."""
    samples, sample_rate = soundfile.read(path, dtype="int16", always_2d=True)
    if samples.shape[1] == 1:
        samples = numpy.repeat(samples, 2, axis=1)
    elif samples.shape[1] > 2:
        samples = samples[:, :2]  # Voice lines and music are stereo at most; drop surround channels.
    return numpy.ascontiguousarray(samples), sample_rate


def audio_file_to_wem(path: str) -> bytes:
    """Converts an audio file to a stereo PCM .wem."""
    return pcm_wem(*read_stereo(path))


# region IMA ADPCM
# Wwise's IMA ADPCM (fmt tag 0x0002), as vgmstream decodes it (decode_wwise_ima): per channel, 0x24-byte blocks
# (channel-interleaved) of s16 first sample, s8 step index, a reserved byte and 32 bytes of nibbles, low nibble
# first: 64 samples per block, the last nibble unused. ~4x smaller than PCM. Tested in game (2026-10-29): plays
# streamed like PCM, every stock .wem being Vorbis notwithstanding.
ADPCM_STEPS = numpy.array([
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97,
    107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
    876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871,
    5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623,
    27086, 29794, 32767], dtype=numpy.int32)
ADPCM_INDEX_CHANGES = numpy.array([-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8], dtype=numpy.int32)
ADPCM_BLOCK_BYTES, ADPCM_BLOCK_SAMPLES = 0x24, 64


def _adpcm_encode_blocks(blocks: numpy.ndarray, start_index: numpy.ndarray) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """Encodes all blocks at once (each starts from its own header): (nibbles (n, 63), final step indices)."""
    predicted = blocks[:, 0].copy()
    index = start_index.copy()
    nibbles = numpy.zeros((len(blocks), ADPCM_BLOCK_SAMPLES - 1), dtype=numpy.uint8)
    for j in range(1, ADPCM_BLOCK_SAMPLES):
        step = ADPCM_STEPS[index]
        diff = blocks[:, j] - predicted
        sign = numpy.where(diff < 0, 8, 0)
        magnitude = numpy.minimum(numpy.abs(diff) * 4 // step, 7)
        delta = ((magnitude * 2 + 1) * step) >> 3  # The decoder's reconstruction, so errors don't accumulate
        predicted = numpy.clip(predicted + numpy.where(sign > 0, -delta, delta), -32768, 32767)
        index = numpy.clip(index + ADPCM_INDEX_CHANGES[magnitude | sign], 0, 88)
        nibbles[:, j - 1] = magnitude | sign
    return nibbles, index


def _adpcm_channel(samples: numpy.ndarray) -> numpy.ndarray:
    """int16 mono samples -> blocks shaped (n, 0x24)."""
    padded = numpy.zeros(-(-len(samples) // ADPCM_BLOCK_SAMPLES) * ADPCM_BLOCK_SAMPLES, dtype=numpy.int32)
    padded[:len(samples)] = samples
    blocks = padded.reshape(-1, ADPCM_BLOCK_SAMPLES)
    # Two passes: each block starts at the step index the previous block ended on in the first pass.
    _, final = _adpcm_encode_blocks(blocks, numpy.full(len(blocks), 20, dtype=numpy.int32))
    start = numpy.concatenate([[0], final[:-1]]).astype(numpy.int32)
    nibbles, _ = _adpcm_encode_blocks(blocks, start)
    nibbles = numpy.concatenate([nibbles, numpy.zeros((len(blocks), 1), dtype=numpy.uint8)], axis=1)
    header = numpy.zeros((len(blocks), 4), dtype=numpy.uint8)
    header[:, 0:2] = blocks[:, 0].astype("<i2").view(numpy.uint8).reshape(-1, 2)
    header[:, 2] = start
    return numpy.concatenate([header, nibbles[:, 0::2] | (nibbles[:, 1::2] << 4)], axis=1)


def adpcm_wem(samples: numpy.ndarray, sample_rate: int) -> bytes:
    """Builds a Wwise IMA ADPCM .wem from int16 stereo samples shaped (frames, 2)."""
    data = numpy.stack([_adpcm_channel(samples[:, channel]) for channel in range(2)], axis=1).tobytes()
    block_align = ADPCM_BLOCK_BYTES * 2
    fmt = struct.pack("<HHIIHHHHI", 0x0002, 2, sample_rate, sample_rate * block_align // ADPCM_BLOCK_SAMPLES,
                      block_align, 4, 6, ADPCM_BLOCK_SAMPLES, STEREO_CHANNEL_CONFIG)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def audio_file_to_adpcm_wem(path: str) -> Tuple[bytes, float]:
    """Converts an audio file to a stereo ADPCM .wem. Returns the wem and its duration in milliseconds."""
    samples, sample_rate = read_stereo(path)
    return adpcm_wem(samples, sample_rate), len(samples) / sample_rate * 1000
# endregion
