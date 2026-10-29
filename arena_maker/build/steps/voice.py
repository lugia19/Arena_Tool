"""Voice lines: Play_v/Stop_v events in ALLMIND's bank (English and Japanese voices), audio as loose sd/wem files."""
import os

from ...audio import audio_file_to_wem
from ...soundbank import Soundbank, VoiceLineAdder

BANKS = ["sd/enus/npc015.bnk", "sd/ja/npc015.bnk"]
TEMPLATE_TALK = 600310100  # Carla's first intro line


def apply(ctx, fights):
    lines = []  # (talk ID, wem)
    for fight, ids in fights:
        for i, line in enumerate(fight.intro):
            if line.audio:
                lines.append((ids.intro_talk(i), audio_file_to_wem(line.audio)))
        for i, line in enumerate(fight.outro):
            if line.audio:
                lines.append((ids.outro_talk(i), audio_file_to_wem(line.audio)))
    if not lines:
        return

    for bank_path in BANKS:
        bank = Soundbank(ctx.bnk2json.unpack(ctx.extract(bank_path)))
        adder = VoiceLineAdder(bank, TEMPLATE_TALK)
        for talk_id, wem in lines:
            ctx.add_file(adder.add(talk_id, wem), wem)  # Same wem path for both banks
        bank.save()
        with open(ctx.bnk2json.repack(bank.folder), "rb") as f:
            ctx.add_file(bank_path, f.read())
