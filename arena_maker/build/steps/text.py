"""Text: tab names, fight descriptions, AC/pilot names and subtitles, in English for every language."""
from ...ids import tab_name_text_id

# Languages with all four text files used below (msg/araae and msg/common have none of them).
LANGUAGES = ["deude", "engus", "frafr", "itait", "jpnjp", "korkr", "polpl", "porbr", "rusru", "spaar", "spaes",
             "thath", "zhocn", "zhotw"]


def apply(ctx, fights):
    for language in LANGUAGES:
        menu = f"msg/{language}/menu.msgbnd.dcx"
        menu_text, profiles, talk = (ctx.fmg(menu, name) for name in ("FNR_メニューテキスト", "ランカープロフィール", "会話"))
        for fight, ids in fights:
            menu_text.set_text(tab_name_text_id(ids.category), fight.tab)
            profiles.set_text(ids.arena, fight.description)
            for i, line in enumerate(fight.intro):
                talk.set_text(ids.intro_talk(i), line.text)
            for i, line in enumerate(fight.outro):
                talk.set_text(ids.outro_talk(i), line.text)

        names = ctx.fmg(f"msg/{language}/item.msgbnd.dcx", "NPC名")
        for fight, ids in fights:
            for offset, text in enumerate((fight.ac_name, fight.pilot_name, fight.ac_name, fight.pilot_name)):
                names.set_text(ids.account + offset, text)
