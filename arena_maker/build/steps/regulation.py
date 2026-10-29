"""Params: one cloned set of rows per fight, based on "Cinder" Carla's fight (all her IDs are 11200000/310/118)."""
from ...ids import PRESET_EMBLEM_CATEGORY

TEMPLATE_ARENA = 118
TEMPLATE_ACCOUNT = 310
TEMPLATE_SPEAKER = 200  # ALLMIND's account: a speaker without an AC
TEMPLATE_CHARA = 11200000
TEMPLATE_TALK = 600310100
TEMPLATE_PRESET_EMBLEM = 1250
STOCK_TAB_CATEGORIES = ("0", "10")


def apply(ctx, fights):
    arena, account, chara_init = ctx.param("ArenaParam"), ctx.param("AccountParam"), ctx.param("CharaInitParam")
    npc, npc_think, talk = ctx.param("NpcParam"), ctx.param("NpcThinkParam"), ctx.param("TalkParam")
    preset_emblems = ctx.param("PresetEmblemSpec")

    used = {arena.values(row)["category"] for row in arena.rows if row.get("id") != "0"}
    taken = sorted({ids.category for _, ids in fights if str(ids.category) in used})
    if taken:  # A base mod's own tabs
        raise ValueError(f"Arena tab categories {taken} are already used by the base mod")

    for fight, ids in fights:
        arena.clone_row(TEMPLATE_ARENA, ids.arena, paramdexName=f"Custom: {fight.name}", category=ids.category,
                        missionParamID=fight.map_id, rankIconID=ids.rank_icon,
                        ranker_accountParamID=ids.account, ranker_chrInitParamID=ids.chara,
                        ranker_npcParamID=ids.chara, ranker_thinkParamID=ids.chara,
                        firstReward_cash=fight.first_reward, rematchReward_cash=fight.rematch_reward,
                        startCutsceneId=fight.start_cutscene, endCutsceneId=fight.end_cutscene, bgmId=fight.bgm)

        account_row = account.clone_row(TEMPLATE_ACCOUNT, ids.account, paramdexName=f"Custom: {fight.name}",
                                        nameTextID=ids.account)
        if fight.emblem:  # Otherwise the template's emblem stays
            account_row.set("emblemImageID", str(ids.emblem))

        chara_init.clone_row(TEMPLATE_CHARA, ids.chara, paramdexName=f"Custom: {fight.name}", assemDataID=ids.chara)
        npc.clone_row(TEMPLATE_CHARA, ids.chara, paramdexName=f"Custom: {fight.name}", nameId=ids.account)
        think_row = npc_think.clone_row(TEMPLATE_CHARA, ids.chara, paramdexName=f"Custom: {fight.name}")
        if fight.logic_file:
            think_row.set("logicId", str(ids.chara))
        elif fight.logic_id is not None:
            think_row.set("logicId", str(fight.logic_id))

        talker = fight.speaker
        if isinstance(fight.speaker, str):  # The subtitle shows text nameTextID + 3 of the talker's account
            account.clone_row(TEMPLATE_SPEAKER, ids.speaker, paramdexName=f"Custom: {fight.name} speaker",
                              nameTextID=ids.speaker)
            talker = ids.speaker
        talk_ids = [ids.intro_talk(i) for i in range(len(fight.intro))] + [ids.outro_talk(i) for i in range(len(fight.outro))]
        for talk_id in talk_ids:
            talk.clone_row(TEMPLATE_TALK, talk_id, paramdexName=f"Custom: {fight.name}", msgId=talk_id,
                           voiceId=talk_id, talkerID=talker)

        if fight.emblem and fight.add_emblem_to_decals:
            preset_emblems.clone_row(TEMPLATE_PRESET_EMBLEM, ids.preset_emblem, PieceID=ids.emblem,
                                     CategoryID=PRESET_EMBLEM_CATEGORY)

    if ctx.hide_vanilla_arena:  # ArenaParam has no "enabled" field, so the stock fights go (row 0 is an empty dummy)
        for row in list(arena.rows):
            if row.get("id") != "0" and arena.values(row)["category"] in STOCK_TAB_CATEGORIES:
                arena.remove_row(int(row.get("id")))
