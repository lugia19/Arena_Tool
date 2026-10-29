"""Audio helpers: Wwise FNV hashes and PCM .wem files (replacing fnv-hash.exe and the private wem_converter.exe)."""
import struct

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


def audio_file_to_wem(path: str) -> bytes:
    """Reads any format libsndfile supports (wav, flac, ogg, mp3...) and converts it to a stereo PCM .wem."""
    samples, sample_rate = soundfile.read(path, dtype="int16", always_2d=True)
    if samples.shape[1] == 1:
        samples = numpy.repeat(samples, 2, axis=1)
    elif samples.shape[1] > 2:
        samples = samples[:, :2]  # Voice lines and music are stereo at most; drop surround channels.
    return pcm_wem(numpy.ascontiguousarray(samples), sample_rate)
