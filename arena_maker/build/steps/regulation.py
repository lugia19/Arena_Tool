"""Params: one cloned set of rows per fight, based on "Cinder" Carla's fight (all her IDs are 11200000/310/118)."""
from ...ids import PRESET_EMBLEM_CATEGORY, TAB_CATEGORY

TEMPLATE_ARENA = 118
TEMPLATE_ACCOUNT = 310
TEMPLATE_CHARA = 11200000
TEMPLATE_TALK = 600310100
TEMPLATE_PRESET_EMBLEM = 1250


def apply(ctx, fights):
    arena, account, chara_init = ctx.param("ArenaParam"), ctx.param("AccountParam"), ctx.param("CharaInitParam")
    npc, npc_think, talk = ctx.param("NpcParam"), ctx.param("NpcThinkParam"), ctx.param("TalkParam")
    preset_emblems = ctx.param("PresetEmblemSpec")

    for fight, ids in fights:
        arena.clone_row(TEMPLATE_ARENA, ids.arena, paramdexName=f"Custom: {fight.name}", category=TAB_CATEGORY,
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

        talk_ids = [ids.intro_talk(i) for i in range(len(fight.intro))] + [ids.outro_talk(i) for i in range(len(fight.outro))]
        for talk_id in talk_ids:
            talk.clone_row(TEMPLATE_TALK, talk_id, paramdexName=f"Custom: {fight.name}", msgId=talk_id,
                           voiceId=talk_id, talkerID=fight.speaker)

        if fight.emblem and fight.add_emblem_to_decals:
            preset_emblems.clone_row(TEMPLATE_PRESET_EMBLEM, ids.preset_emblem, PieceID=ids.emblem,
                                     CategoryID=PRESET_EMBLEM_CATEGORY)
