"""Text: tab names, fight descriptions, AC/pilot names and subtitles, in English for every language."""
from ...ids import tab_name_text_id

# Languages with all four text files used below (msg/araae and msg/common have none of them).
LANGUAGES = ["deude", "engus", "frafr", "itait", "jpnjp", "korkr", "polpl", "porbr", "rusru", "spaar", "spaes",
             "thath", "zhocn", "zhotw"]


def gradient(colors, t: float) -> str:
    """The color at t (0-1) along evenly spaced color stops."""
    position = t * (len(colors) - 1)
    i = min(int(position), len(colors) - 2)
    a, b = (bytes.fromhex(color[1:]) for color in colors[i:i + 2])
    return "#" + bytes(round(x + (y - x) * (position - i)) for x, y in zip(a, b)).hex()


def tab_text(tab: str, fights) -> str:
    """The tab name, colored with the game's <font> markup by the first fight in the tab that sets colors; several
    colors make a gradient across the letters (one <font> per letter, as the game's mods do)."""
    colors = next((fight.tab_colors for fight, _ in fights if fight.tab == tab and fight.tab_colors), [])
    if len(colors) < 2:
        return f'<font color="{colors[0]}">{tab}</font>' if colors else tab
    letters = [i for i, char in enumerate(tab) if not char.isspace()]  # Spaces don't take a color step
    if len(letters) < 2:
        return f'<font color="{colors[0]}">{tab}</font>'
    shade = {i: gradient(colors, n / (len(letters) - 1)) for n, i in enumerate(letters)}
    return "".join(f'<font color="{shade[i]}">{char}</font>' if i in shade else char for i, char in enumerate(tab))


def apply(ctx, fights):
    for language in LANGUAGES:
        menu = f"msg/{language}/menu.msgbnd.dcx"
        menu_text, profiles, talk = (ctx.fmg(menu, name) for name in ("FNR_メニューテキスト", "ランカープロフィール", "会話"))
        for fight, ids in fights:
            menu_text.set_text(tab_name_text_id(ids.category), tab_text(fight.tab, fights))
            profiles.set_text(ids.arena, fight.description)
            for i, line in enumerate(fight.intro):
                talk.set_text(ids.intro_talk(i), line.text)
            for i, line in enumerate(fight.outro):
                talk.set_text(ids.outro_talk(i), line.text)

        names = ctx.fmg(f"msg/{language}/item.msgbnd.dcx", "NPC名")
        for fight, ids in fights:
            for offset, text in enumerate((fight.ac_name, fight.pilot_name, fight.ac_name, fight.pilot_name)):
                names.set_text(ids.account + offset, text)
            if isinstance(fight.speaker, str):
                names.set_text(ids.speaker + 3, fight.speaker)
