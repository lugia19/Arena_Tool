"""Custom music: a BGM_ID table point in init.bnk, playlists in cs_smain.bnk's arena music switch, and the songs as
loose ADPCM sd/wem files."""
from ...audio import audio_file_to_adpcm_wem
from ...soundbank import MusicAdder, Soundbank, add_bgm_points

INIT_BANK = "sd/init.bnk"
MUSIC_BANK = "sd/cs_smain.bnk"


def apply(ctx, fights):
    fights = [(fight, ids) for fight, ids in fights if fight.music]
    if not fights:
        return

    bank = Soundbank(ctx.bnk2json.unpack(ctx.extract(MUSIC_BANK)))
    adder = MusicAdder(bank)
    for fight, ids in fights:
        music = fight.music
        wem, duration_ms = audio_file_to_adpcm_wem(music.file)
        loop_end_ms = duration_ms if music.loop_end is None else music.loop_end * 1000
        if loop_end_ms > duration_ms + 1:
            raise ValueError(f"{fight.name}: loopEnd ({music.loop_end} s) is past the end of the song "
                             f"({duration_ms / 1000:.2f} s)")
        ctx.add_file(f"sd/wem/{ids.music_wem}.wem", wem)
        death = "keep" if music.death_keeps_playing else None
        if music.death:
            death_wem, death_ms = audio_file_to_adpcm_wem(music.death)
            ctx.add_file(f"sd/wem/{ids.death_wem}.wem", death_wem)
            death = (death_wem, ids.death_wem, death_ms)
        adder.add(ids.bgm, wem, ids.music_wem, duration_ms, music.loop_start * 1000, min(loop_end_ms, duration_ms),
                  death)
    adder.save()
    with open(ctx.bnk2json.repack(bank.folder), "rb") as f:
        ctx.add_file(MUSIC_BANK, f.read())

    init = Soundbank(ctx.bnk2json.unpack(ctx.extract(INIT_BANK)))
    add_bgm_points(init, [ids.bgm for _, ids in fights])
    init.save()
    with open(ctx.bnk2json.repack(init.folder), "rb") as f:
        ctx.add_file(INIT_BANK, f.read())
