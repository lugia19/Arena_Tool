local f0_local0 = 99009900
local f0_local1 = { _BattleSituation = 0, _EvenTimeout = 1, _Flag_FirstABDist = 5, _Count_AA = 6, _GuardCount = 8, _Count_Fly = 9, _DBMoratorium = 10, _DBDist = 11, _DBAngle = 12, _DBAngleFS = 13, _DBRisk = 14, _Variation = 19 }
local f0_local2 = { _EvenFinishTime = 0, _AggressiveTime = 1, _DefensiveTime = 2, _EneMelee = 3, _CT_LmtrRls = 5, _CT_FullBurst = 6, _CT_NearRpl = 7, _CT_Fly = 8, _CT_InterruptAB = 9 }
local f0_local3 = { _EvenFinishTime = 10, _EneMelee = 2, _CT_LmtrRls = 45, _CT_FullBurst = 15, _CT_NearRpl = 2, _CT_Fly = 3, _CT_InterruptAB = 15 }
local f0_local4 = { _Initial = 0, _EVEN = 1, _GOOD = 2, _BAD = 3 }
local f0_local5 = { _V_PrisonBreak = 4200010, _EvOp_PrisonBreak_AB = 4200011, _EvOp_PrisonBreak_AB_Shot1 = 4200012, _EvOp_PrisonBreak_AB_Shot2 = 4200013, _isRunningAA = 9100 }
local f0_local6 = { _Initial = 0, _V_PrisonBreak = 1 }
local f0_local7 = { _NearRpl = 0 }
local f0_local8 = { _AtkOp_HandMissileLR = 0, _AtkOp_HandMissileOneSide = 1, _AtkOp_ShoulderMissileLR = 2, _AtkOp_ShoulderMissileOneSide = 3 }
local f0_local9 = { _BurstRifle = 10000100, _SemiAutoRifle = 10010100, _SemiAutoRifle2 = 10020100, _LaserRifle = 11100100, _LaserRifle2 = 11110100, _HighLaserRifleKAI = 11120100, _LaserRifle3 = 11130100, _PlasmaRifle = 11200100, _HighLaserRifleKS = 11210100, _DoubleLaserRifle = 11400100, _LaserShotgun0 = 11500100, _LaserShotgunWide = 11510100, _PlasmaRifleMAI = 11520100 }
local f0_local10 = { _Reverse = 11201000 }
local f0_local11 = AI_WEAPON_PLACE_EnemyWep00
local f0_local12 = AI_WEAPON_PLACE_EnemyWep01
local f0_local13 = AI_WEAPON_PLACE_EnemyWep02
local f0_local14 = AI_WEAPON_PLACE_EnemyWep03
local f0_local15 = AI_WEAPON_PLACE_ItemSlot00
local f0_local16 = AI_WEAPON_PLACE_CoreSpecial
InitializeGlobalFuncArray()

local f0_local17 = function(ai)
    local f1_local0 = ai:GetNumber(f0_local1._BattleSituation)
    local f1_local1 = f1_local0
    local hpRate = ai:GetHpRate(TARGET_ENE_0)
    local hpRate2 = ai:GetHpRate(TARGET_SELF)
    if f1_local0 == f0_local4._Initial then
        f1_local1 = f0_local4._GOOD
        ai:SetTimer(f0_local2._EvenFinishTime, 0)
        ai:SetTimer(f0_local2._AggressiveTime, 6)
        ai:SetTimer(f0_local2._DefensiveTime, 0)
        ai:SetNumber(f0_local1._EvenTimeout, 0)
    elseif f1_local0 == f0_local4._EVEN then
        if ai:IsFinishTimer(f0_local2._EvenFinishTime) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_S) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_L) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_GuardBreak) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_BlowAway) then
            f1_local1 = f0_local4._GOOD
            ai:SetTimer(f0_local2._EvenFinishTime, 0)
            ai:SetTimer(f0_local2._AggressiveTime, 8)
            ai:SetTimer(f0_local2._DefensiveTime, 0)
            ai:SetNumber(f0_local1._EvenTimeout, 0)
        end
        if EZOP_IsNpcAcDamaged_Stagger_L(ai) or EZOP_IsNpcAcDamaged_BlowAway(ai) or EZOP_IsNpcAcDamaged_GuardBreak(ai) then
            f1_local1 = f0_local4._BAD
            ai:SetTimer(f0_local2._EvenFinishTime, 0)
            ai:SetTimer(f0_local2._AggressiveTime, 0)
            ai:SetTimer(f0_local2._DefensiveTime, 4)
            ai:SetNumber(f0_local1._EvenTimeout, 0)
        end
    elseif f1_local0 == f0_local4._GOOD then
        if ai:IsFinishTimer(f0_local2._AggressiveTime) then
            f1_local1 = f0_local4._EVEN
            ai:SetTimer(f0_local2._EvenFinishTime, f0_local3._EvenFinishTime)
            ai:SetTimer(f0_local2._AggressiveTime, 0)
            ai:SetTimer(f0_local2._DefensiveTime, 0)
            ai:SetNumber(f0_local1._EvenTimeout, 0)
        end
        if EZOP_IsNpcAcDamaged_Stagger_L(ai) or EZOP_IsNpcAcDamaged_BlowAway(ai) or EZOP_IsNpcAcDamaged_GuardBreak(ai) then
            f1_local1 = f0_local4._BAD
            ai:SetTimer(f0_local2._EvenFinishTime, 0)
            ai:SetTimer(f0_local2._AggressiveTime, 0)
            ai:SetTimer(f0_local2._DefensiveTime, 4)
            ai:SetNumber(f0_local1._EvenTimeout, 0)
        end
    elseif f1_local0 == f0_local4._BAD and ai:IsFinishTimer(f0_local2._DefensiveTime) then
        f1_local1 = f0_local4._EVEN
        ai:SetTimer(f0_local2._EvenFinishTime, f0_local3._EvenFinishTime)
        ai:SetTimer(f0_local2._AggressiveTime, 0)
        ai:SetTimer(f0_local2._DefensiveTime, 0)
        ai:SetNumber(f0_local1._EvenTimeout, 0)
    else
    end
    ai:SetNumber(f0_local1._BattleSituation, f1_local1)
end

local f0_local18 = function(f2_arg0)
    local f2_local0 = f2_arg0:GetNumber(f0_local1._BattleSituation)
    if f2_local0 == f0_local4._EVEN and f2_arg0:IsFinishTimer(f0_local2._EvenFinishTime) and f2_arg0:GetNumber(f0_local1._EvenTimeout) == 0 then
        f2_arg0:SetNumber(f0_local1._EvenTimeout, 1)
        f0_local17(f2_arg0)
    end
end

local f0_local19 = function(ai, f3_arg1, f3_arg2)
    local distance = ai:GetOriginDist(TARGET_ENE_0)
    local f3_local1 = 450
    if f3_arg2 == f0_local8._AtkOp_HandMissileLR or f3_arg2 == f0_local8._AtkOp_HandMissileOneSide or f3_arg2 == f0_local8._AtkOp_ShoulderMissileLR or f3_arg2 == f0_local8._AtkOp_ShoulderMissileOneSide then
        local f3_local2 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local11) > 0
        local f3_local3 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local12) > 0
        local f3_local4 = f0_local11
        local f3_local5 = f0_local12
        local f3_local6 = {}
        if f3_arg2 == f0_local8._AtkOp_ShoulderMissileLR or f3_arg2 == f0_local8._AtkOp_ShoulderMissileOneSide then
            f3_local2 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local13) > 0
            f3_local3 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local14) > 0
            f3_local4 = f0_local13
            f3_local5 = f0_local14
        end
        if f3_arg2 == f0_local8._AtkOp_HandMissileLR or f3_arg2 == f0_local8._AtkOp_ShoulderMissileLR then
            if f3_local1 < distance then
                f3_local6 = {}
            elseif f3_local2 and f3_local3 then
                f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local4, 0, 10, 0, 0.04, -1),
                    EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local5, 0, 10, 0, 0.04, -1) }
            elseif f3_local2 and not f3_local3 then
                f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local4, 0, 10, 0, 0.04, -1) }
            elseif f3_local3 and not f3_local2 then
                f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local5, 0, 10, 0, 0.04, -1) }
            else
                f3_local6 = {}
            end
        elseif f3_arg2 == f0_local8._AtkOp_HandMissileOneSide or f3_arg2 == f0_local8._AtkOp_ShoulderMissileOneSide then
            if f3_local1 < distance then
                f3_local6 = {}
            elseif not (f3_local2 and f3_local3) then
                if f3_local2 and not f3_local3 then
                    f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local4, 0, 10, 0, 0.04, -1) }
                elseif f3_local3 and not f3_local2 then
                    f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local5, 0, 10, 0, 0.04, -1) }
                    if false then
                    end
                end
            elseif not f3_local2 and not f3_local3 then
                f3_local6 = {}
            elseif ai:GetRandam_Int(0, 1) == 1 then
                f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local4, 0, 10, 0, 0.04, -1) }
            else
                f3_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f3_arg1, f3_local5, 0, 10, 0, 0.04, -1) }
            end
        else
            f3_local6 = {}
        end
        return f3_local6
    else
    end
end

function LogicInitialSetup_99009900(f4_arg0)
    EZOP_LayerSetup(f4_arg0, f0_local0)
    f4_arg0:SetCameraEmuSwingSpeedH(9999)
    f4_arg0:SetCameraEmuSwingSpeedV(9999)
    f4_arg0:SetCameraTargetPastTime(0)
    f4_arg0:SetCameraTargetSampleTime(0)
    f4_arg0:SetCameraTargetPredictionTime(0)
    EZOP_SetUpInterruptFunc(f4_arg0, InterrunptCallBack_99009900)
    EZOP_UseInterrupt(f4_arg0, INTERUPT_TransitionAiActType, TARGET_ENE_0)
    EZOP_UseInterrupt(f4_arg0, INTERUPT_Inside_ObserveArea, f0_local7._NearRpl, TARGET_SELF, TARGET_ENE_0, AI_DIR_TYPE_F,
        120, 70)
    EZOP_UseInterrupt(f4_arg0, INTERUPT_ActivateSpecialEffect, TARGET_SELF, f0_local5._isRunningAA)
    f4_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
    f4_arg0:SetLockonTargetType(TARGET_ENE_0)
    local f4_local0 = f4_arg0:GetNumber(f0_local1._Variation)
    if f4_local0 == f0_local6._Initial and f4_arg0:HasSpecialEffectId(TARGET_SELF, f0_local5._V_PrisonBreak) then
        f4_local0 = f0_local6._V_PrisonBreak
        EZOP_UseInterrupt(f4_arg0, INTERUPT_ActivateSpecialEffect, TARGET_SELF, f0_local5._EvOp_PrisonBreak_AB_Shot1)
        EZOP_UseInterrupt(f4_arg0, INTERUPT_ActivateSpecialEffect, TARGET_SELF, f0_local5._EvOp_PrisonBreak_AB_Shot2)
    end
    f4_arg0:SetNumber(f0_local1._Variation, f4_local0)
    EZOP_CommonReactionWhenPlayerDies_SetUp(f4_arg0, f0_local0)
end

REGIST_INITIALIZE_FUNCTION(f0_local0, "LogicInitialSetup_" .. f0_local0)
OpFuncArr[f0_local0] = EZOP_OPERATION_SET

local f0_local20 = function(ai, f5_arg1)
    local f5_local0 = {}
    local distance = ai:GetOriginDist(TARGET_ENE_0)
    local f5_local2 = ai:GetOriginDistXZ(TARGET_ENE_0)
    local f5_local3 = ai:GetHeightFromGround(TARGET_ENE_0)
    local f5_local4 = ai:GetHeightFromGround(TARGET_SELF)
    local f5_local5 = ai:GetNumber(f0_local1._Variation)
    local f5_local6 = ai:GetNumber(f0_local1._BattleSituation)
    local f5_local7 = not (f5_local6 ~= f0_local4._GOOD)
    local f5_local8 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local11) > 0
    local f5_local9 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local12) > 0
    local f5_local10 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local13) > 0
    local f5_local11 = ai:GetMagazineBulletRate(TARGET_SELF, f0_local14) > 0
    if f5_local8 then
        local f5_local12 = f5_local8
    elseif f5_local9 then
        local f5_local12 = f5_local9
    elseif f5_local10 then
        local f5_local12 = f5_local10
    else
        local f5_local12 = f5_local11
    end
    local hpRate = ai:GetHpRate(TARGET_SELF)
    local f5_local14 = ai:GetItemStockNum(TARGET_SELF, f0_local15)
    local f5_local15 = ai:GetRequireEn_QbNum(TARGET_SELF) > 2
    local f5_local16 = distance <= 450
    if ai:GetNpcThinkParamID() == f0_local10._Reverse and ai:GetNumber(f0_local1._Flag_FirstABDist) == 0 then
        f5_local16 = distance <= 700
        ai:SetNumber(f0_local1._Flag_FirstABDist, 1)
    end
    ai:SetLockonTargetType(TARGET_ENE_0)
    ai:SetTurnTargetMode(AI_TURN_TARGET_TYPE_TARGET_DIRECTION)
    ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
    f0_local17(ai)
    if f5_local4 > 1 and ai:IsFinishTimer(f0_local2._CT_Fly) then
        local f5_local17 = ai:GetNumber(f0_local1._Count_Fly) + 1
        ai:SetNumber(f0_local1._Count_Fly, f5_local17)
    end
    if ai:IsFinishTimer(f0_local2._CT_Fly) and ai:GetNumber(f0_local1._Count_Fly) > 1 then
        ai:SetTimer(f0_local2._CT_Fly, f0_local3._CT_Fly)
        ai:SetNumber(f0_local1._Count_Fly, 0)
    end
    if EZOP_CommonReactionWhenPlayerDies(ai, f5_local0, EZOP_ReactionType_WhenPlayerDies._WAIT) then
    elseif f5_local5 == f0_local6._V_PrisonBreak and ai:HasSpecialEffectId(TARGET_SELF, f0_local5._EvOp_PrisonBreak_AB) then
        f5_local0[8000] = 100
    elseif hpRate < 0.5 and f5_local14 > 0 and f5_local5 ~= f0_local6._V_PrisonBreak then
        f5_local0[3000] = 100
    elseif f5_local5 == f0_local6._V_PrisonBreak and ai:GetNumber(f0_local1._Count_AA) < 3 and ai:IsFinishTimer(f0_local2._CT_LmtrRls) and distance < 100 then
        f5_local0[2000] = 100
    elseif ai:IsFinishTimer(f0_local2._CT_FullBurst) and f5_local16 then
        if f5_local2 > 180 then
            if ai:GetRequireEn_QbNum(TARGET_SELF) > 2 then
                f5_local0[1550] = 100
            else
                f5_local0[1500] = 100
            end
        elseif distance > 70 then
            if ai:GetRequireEn_QbNum(TARGET_SELF) > 2 then
                f5_local0[1550] = 100
            else
                f5_local0[1510] = 100
            end
        elseif ai:GetRequireEn_QbNum(TARGET_SELF) > 2 then
            f5_local0[1620] = 100
        else
            f5_local0[1520] = 100
        end
        ai:SetTimer(f0_local2._CT_FullBurst, f0_local3._CT_FullBurst)
    elseif f5_local2 > 180 then
        if ai:GetRequireEn_QbNum(TARGET_SELF) > 2 and ai:IsFinishTimer(f0_local2._CT_Fly) then
            f5_local0[1200] = 100
        else
            f5_local0[1000] = 100
            f5_local0[1010] = 100
        end
    elseif f5_local2 > 70 then
        if ai:GetRequireEn_QbNum(TARGET_SELF) > 2 and ai:IsFinishTimer(f0_local2._CT_Fly) then
            EZOP_CActLot(f5_local0, 1200, 50, 0)
            EZOP_CActLot(f5_local0, 1210, 100, 0)
        else
            f5_local0[1011] = 50
            f5_local0[1030] = 100
        end
    elseif ai:GetRequireEn_QbNum(TARGET_SELF) > 2 and ai:IsFinishTimer(f0_local2._CT_Fly) then
        f5_local0[1220] = 50
        f5_local0[1100] = 100
    elseif ai:GetRequireEn_QbNum(TARGET_SELF) > 2 then
        f5_local0[1100] = 100
        f5_local0[1031] = 10
    else
        f5_local0[1031] = 100
    end
    EZOP_SetCoolTime(ai, f5_local0, 1100, 5, 0)
    EZOP_SetCoolTime(ai, f5_local0, 1110, 5, 0)
    return EZOP_MakeActLotTable(f5_local0)
end

TacCtrlFuncArr[f0_local0] = f0_local20

function InterrunptCallBack_99009900(ai, f6_arg1, f6_arg2, f6_arg3)
    local f6_local0 = {}
    local distance = ai:GetOriginDist(TARGET_ENE_0)
    local f6_local2 = ai:GetNumber(f0_local1._BattleSituation)
    local f6_local3 = ai:GetShieldHpRate(TARGET_SELF, AI_SHIELD_PHYSICS)
    local f6_local4 = ai:GetNumber(f0_local1._GuardCount) + 1
    if ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_S) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_L) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_BlowAway) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_GuardBreak) then
        f0_local17(ai)
    end
    if ai:IsInterupt(INTERUPT_ActivateSpecialEffect) then
        if ai:GetSpecialEffectActivateInterruptId(f0_local5._EvOp_PrisonBreak_AB_Shot1) then
            f6_local0[8001] = 100
            EZOP_ExecInterruptAction(ai, f6_local0)
        end
        if ai:GetSpecialEffectActivateInterruptId(f0_local5._EvOp_PrisonBreak_AB_Shot2) then
            f6_local0[8002] = 100
            EZOP_ExecInterruptAction(ai, f6_local0)
        end
        if ai:GetSpecialEffectActivateInterruptId(f0_local5._isRunningAA) then
            local f6_local5 = ai:GetNumber(f0_local1._Count_AA) + 1
            ai:SetNumber(f0_local1._Count_AA, f6_local5)
            ai:SetTimer(f0_local2._CT_LmtrRls, f0_local3._CT_LmtrRls)
        end
    end
end

local f0_local21 = function(ai, f7_arg1, f7_arg2, f7_arg3)
    local f7_local0 = {}
    local distance = ai:GetOriginDist(TARGET_ENE_0)
    local f7_local2 = ai:GetNumber(f0_local1._BattleSituation)
    if ai:IsInterupt(INTERUPT_Inside_ObserveArea) and ai:IsInsideObserve(f0_local7._NearRpl) and ai:IsFinishTimer(f0_local2._CT_NearRpl) then
        if ai:GetRequireEn_QbNum(TARGET_SELF) > 1 and not ai:IsFinishTimer(f0_local2._EneMelee) then
            ai:SetTimer(f0_local2._CT_NearRpl, f0_local3._CT_NearRpl)
            ai:SetTimer(f0_local2._EneMelee, 0)
            f7_local0[9051] = 10
            EZOP_ExecInterruptAction(ai, f7_local0)
        else
            ai:SetTimer(f0_local2._CT_NearRpl, f0_local3._CT_NearRpl)
            EZOP_Replanning(ai)
        end
    end
    if (ai:GetInterruptResult_TransitionAiActType(AiActionType_Melee) or ai:GetInterruptResult_TransitionAiActType(AiActionType_ComboMelee) or ai:GetInterruptResult_TransitionAiActType(AiActionType_AssaultBoost_Kick_Start)) and distance < 150 then
        if distance > 70 then
            if ai:IsFinishTimer(f0_local2._EneMelee) then
                ai:SetTimer(f0_local2._EneMelee, f0_local3._EneMelee)
            end
        elseif ai:GetRequireEn_QbNum(TARGET_SELF) > 1 then
            f7_local0[9051] = 10
            EZOP_ExecInterruptAction(ai, f7_local0)
        end
    end
    if (ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_S) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_L) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_BlowAway) or ai:GetInterruptResult_TransitionAiActType(AiActionType_Damage_GuardBreak)) and ai:IsFinishTimer(f0_local2._CT_InterruptAB) then
        f7_local0[1550] = 100
        ai:SetTimer(f0_local2._CT_InterruptAB, f0_local3._CT_InterruptAB)
        EZOP_ExecInterruptAction(ai, f7_local0)
    end
end

local f0_local22 = function(ai, f8_arg1, f8_arg2, f8_arg3)
    local f8_local0 = {}
    local distance = ai:GetOriginDist(TARGET_ENE_0)
    if (ai:GetInterruptResult_TransitionAiActType(AiActionType_AI_StopShot1_ADS_Start) or ai:GetInterruptResult_TransitionAiActType(AiActionType_AI_StopShot2_ADS_Start)) and distance < 500 and ai:IsLanding() then
        f8_local0[5000] = 25
        EZOP_ExecInterruptAction(ai, f8_local0)
    end
end

local f0_local23 = function(ai, f9_arg1, f9_arg2, f9_arg3)
    local f9_local0 = {}
    if ai:IsInterupt(INTERUPT_DangerousBullet) then
        local f9_local1 = ai:GetDangerousBulletLandingTime(0)
        local f9_local2 = ai:GetDangerousBulletDistance(0)
        local f9_local3 = ai:GetDangerousBulletAngle(0)
        local f9_local4 = ai:GetDangerousBulletAngleFromSelf(0)
        local f9_local5 = ai:GetDangerousBulletAngleFromBullet(0)
        local f9_local6 = ai:GetDangerousBulletParamId(0)
        local f9_local7 = EZOP_GetDBRiskCategori(ai, 0)
        local distance = ai:GetOriginDist(TARGET_ENE_0)
        local f9_local9 = ai:GetHeightFromDummyPoly(TARGET_ENE_0, 220)
        local f9_local10 = ai:GetNumber(f0_local1._BattleSituation)
        local f9_local11 = ai:GetEnRate(TARGET_SELF)
        local hpRate = ai:GetHpRate(TARGET_SELF)
        local f9_local13 = ai:GetDangerousBulletRisk(0)
        local f9_local14 = not (f9_local13 ~= EZOP_DBC._Single_BigExp and f9_local13 ~= EZOP_DBC._Single_HiSpeed and f9_local13 ~= EZOP_DBC._Single_LowSpeed)
        local f9_local15 = not (f9_local13 ~= EZOP_DBC._Missile)
        local f9_local16 = not (f9_local13 ~= EZOP_DBC._ShortRange and f9_local13 ~= EZOP_DBC._Rapid)
        if EZOP_IsNpcAcAssultBoosting(ai) then
            if f9_local14 then
                if ai:GetRequireEn_QbNum(TARGET_SELF) > 1 then
                    f9_local0[1555] = 10
                    EZOP_ExecInterruptAction(ai, f9_local0)
                end
            elseif f9_local15 and ai:GetRequireEn_QbNum(TARGET_SELF) > 1 and f9_local1 < 0.5 then
                f9_local0[1555] = 10
                EZOP_ExecInterruptAction(ai, f9_local0)
                if false then
                end
            end
        elseif f9_local14 then
            if ai:GetRequireEn_QbNum(TARGET_SELF) > 1 then
                f9_local0[9050] = 10
                EZOP_ExecInterruptAction(ai, f9_local0)
            end
        elseif f9_local16 then
            if ai:GetRequireEn_QbNum(TARGET_SELF) > 1 and ai:GetImpactGaugeValue(TARGET_SELF, DAMAGE_LEVEL_Damage_L) > 0.4 and f9_local5 <= 5 and (distance < 500 or hpRate < 0.3) then
                if f9_local9 < 25 then
                    f9_local0[1210] = 50
                    f9_local0[9050] = 10
                    EZOP_ExecInterruptAction(ai, f9_local0)
                else
                    f9_local0[9050] = 10
                    EZOP_ExecInterruptAction(ai, f9_local0)
                end
            end
        elseif f9_local15 then
            if ai:GetRequireEn_QbNum(TARGET_SELF) > 1 and f9_local1 < 0.5 and ai:GetImpactGaugeValue(TARGET_SELF, DAMAGE_LEVEL_Damage_L) > 0.4 then
                if f9_local9 < 25 then
                    f9_local0[1210] = 50
                    f9_local0[9050] = 10
                    EZOP_ExecInterruptAction(ai, f9_local0)
                else
                    f9_local0[9050] = 10
                    EZOP_ExecInterruptAction(ai, f9_local0)
                end
            end
        elseif ai:GetRequireEn_QbNum(TARGET_SELF) > 1 and ai:GetImpactGaugeValue(TARGET_SELF, DAMAGE_LEVEL_Damage_L) > 0.7 and ai:GetRequireEn_QbNum(TARGET_SELF) > 1 then
            if f9_local9 < 25 then
                f9_local0[1210] = 50
                f9_local0[9050] = 10
                EZOP_ExecInterruptAction(ai, f9_local0)
            else
                f9_local0[9050] = 10
                EZOP_ExecInterruptAction(ai, f9_local0)
            end
        end
    end
end

local f0_local24 = {
    [1] = function(f10_arg0, f10_arg1)
        local f10_local0 = EZOPArray.new()
        f10_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        f10_local0:Add(EZOP_SetAct_Wait(f10_arg0, 1, TARGET_SELF))
        return f10_local0
    end,
    [100] = function(f11_arg0, f11_arg1)
        local f11_local0 = EZOPArray.new()
        f11_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f11_local1 = 5
        local f11_local2 = TARGET_ENE_0
        local f11_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f11_local4 = EZOP_MOVETYPE._WALK
        local f11_local5 = 50
        local f11_local6 = {}

        local f11_local7 = function(f12_arg0)
            EZOP_UseInterrupt(f12_arg0, INTERUPT_DangerousBullet)
        end

        local f11_local8 = f0_local23
        local f11_local9 = true
        f11_local0:Add(EZOP_SetAct_ApproachTarget(f11_arg0, f11_local1, f11_local2, f11_local3, f11_local4, f11_local5,
            f11_local6, f11_local7, f11_local8, TransAct, f11_local9))
        return f11_local0
    end,
    [110] = function(f13_arg0, f13_arg1)
        local f13_local0 = EZOPArray.new()
        f13_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f13_local1 = 5
        local f13_local2 = TARGET_ENE_0
        local f13_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f13_local4 = EZOP_MOVETYPE._WALK
        local f13_local5 = 300
        local f13_local6 = {}

        local f13_local7 = function(f14_arg0)
            EZOP_UseInterrupt(f14_arg0, INTERUPT_DangerousBullet)
        end

        local f13_local8 = f0_local23
        local f13_local9 = true
        f13_local0:Add(EZOP_SetAct_LeaveTarget(f13_arg0, f13_local1, f13_local2, f13_local3, f13_local4, f13_local5,
            f13_local6, f13_local7, f13_local8, TransAct, f13_local9))
        return f13_local0
    end,
    [120] = function(f15_arg0, f15_arg1)
        local f15_local0 = EZOPArray.new()
        f15_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f15_local1 = 5
        local f15_local2 = TARGET_ENE_0
        local f15_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f15_local4 = EZOP_MOVETYPE._WALK
        local f15_local5 = false
        local f15_local6 = {}

        local f15_local7 = function(f16_arg0)

        end

        local f15_local8 = nil
        local f15_local9 = true
        f15_local0:Add(EZOP_SetAct_SideWayMove(f15_arg0, f15_local1, f15_local2, f15_local3, f15_local4, f15_local5,
            f15_local6, f15_local7, f15_local8, TransAct, f15_local9))
        return f15_local0
    end,
    [150] = function(f17_arg0, f17_arg1)
        local f17_local0 = EZOPArray.new()
        f17_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f17_local1 = 3
        local f17_local2 = TARGET_ENE_0
        local f17_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f17_local4 = EZOP_MOVETYPE._WALK
        local f17_local5 = true
        local f17_local6 = {}

        local f17_local7 = function(f18_arg0)
            EZOP_UseInterrupt(f18_arg0, INTERUPT_DangerousBullet)
        end

        local f17_local8 = f0_local23
        local f17_local9 = true
        if f17_arg0:GetRandam_Int(0, 1) == 0 then
            f17_local5 = false
        end
        f17_local0:Add(EZOP_SetAct_SideWayMove(f17_arg0, f17_local1, f17_local2, f17_local3, f17_local4, f17_local5,
            f17_local6, f17_local7, f17_local8, TransAct, f17_local9))
        return f17_local0
    end,
    [200] = function(f19_arg0, f19_arg1)
        local f19_local0 = EZOPArray.new()
        f19_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f19_local1 = 1.2
        local f19_local2 = TARGET_ENE_0
        local f19_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f19_local4 = EZOP_MOVETYPE._BOOST
        local f19_local5 = 10
        local f19_local6 = {}

        local f19_local7 = function(f20_arg0)
            EZOP_UseInterrupt(f20_arg0, INTERUPT_DangerousBullet)
        end

        local f19_local8 = { f0_local23, f0_local21 }
        local f19_local9 = true
        f19_local0:Add(EZOP_SetAct_ApproachTarget(f19_arg0, f19_local1, f19_local2, f19_local3, f19_local4, f19_local5,
            f19_local6, f19_local7, f19_local8, TransAct, f19_local9))
        return f19_local0
    end,
    [210] = function(f21_arg0, f21_arg1)
        local f21_local0 = EZOPArray.new()
        f21_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f21_local1 = 1.2
        local f21_local2 = TARGET_ENE_0
        local f21_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f21_local4 = EZOP_MOVETYPE._BOOST
        local f21_local5 = 300
        local f21_local6 = {}

        local f21_local7 = function(f22_arg0)
            EZOP_UseInterrupt(f22_arg0, INTERUPT_DangerousBullet)
        end

        local f21_local8 = { f0_local23, f0_local21 }
        local f21_local9 = true
        f21_local0:Add(EZOP_SetAct_LeaveTarget(f21_arg0, f21_local1, f21_local2, f21_local3, f21_local4, f21_local5,
            f21_local6, f21_local7, f21_local8, TransAct, f21_local9))
        return f21_local0
    end,
    [250] = function(f23_arg0, f23_arg1)
        local f23_local0 = EZOPArray.new()
        f23_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f23_local1 = 1.2
        local f23_local2 = TARGET_ENE_0
        local f23_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f23_local4 = EZOP_MOVETYPE._BOOST
        local f23_local5 = false
        local f23_local6 = {}

        local f23_local7 = function(f24_arg0)
            EZOP_UseInterrupt(f24_arg0, INTERUPT_DangerousBullet)
        end

        local f23_local8 = { f0_local22, f0_local23 }
        local f23_local9 = true
        if f23_arg0:GetRandam_Int(0, 1) == 0 then
            f23_local5 = true
        end
        f23_local0:Add(EZOP_SetAct_SideWayMove(f23_arg0, f23_local1, f23_local2, f23_local3, f23_local4, f23_local5,
            f23_local6, f23_local7, f23_local8, TransAct, f23_local9))
        return f23_local0
    end,
    [350] = function(f25_arg0, f25_arg1)
        local f25_local0 = EZOPArray.new()
        f25_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f25_local1 = 1.2
        local f25_local2 = TARGET_ENE_0
        local f25_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f25_local4 = EZOP_MOVETYPE._BOOST
        local f25_local5 = false
        local f25_local6 = {}

        local f25_local7 = function(f26_arg0)
            EZOP_UseInterrupt(f26_arg0, INTERUPT_DangerousBullet)
        end

        local f25_local8 = { f0_local23, f0_local21 }
        local f25_local9 = true
        local f25_local10 = f25_arg0:GetAngleAtoB(TARGET_SELF, TARGET_EVENT)
        if f25_local10 <= 180 then
            f25_local5 = true
        end
        f25_local0:Add(EZOP_SetAct_SideWayMove(f25_arg0, f25_local1, f25_local2, f25_local3, f25_local4, f25_local5,
            f25_local6, f25_local7, f25_local8, TransAct, f25_local9))
        return f25_local0
    end,
    [1000] = function(f27_arg0, f27_arg1)
        local f27_local0 = EZOPArray.new()
        if f27_arg0:IsLanding() then
            f27_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        else
            f27_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        end
        local f27_local1 = 1.5
        local f27_local2 = TARGET_ENE_0
        local f27_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f27_local4 = EZOP_MOVETYPE._BOOST
        local f27_local5 = 10
        local f27_local6 = f0_local19(f27_arg0, f27_local2, f0_local8._AtkOp_ShoulderMissileLR)

        local f27_local7 = function(f28_arg0)
            EZOP_UseInterrupt(f28_arg0, INTERUPT_DangerousBullet)
        end

        local f27_local8 = { f0_local22, f0_local23, f0_local21 }
        local f27_local9 = true
        f27_local0:Add(EZOP_SetAct_ApproachTarget(f27_arg0, f27_local1, f27_local2, f27_local3, f27_local4, f27_local5,
            f27_local6, f27_local7, f27_local8, TransAct, f27_local9))
        return f27_local0
    end,
    [1010] = function(f29_arg0, f29_arg1)
        local f29_local0 = EZOPArray.new()
        if f29_arg0:IsLanding() then
            f29_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        else
            f29_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        end
        local f29_local1 = 3
        local f29_local2 = TARGET_ENE_0
        local f29_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f29_local4 = EZOP_MOVETYPE._BOOST
        local f29_local5 = true
        if f29_arg0:GetRandam_Int(0, 1) == 1 then
            f29_local5 = false
        end
        local f29_local6 = f0_local19(f29_arg0, f29_local2, f0_local8._AtkOp_ShoulderMissileLR)

        local f29_local7 = function(f30_arg0)
            EZOP_UseInterrupt(f30_arg0, INTERUPT_DangerousBullet)
        end

        local f29_local8 = { f0_local22, f0_local23, f0_local21 }
        local f29_local9 = true
        f29_local0:Add(EZOP_SetAct_SideWayMove(f29_arg0, f29_local1, f29_local2, f29_local3, f29_local4, f29_local5,
            f29_local6, f29_local7, f29_local8, TransAct, f29_local9))
        return f29_local0
    end,
    [1011] = function(f31_arg0, f31_arg1)
        local f31_local0 = EZOPArray.new()
        if f31_arg0:IsLanding() then
            f31_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        else
            f31_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        end
        local f31_local1 = 3
        local f31_local2 = TARGET_ENE_0
        local f31_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f31_local4 = EZOP_MOVETYPE._BOOST
        local f31_local5 = true
        if f31_arg0:GetRandam_Int(0, 1) == 1 then
            f31_local5 = false
        end
        local f31_local6 = f0_local19(f31_arg0, f31_local2, f0_local8._AtkOp_HandMissileOneSide)

        local f31_local7 = function(f32_arg0)
            EZOP_UseInterrupt(f32_arg0, INTERUPT_DangerousBullet)
        end

        local f31_local8 = { f0_local22, f0_local23, f0_local21 }
        local f31_local9 = true
        f31_local0:Add(EZOP_SetAct_SideWayMove(f31_arg0, f31_local1, f31_local2, f31_local3, f31_local4, f31_local5,
            f31_local6, f31_local7, f31_local8, TransAct, f31_local9))
        return f31_local0
    end,
    [1030] = function(f33_arg0, f33_arg1)
        local f33_local0 = EZOPArray.new()
        if f33_arg0:IsLanding() then
            f33_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        else
            f33_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        end
        local f33_local1 = 1.5
        local f33_local2 = TARGET_ENE_0
        local f33_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f33_local4 = EZOP_MOVETYPE._BOOST
        local f33_local5 = 200
        local f33_local6 = f0_local19(f33_arg0, f33_local2, f0_local8._AtkOp_ShoulderMissileOneSide)

        local f33_local7 = function(f34_arg0)
            EZOP_UseInterrupt(f34_arg0, INTERUPT_DangerousBullet)
        end

        local f33_local8 = { f0_local22, f0_local23, f0_local21 }
        local f33_local9 = true
        f33_local0:Add(EZOP_SetAct_LeaveTarget(f33_arg0, f33_local1, f33_local2, f33_local3, f33_local4, f33_local5,
            f33_local6, f33_local7, f33_local8, TransAct, f33_local9))
        return f33_local0
    end,
    [1031] = function(f35_arg0, f35_arg1)
        local f35_local0 = EZOPArray.new()
        if f35_arg0:IsLanding() then
            f35_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        else
            f35_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        end
        local f35_local1 = 1.5
        local f35_local2 = TARGET_ENE_0
        local f35_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f35_local4 = EZOP_MOVETYPE._BOOST
        local f35_local5 = 200
        local f35_local6 = f0_local19(f35_arg0, f35_local2, f0_local8._AtkOp_HandMissileOneSide)

        local f35_local7 = function(f36_arg0)
            EZOP_UseInterrupt(f36_arg0, INTERUPT_DangerousBullet)
        end

        local f35_local8 = { f0_local22, f0_local23, f0_local21 }
        local f35_local9 = true
        f35_local0:Add(EZOP_SetAct_LeaveTarget(f35_arg0, f35_local1, f35_local2, f35_local3, f35_local4, f35_local5,
            f35_local6, f35_local7, f35_local8, TransAct, f35_local9))
        return f35_local0
    end,
    [1100] = function(f37_arg0, f37_arg1)
        local f37_local0 = EZOPArray.new()
        local f37_local1 = 5
        local f37_local2 = TARGET_ENE_0
        local f37_local3 = 180
        local f37_local4 = f0_local19(f37_arg0, f37_local2, f0_local8._AtkOp_HandMissileLR)

        local f37_local5 = function(f38_arg0)

        end

        local f37_local6 = {}
        local f37_local7 = ChkFunc_HAGI_InsideRange
        local f37_local8 = { 0, 360, 0, 9999 }
        f37_local0:Add(EZOP_SetAct_QuickBoost(f37_arg0, f37_local1, f37_local2, f37_local3, f37_local4, f37_local7,
            f37_local8, f37_local5, f37_local6, TransAct))
        return f37_local0
    end,
    [1110] = function(f39_arg0, f39_arg1)
        local f39_local0 = EZOPArray.new()
        local f39_local1 = 5
        local f39_local2 = TARGET_ENE_0
        local f39_local3 = 0
        local f39_local4 = f0_local19(f39_arg0, f39_local2, f0_local8._AtkOp_HandMissileLR)

        local f39_local5 = function(f40_arg0)

        end

        local f39_local6 = {}
        local f39_local7 = ChkFunc_HAGI_InsideRange
        local f39_local8 = { 0, 360, 0, 9999 }
        f39_local0:Add(EZOP_SetAct_QuickBoost(f39_arg0, f39_local1, f39_local2, f39_local3, f39_local4, f39_local7,
            f39_local8, f39_local5, f39_local6, TransAct))
        return f39_local0
    end,
    [1150] = function(ai, f41_arg1)
        local f41_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 1)
        ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f41_local2 = TARGET_ENE_0
        local f41_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f41_local4 = EZOP_MOVETYPE._BOOST
        local f41_local5 = false

        local f41_local6 = function(f42_arg0)
            EZOP_UseInterrupt(f42_arg0, INTERUPT_DangerousBullet)
        end

        local f41_local7 = { f0_local23, f0_local21 }
        local f41_local8 = true
        if ai:GetRandam_Int(0, 1) == 0 then
            f41_local5 = true
        end
        if ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            if random == 0 then
                local f41_local9 = 1.5
                local f41_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local12, 0, 0, 0, 0.04, -1),
                    EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local13, 0, 0, 0, 0.04, -1) }
                f41_local0:Add(EZOP_SetAct_SideWayMove(ai, f41_local9, f41_local2, f41_local3, f41_local4, f41_local5,
                    f41_local10, f41_local6, f41_local7, TransAct, f41_local8))
            elseif random == 1 then
                local f41_local9 = 3
                local f41_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local12, 0, 0, 0, 0.04, -1),
                    EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local14, 1.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
                f41_local2, f0_local13, 0, 0, 0, 0.04, -1) }
                f41_local0:Add(EZOP_SetAct_SideWayMove(ai, f41_local9, f41_local2, f41_local3, f41_local4, f41_local5,
                    f41_local10, f41_local6, f41_local7, TransAct, f41_local8))
            end
        elseif random == 0 then
            local f41_local9 = 1.5
            local f41_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local12, 0, 0, 0, 0.04, -1) }
            f41_local0:Add(EZOP_SetAct_SideWayMove(ai, f41_local9, f41_local2, f41_local3, f41_local4, f41_local5,
                f41_local10, f41_local6, f41_local7, TransAct, f41_local8))
        elseif random == 1 then
            local f41_local9 = 3
            local f41_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f41_local2, f0_local14, 1.5, 1, 0, 0, -1) }
            f41_local0:Add(EZOP_SetAct_SideWayMove(ai, f41_local9, f41_local2, f41_local3, f41_local4, f41_local5,
                f41_local10, f41_local6, f41_local7, TransAct, f41_local8))
        end
        return f41_local0
    end,
    [1200] = function(f43_arg0, f43_arg1)
        local f43_local0 = EZOPArray.new()
        local f43_local1 = f43_arg0:GetHeightFromGround(TARGET_ENE_0)
        f43_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f43_local2 = 1.5
        local f43_local3 = TARGET_ENE_0
        local f43_local4 = 0
        local f43_local5 = 90
        local f43_local6 = f43_local1 + f43_arg0:GetRandam_Float(30, 35)
        local f43_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f43_local8 = EZOP_MOVETYPE._BOOST
        local f43_local9 = 10
        local f43_local10 = f0_local19(f43_arg0, f43_local3, f0_local8._AtkOp_ShoulderMissileLR)

        local f43_local11 = function(f44_arg0)
            EZOP_UseInterrupt(f44_arg0, INTERUPT_DangerousBullet)
        end

        local f43_local12 = { f0_local23, f0_local21 }
        local f43_local13 = true
        f43_local0:Add(EZOP_SetAct_ApproachBoostRise(f43_arg0, f43_local2, f43_local3, f43_local4, f43_local5, f43_local6,
            f43_local7, f43_local8, f43_local9, f43_local10, f43_local11, f43_local12, ChkFunc, ChkParam, TransAct,
            f43_local13))
        local f43_local14 = 90
        if f43_arg0:GetRandam_Int(0, 1) == 1 then
            f43_local14 = f43_local14 * -1
        end
        local f43_local15 = 200
        f43_local0:Add(EZOP_SetAct_ApproachBoostRise(f43_arg0, f43_local2, f43_local3, f43_local14, f43_local15,
            f43_local6, f43_local7, f43_local8, f43_local9, f43_local10, f43_local11, f43_local12, ChkFunc, ChkParam,
            TransAct, f43_local13))
        return f43_local0
    end,
    [1210] = function(f45_arg0, f45_arg1)
        local f45_local0 = EZOPArray.new()
        local f45_local1 = f45_arg0:GetHeightFromGround(TARGET_ENE_0)
        f45_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f45_local2 = 1.5
        local f45_local3 = TARGET_ENE_0
        local f45_local4 = 90
        if f45_arg0:GetRandam_Int(0, 1) == 1 then
            f45_local4 = f45_local4 * -1
        end
        local f45_local5 = 200
        local f45_local6 = f45_local1 + f45_arg0:GetRandam_Float(30, 35)
        local f45_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f45_local8 = EZOP_MOVETYPE._BOOST
        local f45_local9 = 10
        local f45_local10 = f0_local19(f45_arg0, f45_local3, f0_local8._AtkOp_HandMissileOneSide)

        local f45_local11 = function(f46_arg0)
            EZOP_UseInterrupt(f46_arg0, INTERUPT_DangerousBullet)
        end

        local f45_local12 = { f0_local23, f0_local21 }
        local f45_local13 = true
        f45_local0:Add(EZOP_SetAct_ApproachBoostRise(f45_arg0, f45_local2, f45_local3, f45_local4, f45_local5, f45_local6,
            f45_local7, f45_local8, f45_local9, f45_local10, f45_local11, f45_local12, ChkFunc, ChkParam, TransAct,
            f45_local13))
        f45_local0:Add(EZOP_SetAct_ApproachBoostRise(f45_arg0, f45_local2, f45_local3, f45_local4, f45_local5, f45_local6,
            f45_local7, f45_local8, f45_local9, f45_local10, f45_local11, f45_local12, ChkFunc, ChkParam, TransAct,
            f45_local13))
        return f45_local0
    end,
    [1220] = function(f47_arg0, f47_arg1)
        local f47_local0 = EZOPArray.new()
        local f47_local1 = f47_arg0:GetHeightFromGround(TARGET_ENE_0)
        f47_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f47_local2 = 1.5
        local f47_local3 = TARGET_ENE_0
        local f47_local4 = 0
        local f47_local5 = 300
        local f47_local6 = f47_local1 + f47_arg0:GetRandam_Float(30, 35)
        local f47_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f47_local8 = EZOP_MOVETYPE._BOOST
        local f47_local9 = 10
        local f47_local10 = f0_local19(f47_arg0, f47_local3, f0_local8._AtkOp_HandMissileLR)

        local f47_local11 = function(f48_arg0)
            EZOP_UseInterrupt(f48_arg0, INTERUPT_DangerousBullet)
        end

        local f47_local12 = { f0_local23, f0_local21 }
        local f47_local13 = true
        f47_local0:Add(EZOP_SetAct_ApproachBoostRise(f47_arg0, f47_local2, f47_local3, f47_local4, f47_local5, f47_local6,
            f47_local7, f47_local8, f47_local9, f47_local10, f47_local11, f47_local12, ChkFunc, ChkParam, TransAct,
            f47_local13))
        local f47_local14 = 2
        local f47_local15 = 90
        if f47_arg0:GetRandam_Int(0, 1) == 1 then
            f47_local15 = f47_local15 * -1
        end
        local f47_local16 = 200
        f47_local0:Add(EZOP_SetAct_ApproachBoostRise(f47_arg0, f47_local14, f47_local3, f47_local15, f47_local16,
            f47_local6, f47_local7, f47_local8, f47_local9, f47_local10, f47_local11, f47_local12, ChkFunc, ChkParam,
            TransAct, f47_local13))
        return f47_local0
    end,
    [1250] = function(ai, f49_arg1)
        local f49_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 2)
        local f49_local2 = ai:GetHeight(TARGET_ENE_0)
        ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f49_local3 = TARGET_ENE_0
        local f49_local4 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f49_local5 = 90
        local f49_local6 = 150
        local f49_local7 = f49_local2 + 75
        local f49_local8 = EZOP_MOVETYPE._BOOST
        local f49_local9 = 10

        local f49_local10 = function(f50_arg0)
            EZOP_UseInterrupt(f50_arg0, INTERUPT_DangerousBullet)
        end

        local f49_local11 = { f0_local23, f0_local21 }
        local f49_local12 = true
        if ai:GetRandam_Int(0, 1) == 0 then
            f49_local5 = f49_local5 * -1
        end
        if ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            if random == 0 or random == 1 then
                local f49_local13 = 1.5
                local f49_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local12, 0, 0, 0, 0.04, -1),
                    EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local13, 0, 0, 0, 0.04, -1) }
                f49_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f49_local13, f49_local3, f49_local5, f49_local6,
                    f49_local7, f49_local4, f49_local8, f49_local9, f49_local14, f49_local10, f49_local11, ChkFunc,
                    ChkParam, TransAct, f49_local12))
            elseif random == 2 then
                local f49_local13 = 3
                local f49_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local12, 0, 0, 0, 0.04, -1),
                    EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local14, 1.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
                f49_local3, f0_local13, 0, 0, 0, 0.04, -1) }
                f49_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f49_local13, f49_local3, f49_local5, f49_local6,
                    f49_local7, f49_local4, f49_local8, f49_local9, f49_local14, f49_local10, f49_local11, ChkFunc,
                    ChkParam, TransAct, f49_local12))
            end
        elseif random == 0 then
            local f49_local13 = 1.5
            local f49_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local12, 0, 0, 0, 0.04, -1) }
            f49_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f49_local13, f49_local3, f49_local5, f49_local6, f49_local7,
                f49_local4, f49_local8, f49_local9, f49_local14, f49_local10, f49_local11, ChkFunc, ChkParam, TransAct,
                f49_local12))
        elseif random == 1 then
            local f49_local13 = 3
            local f49_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local14, 1.5, 1, 0, 0, -1) }
            f49_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f49_local13, f49_local3, f49_local5, f49_local6, f49_local7,
                f49_local4, f49_local8, f49_local9, f49_local14, f49_local10, f49_local11, ChkFunc, ChkParam, TransAct,
                f49_local12))
        elseif random == 2 then
            local f49_local13 = 2.5
            local f49_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f49_local3, f0_local14, 1, 1, 0, 0, -1) }
            f49_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f49_local13, f49_local3, f49_local5, f49_local6, f49_local7,
                f49_local4, f49_local8, f49_local9, f49_local14, f49_local10, f49_local11, ChkFunc, ChkParam, TransAct,
                f49_local12))
        end
        return f49_local0
    end,
    [1500] = function(f51_arg0, f51_arg1)
        local f51_local0 = EZOPArray.new()
        local f51_local1 = 2
        local f51_local2 = TARGET_ENE_0
        local f51_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f51_local4 = EZOP_MOVETYPE._BOOST
        local f51_local5 = 90
        local f51_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f51_local2, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f51_local2, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f51_local2,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f51_local2, f0_local14, 0, 10, 0, 0.04, -1) }

        local f51_local7 = function(f52_arg0)
            EZOP_UseInterrupt(f52_arg0, INTERUPT_DangerousBullet)
        end

        local f51_local8 = { f0_local22, f0_local23, f0_local21 }
        local f51_local9 = true
        f51_local0:Add(EZOP_SetAct_ApproachTarget(f51_arg0, f51_local1, f51_local2, f51_local3, f51_local4, f51_local5,
            f51_local6, f51_local7, f51_local8, ChkFunc, ChkParam, TransAct, f51_local9))
        return f51_local0
    end,
    [1510] = function(f53_arg0, f53_arg1)
        local f53_local0 = EZOPArray.new()
        local f53_local1 = 2
        local f53_local2 = TARGET_ENE_0
        local f53_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f53_local4 = EZOP_MOVETYPE._BOOST
        local f53_local5 = false
        if f53_arg0:GetRandam_Int(0, 1) == 0 then
            f53_local5 = true
        end
        local f53_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f53_local2, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f53_local2, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f53_local2,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f53_local2, f0_local14, 0, 10, 0, 0.04, -1) }

        local f53_local7 = function(f54_arg0)
            EZOP_UseInterrupt(f54_arg0, INTERUPT_DangerousBullet)
        end

        local f53_local8 = { f0_local22, f0_local23, f0_local21 }
        local f53_local9 = true
        f53_local0:Add(EZOP_SetAct_SideWayMove(f53_arg0, f53_local1, f53_local2, f53_local3, f53_local4, f53_local5,
            f53_local6, f53_local7, f53_local8, TransAct, f53_local9))
        return f53_local0
    end,
    [1520] = function(f55_arg0, f55_arg1)
        local f55_local0 = EZOPArray.new()
        local f55_local1 = 2
        local f55_local2 = TARGET_ENE_0
        local f55_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f55_local4 = EZOP_MOVETYPE._BOOST
        local f55_local5 = 300
        local f55_local6 = { EZOP_MakeAtkOp_NpcAcShoot(f55_local2, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f55_local2, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f55_local2,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f55_local2, f0_local14, 0, 10, 0, 0.04, -1) }

        local f55_local7 = function(f56_arg0)
            EZOP_UseInterrupt(f56_arg0, INTERUPT_DangerousBullet)
        end

        local f55_local8 = { f0_local22, f0_local23, f0_local21 }
        local f55_local9 = true
        f55_local0:Add(EZOP_SetAct_LeaveTarget(f55_arg0, f55_local1, f55_local2, f55_local3, f55_local4, f55_local5,
            f55_local6, f55_local7, f55_local8, ChkFunc, ChkParam, TransAct, f55_local9))
        return f55_local0
    end,
    [1550] = function(f57_arg0, f57_arg1)
        local f57_local0 = EZOPArray.new()
        local f57_local1 = 7
        local f57_local2 = TARGET_ENE_0
        local f57_local3 = 0
        local f57_local4 = -1
        local f57_local5 = 70
        local f57_local6 = -1
        local f57_local7 = -1
        local f57_local8 = true
        local f57_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f57_local2, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f57_local2, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f57_local2,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f57_local2, f0_local14, 0, 10, 0, 0.04, -1) }
        local f57_local10 = ChkFunc_HAGI_InsideRange
        local f57_local11 = { 0, 240, 0, 150 }

        local f57_local12 = function(f58_arg0)
            EZOP_UseInterrupt(f58_arg0, INTERUPT_DangerousBullet)
        end

        local f57_local13 = { f0_local23 }
        f57_local0:Add(EZOP_SetAct_NPC_AssultBoost(f57_arg0, f57_local1, f57_local2, f57_local3, f57_local4, f57_local5,
            f57_local6, f57_local7, f57_local8, f57_local9, f57_local10, f57_local11, f57_local12, f57_local13, TransAct))
        local f57_local14 = 70
        local f57_local15 = -1
        local f57_local16 = nil
        local f57_local17 = nil
        f57_local0:Add(EZOP_SetAct_NPC_AssultBoost(f57_arg0, f57_local1, f57_local2, f57_local3, f57_local14, f57_local15,
            f57_local6, f57_local7, f57_local8, f57_local9, f57_local10, f57_local11, f57_local16, f57_local17, TransAct))
        if f57_arg0:GetNumber(f0_local1._Count_AA) < 3 and f57_arg0:IsFinishTimer(f0_local2._CT_LmtrRls) then
            local f57_local18 = 0.5
            local f57_local19 = TARGET_ENE_0
            local f57_local20 = { EZOP_MakeAtkOp_NpcAcShoot(f57_local19, f0_local16, 0, 1, 0, 0, -1) }
            f57_local0:Add(EZOP_SetAct_StandShoot(f57_arg0, f57_local18, f57_local19, f57_local20))
            f57_local0:Add(EZOP_SetAct_StandShoot(f57_arg0, 3, f57_local19, f57_local20))
        end
        return f57_local0
    end,
    [1555] = function(f59_arg0, f59_arg1)
        local f59_local0 = EZOPArray.new()
        local f59_local1 = 3
        local f59_local2 = TARGET_ENE_0
        local f59_local3 = 90
        if f59_arg0:GetRandam_Int(0, 1) == 1 then
            f59_local3 = f59_local3 * -1
        end
        local f59_local4 = -1
        local f59_local5 = -1
        local f59_local6 = -1
        local f59_local7 = -1
        local f59_local8 = true
        local f59_local9 = {}
        local f59_local10 = ChkFunc_HAGI_InsideRange
        local f59_local11 = { 0, 240, 0, 9999 }
        local f59_local12 = nil
        local f59_local13 = nil
        f59_local0:Add(EZOP_SetAct_NPC_AssultBoost(f59_arg0, f59_local1, f59_local2, f59_local3, f59_local4, f59_local5,
            f59_local6, f59_local7, f59_local8, f59_local9, f59_local10, f59_local11, f59_local12, f59_local13, TransAct))
        local f59_local14 = 7
        local f59_local15 = 0
        local f59_local16 = 70
        local f59_local17 = { EZOP_MakeAtkOp_NpcAcShoot(f59_local2, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f59_local2, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f59_local2,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f59_local2, f0_local14, 0, 10, 0, 0.04, -1) }
        local f59_local18 = ChkFunc_HAGI_InsideRange
        local f59_local19 = { 0, 240, 0, 150 }
        f59_local0:Add(EZOP_SetAct_NPC_AssultBoost(f59_arg0, f59_local14, f59_local2, f59_local15, f59_local4,
            f59_local16, f59_local6, f59_local7, f59_local8, f59_local17, f59_local18, f59_local19, f59_local12,
            f59_local13, TransAct))
        local f59_local20 = 70
        local f59_local21 = -1
        f59_local0:Add(EZOP_SetAct_NPC_AssultBoost(f59_arg0, f59_local14, f59_local2, f59_local15, f59_local20,
            f59_local21, f59_local6, f59_local7, f59_local8, f59_local17, f59_local18, f59_local19, f59_local12,
            f59_local13, TransAct))
        if f59_arg0:GetNumber(f0_local1._Count_AA) < 3 and f59_arg0:IsFinishTimer(f0_local2._CT_LmtrRls) then
            local f59_local22 = 0.5
            local f59_local23 = TARGET_ENE_0
            local f59_local24 = { EZOP_MakeAtkOp_NpcAcShoot(f59_local23, f0_local16, 0, 1, 0, 0, -1) }
            f59_local0:Add(EZOP_SetAct_StandShoot(f59_arg0, f59_local22, f59_local23, f59_local24))
            f59_local0:Add(EZOP_SetAct_StandShoot(f59_arg0, 3, f59_local23, f59_local24))
        end
        return f59_local0
    end,
    [1600] = function(f60_arg0, f60_arg1)
        local f60_local0 = EZOPArray.new()
        local f60_local1 = f60_arg0:GetHeightFromGround(TARGET_ENE_0)
        f60_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f60_local2 = 1.5
        local f60_local3 = TARGET_ENE_0
        local f60_local4 = 0
        local f60_local5 = 90
        local f60_local6 = f60_local1 + f60_arg0:GetRandam_Float(30, 35)
        local f60_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f60_local8 = EZOP_MOVETYPE._BOOST
        local f60_local9 = 10
        local f60_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f60_local3, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f60_local3, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f60_local3,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f60_local3, f0_local14, 0, 10, 0, 0.04, -1) }

        local f60_local11 = function(f61_arg0)
            EZOP_UseInterrupt(f61_arg0, INTERUPT_DangerousBullet)
        end

        local f60_local12 = { f0_local23, f0_local21 }
        local f60_local13 = true
        f60_local0:Add(EZOP_SetAct_ApproachBoostRise(f60_arg0, f60_local2, f60_local3, f60_local4, f60_local5, f60_local6,
            f60_local7, f60_local8, f60_local9, f60_local10, f60_local11, f60_local12, ChkFunc, ChkParam, TransAct,
            f60_local13))
        local f60_local14 = 90
        if f60_arg0:GetRandam_Int(0, 1) == 1 then
            f60_local14 = f60_local14 * -1
        end
        local f60_local15 = 200
        f60_local0:Add(EZOP_SetAct_ApproachBoostRise(f60_arg0, f60_local2, f60_local3, f60_local14, f60_local15,
            f60_local6, f60_local7, f60_local8, f60_local9, f60_local10, f60_local11, f60_local12, ChkFunc, ChkParam,
            TransAct, f60_local13))
        return f60_local0
    end,
    [1610] = function(f62_arg0, f62_arg1)
        local f62_local0 = EZOPArray.new()
        local f62_local1 = f62_arg0:GetHeightFromGround(TARGET_ENE_0)
        f62_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f62_local2 = 1.5
        local f62_local3 = TARGET_ENE_0
        local f62_local4 = 90
        if f62_arg0:GetRandam_Int(0, 1) == 1 then
            f62_local4 = f62_local4 * -1
        end
        local f62_local5 = 200
        local f62_local6 = f62_local1 + f62_arg0:GetRandam_Float(30, 35)
        local f62_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f62_local8 = EZOP_MOVETYPE._BOOST
        local f62_local9 = 10
        local f62_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f62_local3, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f62_local3, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f62_local3,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f62_local3, f0_local14, 0, 10, 0, 0.04, -1) }

        local f62_local11 = function(f63_arg0)
            EZOP_UseInterrupt(f63_arg0, INTERUPT_DangerousBullet)
        end

        local f62_local12 = { f0_local23, f0_local21 }
        local f62_local13 = true
        f62_local0:Add(EZOP_SetAct_ApproachBoostRise(f62_arg0, f62_local2, f62_local3, f62_local4, f62_local5, f62_local6,
            f62_local7, f62_local8, f62_local9, f62_local10, f62_local11, f62_local12, ChkFunc, ChkParam, TransAct,
            f62_local13))
        f62_local0:Add(EZOP_SetAct_ApproachBoostRise(f62_arg0, f62_local2, f62_local3, f62_local4, f62_local5, f62_local6,
            f62_local7, f62_local8, f62_local9, f62_local10, f62_local11, f62_local12, ChkFunc, ChkParam, TransAct,
            f62_local13))
        return f62_local0
    end,
    [1620] = function(f64_arg0, f64_arg1)
        local f64_local0 = EZOPArray.new()
        local f64_local1 = f64_arg0:GetHeightFromGround(TARGET_ENE_0)
        f64_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_VOLUME)
        local f64_local2 = 1.5
        local f64_local3 = TARGET_ENE_0
        local f64_local4 = 0
        local f64_local5 = 300
        local f64_local6 = f64_local1 + f64_arg0:GetRandam_Float(30, 35)
        local f64_local7 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f64_local8 = EZOP_MOVETYPE._BOOST
        local f64_local9 = 10
        local f64_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f64_local3, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f64_local3, f0_local12, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f64_local3,
            f0_local13, 0, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f64_local3, f0_local14, 0, 10, 0, 0.04, -1) }

        local f64_local11 = function(f65_arg0)
            EZOP_UseInterrupt(f65_arg0, INTERUPT_DangerousBullet)
        end

        local f64_local12 = { f0_local23, f0_local21 }
        local f64_local13 = true
        f64_local0:Add(EZOP_SetAct_ApproachBoostRise(f64_arg0, f64_local2, f64_local3, f64_local4, f64_local5, f64_local6,
            f64_local7, f64_local8, f64_local9, f64_local10, f64_local11, f64_local12, ChkFunc, ChkParam, TransAct,
            f64_local13))
        local f64_local14 = 2
        local f64_local15 = 90
        if f64_arg0:GetRandam_Int(0, 1) == 1 then
            f64_local15 = f64_local15 * -1
        end
        local f64_local16 = 200
        f64_local0:Add(EZOP_SetAct_ApproachBoostRise(f64_arg0, f64_local14, f64_local3, f64_local15, f64_local16,
            f64_local6, f64_local7, f64_local8, f64_local9, f64_local10, f64_local11, f64_local12, ChkFunc, ChkParam,
            TransAct, f64_local13))
        return f64_local0
    end,
    [2000] = function(f66_arg0, f66_arg1)
        local f66_local0 = EZOPArray.new()
        local f66_local1 = 0.5
        local f66_local2 = TARGET_ENE_0
        local f66_local3 = { EZOP_MakeAtkOp_NpcAcShoot(f66_local2, f0_local16, 0, 1, 0, 0, -1) }
        f66_local0:Add(EZOP_SetAct_StandShoot(f66_arg0, f66_local1, f66_local2, f66_local3))
        f66_local0:Add(EZOP_SetAct_StandShoot(f66_arg0, 3, f66_local2, f66_local3))
        return f66_local0
    end,
    [2100] = function(f67_arg0, f67_arg1)
        local f67_local0 = EZOPArray.new()
        local f67_local1 = 2
        local f67_local2 = TARGET_ENE_0
        local f67_local3 = 0
        local f67_local4 = -1
        local f67_local5 = -1
        local f67_local6 = {}
        local f67_local7 = ChkFunc_HAGI_InsideRange
        local f67_local8 = { 0, 360, 0, 999 }
        f67_local0:Add(EZOP_SetAct_NPC_AssultBoost(f67_arg0, f67_local1, f67_local2, f67_local3, f67_local4, f67_local5,
            f67_local6, f67_local7, f67_local8, InterruptSetupFunc, InterruptFunc, TransAct))
        return f67_local0
    end,
    [2120] = function(f68_arg0, f68_arg1)
        local f68_local0 = EZOPArray.new()
        local f68_local1 = 2
        local f68_local2 = TARGET_ENE_0
        local f68_local3 = -90
        local f68_local4 = -1
        local f68_local5 = -1
        local f68_local6 = {}
        local f68_local7 = ChkFunc_HAGI_InsideRange
        local f68_local8 = { 0, 360, 0, 999 }
        f68_local0:Add(EZOP_SetAct_NPC_AssultBoost(f68_arg0, f68_local1, f68_local2, f68_local3, f68_local4, f68_local5,
            f68_local6, f68_local7, f68_local8, InterruptSetupFunc, InterruptFunc, TransAct))
        return f68_local0
    end,
    [2130] = function(f69_arg0, f69_arg1)
        local f69_local0 = EZOPArray.new()
        local f69_local1 = 2
        local f69_local2 = TARGET_ENE_0
        local f69_local3 = 90
        local f69_local4 = -1
        local f69_local5 = -1
        local f69_local6 = {}
        local f69_local7 = ChkFunc_HAGI_InsideRange
        local f69_local8 = { 0, 360, 0, 999 }
        f69_local0:Add(EZOP_SetAct_NPC_AssultBoost(f69_arg0, f69_local1, f69_local2, f69_local3, f69_local4, f69_local5,
            f69_local6, f69_local7, f69_local8, InterruptSetupFunc, InterruptFunc, TransAct))
        return f69_local0
    end,
    [2200] = function(f70_arg0, f70_arg1)
        local f70_local0 = EZOPArray.new()
        local f70_local1 = 15
        local f70_local2 = TARGET_ENE_0
        local f70_local3 = 0
        local f70_local4 = -1
        local f70_local5 = 25
        local f70_local6 = -1
        local f70_local7 = -1
        local f70_local8 = true
        local f70_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f70_local2, f0_local11, 0.1, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f70_local2, f0_local12, 0.1, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(
        f70_local2, f0_local13, 0.1, 10, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f70_local2, f0_local14, 0.1, 10, 0, 0.04,
            -1) }
        local f70_local10 = ChkFunc_HAGI_InsideRange
        local f70_local11 = { 0, 360, 0, 9999 }
        local f70_local12 = nil
        local f70_local13 = nil
        f70_local0:Add(EZOP_SetAct_NPC_AssultBoost(f70_arg0, f70_local1, f70_local2, f70_local3, f70_local4, f70_local5,
            f70_local6, f70_local7, f70_local8, f70_local9, f70_local10, f70_local11, f70_local12, f70_local13, TransAct))
        return f70_local0
    end,
    [2250] = function(ai, f71_arg1)
        local f71_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 1)
        local random2 = ai:GetRandam_Float(2, 3)
        local f71_local3 = TARGET_ENE_0
        local f71_local4 = 90
        local f71_local5 = -1
        local f71_local6 = -1
        local f71_local7 = ChkFunc_HAGI_InsideRange
        local f71_local8 = { 180, 240, 0, 250 }
        if ai:GetRandam_Int(0, 1) == 0 then
            f71_local4 = f71_local4 * -1
        end
        if random == 0 then
            local f71_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f71_local3, f0_local12, 0, 0, 0, 0.04, -1) }
            f71_local0:Add(EZOP_SetAct_NPC_AssultBoost(ai, random2, f71_local3, f71_local4, f71_local5, f71_local6,
                f71_local9, f71_local7, f71_local8, InterruptSetupFunc, InterruptFunc, TransAct))
        elseif random == 1 and ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            local f71_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f71_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f71_local3, f0_local13, 0, 0, 0, 0.04, -1) }
            f71_local0:Add(EZOP_SetAct_NPC_AssultBoost(ai, random2, f71_local3, f71_local4, f71_local5, f71_local6,
                f71_local9, f71_local7, f71_local8, InterruptSetupFunc, InterruptFunc, TransAct))
        end
        local f71_local9 = TARGET_ENE_0
        local f71_local10 = 1.5
        local f71_local11 = { EZOP_MakeAtkOp_NpcAcShoot(f71_local9, f0_local14, 0, 1, 0, 1, -1) }
        f71_local0:Add(EZOP_SetAct_StandShoot(ai, f71_local10, f71_local9, f71_local11))
        return f71_local0
    end,
    [3000] = function(f72_arg0, f72_arg1)
        local f72_local0 = EZOPArray.new()
        local f72_local1 = 0.1
        local f72_local2 = TARGET_ENE_0
        local f72_local3 = { EZOP_MakeAtkOp_NpcAcShoot(f72_local2, f0_local15, 0, 1, 0, 1, -1) }
        f72_local0:Add(EZOP_SetAct_StandShoot(f72_arg0, f72_local1, f72_local2, f72_local3))
        return f72_local0
    end,
    [3150] = function(ai, f73_arg1)
        local f73_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 4)
        ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f73_local2 = TARGET_ENE_0
        local f73_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f73_local4 = EZOP_MOVETYPE._BOOST
        local f73_local5 = false

        local f73_local6 = function(f74_arg0)

        end

        local f73_local7 = nil
        local f73_local8 = true
        if ai:GetRandam_Int(0, 1) == 0 then
            f73_local5 = true
        end
        if random == 0 then
            local f73_local9 = 3
            local f73_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local15, 0.5, 1, 0, 0, -1) }
            f73_local0:Add(EZOP_SetAct_SideWayMove(ai, f73_local9, f73_local2, f73_local3, f73_local4, f73_local5,
                f73_local10, f73_local6, f73_local7, TransAct, f73_local8))
        elseif random == 1 then
            local f73_local9 = 3
            local f73_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local14, 2.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f73_local2, f0_local15, 0.5, 1, 0, 0, -1) }
            f73_local0:Add(EZOP_SetAct_SideWayMove(ai, f73_local9, f73_local2, f73_local3, f73_local4, f73_local5,
                f73_local10, f73_local6, f73_local7, TransAct, f73_local8))
        elseif random == 2 and ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            local f73_local9 = 3
            local f73_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local13, 0, 0, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f73_local2, f0_local15, 0.5, 1, 0, 0, -1) }
            f73_local0:Add(EZOP_SetAct_SideWayMove(ai, f73_local9, f73_local2, f73_local3, f73_local4, f73_local5,
                f73_local10, f73_local6, f73_local7, TransAct, f73_local8))
        elseif random == 3 and ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            local f73_local9 = 3
            local f73_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local14, 2.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f73_local2, f0_local13, 0, 0, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f73_local2, f0_local15, 0.5, 1, 0, 0,
                -1) }
            f73_local0:Add(EZOP_SetAct_SideWayMove(ai, f73_local9, f73_local2, f73_local3, f73_local4, f73_local5,
                f73_local10, f73_local6, f73_local7, TransAct, f73_local8))
        end
        return f73_local0
    end,
    [3250] = function(ai, f75_arg1)
        local f75_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 3)
        local f75_local2 = ai:GetHeight(TARGET_ENE_0)
        ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f75_local3 = TARGET_ENE_0
        local f75_local4 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f75_local5 = 90
        local f75_local6 = 150
        local f75_local7 = f75_local2 + 75
        local f75_local8 = EZOP_MOVETYPE._BOOST
        local f75_local9 = 10

        local f75_local10 = function(f76_arg0)

        end

        local f75_local11 = nil
        local f75_local12 = true
        if ai:GetRandam_Int(0, 1) == 0 then
            f75_local5 = f75_local5 * -1
        end
        if random == 0 then
            local f75_local13 = 3
            local f75_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local15, 0.5, 1, 0, 0, -1) }
            f75_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f75_local13, f75_local3, f75_local5, f75_local6, f75_local7,
                f75_local4, f75_local8, f75_local9, f75_local14, f75_local10, f75_local11, ChkFunc, ChkParam, TransAct,
                f75_local12))
        elseif random == 1 then
            local f75_local13 = 3
            local f75_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local14, 2.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f75_local3, f0_local15, 0.5, 1, 0, 0, -1) }
            f75_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f75_local13, f75_local3, f75_local5, f75_local6, f75_local7,
                f75_local4, f75_local8, f75_local9, f75_local14, f75_local10, f75_local11, ChkFunc, ChkParam, TransAct,
                f75_local12))
        elseif random == 2 and ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            local f75_local13 = 3
            local f75_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local13, 0, 0, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f75_local3, f0_local15, 0.5, 1, 0, 0, -1) }
            f75_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f75_local13, f75_local3, f75_local5, f75_local6, f75_local7,
                f75_local4, f75_local8, f75_local9, f75_local14, f75_local10, f75_local11, ChkFunc, ChkParam, TransAct,
                f75_local12))
        elseif random == 3 and ai:GetLockNumRate(TARGET_SELF, f0_local13) > 0.8 then
            local f75_local13 = 3
            local f75_local14 = { EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local12, 0, 0, 0, 0.04, -1),
                EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local14, 2.5, 1, 0, 0, -1), EZOP_MakeAtkOp_NpcAcShoot(
            f75_local3, f0_local13, 0, 0, 0, 0.04, -1), EZOP_MakeAtkOp_NpcAcShoot(f75_local3, f0_local15, 0.5, 1, 0, 0,
                -1) }
            f75_local0:Add(EZOP_SetAct_ApproachBoostRise(ai, f75_local13, f75_local3, f75_local5, f75_local6, f75_local7,
                f75_local4, f75_local8, f75_local9, f75_local14, f75_local10, f75_local11, ChkFunc, ChkParam, TransAct,
                f75_local12))
        end
        return f75_local0
    end,
    [4000] = function(f77_arg0, f77_arg1)
        local f77_local0 = EZOPArray.new()
        f77_arg0:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f77_local1 = TARGET_ENE_0
        local f77_local2 = 5
        local f77_local3 = { EZOP_MakeAtkOp_NpcAcShoot(f77_local1, f0_local13, 0, 0, 0, 0, -1) }
        f77_local0:Add(EZOP_SetAct_StandShoot(f77_arg0, f77_local2, f77_local1, f77_local3))
        return f77_local0
    end,
    [5000] = function(f78_arg0, f78_arg1)
        local f78_local0 = EZOPArray.new()
        local f78_local1 = 1.5
        local f78_local2 = TARGET_ENE_0
        local f78_local3 = {}
        local f78_local4 = ChkFunc_HAGI_InsideRange
        local f78_local5 = { 0, 360, 0, 9999 }

        local f78_local6 = function(f79_arg0)
            EZOP_UseInterrupt(f79_arg0, INTERUPT_DangerousBullet)
        end

        local f78_local7 = { f0_local23 }
        local f78_local8 = nil
        local f78_local9 = true
        f78_local0:Add(EZOP_SetAct_StandShoot(f78_arg0, f78_local1, f78_local2, f78_local3, f78_local4, f78_local5,
            f78_local6, f78_local7, f78_local8, f78_local9))
        return f78_local0
    end,
    [8000] = function(f80_arg0, f80_arg1)
        local f80_local0 = EZOPArray.new()
        local f80_local1 = 15
        local f80_local2 = POINT_EVENT
        local f80_local3 = TARGET_ENE_0
        local f80_local4 = 0
        local f80_local5 = 20
        local f80_local6 = -1
        local f80_local7 = -1
        local f80_local8 = -1
        local f80_local9 = false
        local f80_local10 = {}
        local f80_local11 = ChkFunc_HAGI_InsideRange
        local f80_local12 = { 180, 240, 0, 250 }
        local f80_local13 = nil
        local f80_local14 = nil
        f80_local0:Add(EZOP_SetAct_NPC_AssultBoost(f80_arg0, f80_local1, f80_local2, f80_local4, f80_local5, f80_local6,
            f80_local7, f80_local8, f80_local9, f80_local10, f80_local11, f80_local12, f80_local13, f80_local14, TransAct))
        return f80_local0
    end,
    [8001] = function(f81_arg0, f81_arg1)
        local f81_local0 = EZOPArray.new()
        local f81_local1 = 7
        local f81_local2 = POINT_EVENT
        local f81_local3 = TARGET_ENE_0
        local f81_local4 = 0
        local f81_local5 = 20
        local f81_local6 = -1
        local f81_local7 = -1
        local f81_local8 = -1
        local f81_local9 = false
        local f81_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f81_local3, f0_local13, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f81_local3, f0_local14, 0, 10, 0, 0.04, -1) }
        local f81_local11 = ChkFunc_HAGI_InsideRange
        local f81_local12 = { 180, 240, 0, 250 }
        local f81_local13 = nil
        local f81_local14 = nil
        f81_local0:Add(EZOP_SetAct_NPC_AssultBoost(f81_arg0, f81_local1, f81_local2, f81_local4, f81_local5, f81_local6,
            f81_local7, f81_local8, f81_local9, f81_local10, f81_local11, f81_local12, f81_local13, f81_local14, TransAct))
        return f81_local0
    end,
    [8002] = function(f82_arg0, f82_arg1)
        local f82_local0 = EZOPArray.new()
        local f82_local1 = 7
        local f82_local2 = POINT_EVENT
        local f82_local3 = TARGET_EVENT
        local f82_local4 = 0
        local f82_local5 = 50
        local f82_local6 = -1
        local f82_local7 = -1
        local f82_local8 = -1
        local f82_local9 = false
        local f82_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f82_local3, f0_local11, 0, 10, 0, 0.04, -1),
            EZOP_MakeAtkOp_NpcAcShoot(f82_local3, f0_local12, 0, 10, 0, 0.04, -1) }
        local f82_local11 = ChkFunc_HAGI_InsideRange
        local f82_local12 = { 180, 240, 0, 250 }
        local f82_local13 = nil
        local f82_local14 = nil
        f82_local0:Add(EZOP_SetAct_NPC_AssultBoost(f82_arg0, f82_local1, f82_local2, f82_local4, f82_local5, f82_local6,
            f82_local7, f82_local8, f82_local9, f82_local10, f82_local11, f82_local12, f82_local13, f82_local14, TransAct))
        return f82_local0
    end,
    [9000] = function(f83_arg0, f83_arg1)
        local f83_local0 = EZOPArray.new()
        local f83_local1 = 3
        local f83_local2 = TARGET_ENE_0
        local f83_local3 = 0
        local f83_local4 = {}
        local f83_local5 = ChkFunc_HAGI_InsideRange
        local f83_local6 = { 0, 360, 0, 9999 }
        f83_local0:Add(EZOP_SetAct_QuickBoost(f83_arg0, f83_local1, f83_local2, f83_local3, f83_local4, f83_local5,
            f83_local6))
        return f83_local0
    end,
    [9010] = function(f84_arg0, f84_arg1)
        local f84_local0 = EZOPArray.new()
        local f84_local1 = 3
        local f84_local2 = TARGET_ENE_0
        local f84_local3 = 180
        local f84_local4 = {}
        local f84_local5 = ChkFunc_HAGI_InsideRange
        local f84_local6 = { 0, 360, 0, 9999 }
        f84_local0:Add(EZOP_SetAct_QuickBoost(f84_arg0, f84_local1, f84_local2, f84_local3, f84_local4, f84_local5,
            f84_local6))
        return f84_local0
    end,
    [9020] = function(f85_arg0, f85_arg1)
        local f85_local0 = EZOPArray.new()
        local f85_local1 = 3
        local f85_local2 = TARGET_ENE_0
        local f85_local3 = -90
        local f85_local4 = {}
        local f85_local5 = ChkFunc_HAGI_InsideRange
        local f85_local6 = { 0, 360, 0, 9999 }
        f85_local0:Add(EZOP_SetAct_QuickBoost(f85_arg0, f85_local1, f85_local2, f85_local3, f85_local4, f85_local5,
            f85_local6))
        return f85_local0
    end,
    [9030] = function(f86_arg0, f86_arg1)
        local f86_local0 = EZOPArray.new()
        local f86_local1 = 3
        local f86_local2 = TARGET_ENE_0
        local f86_local3 = 90
        local f86_local4 = {}
        local f86_local5 = ChkFunc_HAGI_InsideRange
        local f86_local6 = { 0, 360, 0, 9999 }
        f86_local0:Add(EZOP_SetAct_QuickBoost(f86_arg0, f86_local1, f86_local2, f86_local3, f86_local4, f86_local5,
            f86_local6))
        return f86_local0
    end,
    [9050] = function(ai, f87_arg1)
        local f87_local0 = EZOPArray.new()
        local f87_local1 = 3
        local f87_local2 = TARGET_ENE_0
        local f87_local3 = 90
        local f87_local4 = f0_local19(ai, f87_local2, f0_local8._AtkOp_HandMissileOneSide)
        local distance = ai:GetOriginDist(TARGET_ENE_0)
        if distance > 150 and ai:GetRandam_Int(0, 100) > 30 then
            f87_local4 = f0_local19(ai, f87_local2, f0_local8._AtkOp_ShoulderMissileOneSide)
        end
        local f87_local6 = ChkFunc_HAGI_InsideRange
        local f87_local7 = { 0, 360, 0, 9999 }
        if ai:GetRandam_Int(0, 1) == 0 then
            f87_local3 = f87_local3 * -1
        end
        f87_local0:Add(EZOP_SetAct_QuickBoost(ai, f87_local1, f87_local2, f87_local3, f87_local4, f87_local6, f87_local7))
        return f87_local0
    end,
    [9051] = function(ai, f88_arg1)
        local f88_local0 = EZOPArray.new()
        local f88_local1 = 3
        local f88_local2 = TARGET_ENE_0
        local f88_local3 = 60
        local f88_local4 = f0_local19(ai, f88_local2, f0_local8._AtkOp_HandMissileOneSide)
        local distance = ai:GetOriginDist(TARGET_ENE_0)
        if distance > 150 and ai:GetRandam_Int(0, 100) > 30 then
            f88_local4 = f0_local19(ai, f88_local2, f0_local8._AtkOp_ShoulderMissileOneSide)
        end
        local f88_local6 = ChkFunc_HAGI_InsideRange
        local f88_local7 = { 0, 360, 0, 9999 }
        if ai:GetRandam_Int(0, 1) == 0 then
            f88_local3 = f88_local3 * -1
        end
        f88_local0:Add(EZOP_SetAct_QuickBoost(ai, f88_local1, f88_local2, f88_local3, f88_local4, f88_local6, f88_local7))
        return f88_local0
    end,
    [9100] = function(ai, f89_arg1)
        local f89_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 1)
        local f89_local2 = TARGET_ENE_0
        local f89_local3 = 0
        local f89_local4 = ChkFunc_HAGI_InsideRange
        local f89_local5 = { 0, 360, 0, 9999 }
        if random == 0 then
            local f89_local6 = 2
            local f89_local7 = { EZOP_MakeAtkOp_NpcAcShoot(f89_local2, f0_local11, 0, 1, 0, 0, -1) }
            f89_local0:Add(EZOP_SetAct_QuickBoost(ai, f89_local6, f89_local2, f89_local3, f89_local7, f89_local4,
                f89_local5))
        elseif random == 1 then
            local f89_local6 = 3
            local f89_local7 = { EZOP_MakeAtkOp_NpcAcShoot(f89_local2, f0_local11, 0, 1, 1, 0, -1) }
            f89_local0:Add(EZOP_SetAct_QuickBoost(ai, f89_local6, f89_local2, f89_local3, f89_local7, f89_local4,
                f89_local5))
        end
        return f89_local0
    end,
    [9110] = function(f90_arg0, f90_arg1)
        local f90_local0 = EZOPArray.new()
        local f90_local1 = 3
        local f90_local2 = TARGET_ENE_0
        local f90_local3 = 180
        local f90_local4 = {}
        local f90_local5 = ChkFunc_HAGI_InsideRange
        local f90_local6 = { 0, 360, 0, 9999 }
        f90_local0:Add(EZOP_SetAct_QuickBoost(f90_arg0, f90_local1, f90_local2, f90_local3, f90_local4, f90_local5,
            f90_local6))
        local f90_local7 = TARGET_ENE_0
        local f90_local8 = 1
        local f90_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f90_local7, f0_local14, 0, 1, 0, 0.1, -1) }
        f90_local0:Add(EZOP_SetAct_StandShoot(f90_arg0, f90_local8, f90_local7, f90_local9))
        return f90_local0
    end,
    [9200] = function(f91_arg0, f91_arg1)
        local f91_local0 = EZOPArray.new()
        local f91_local1 = 3
        local f91_local2 = TARGET_ENE_0
        local f91_local3 = 0
        local f91_local4 = {}
        local f91_local5 = ChkFunc_HAGI_InsideRange
        local f91_local6 = { 0, 360, 0, 9999 }
        f91_local0:Add(EZOP_SetAct_QuickBoost(f91_arg0, f91_local1, f91_local2, f91_local3, f91_local4, f91_local5,
            f91_local6))
        local f91_local7 = TARGET_ENE_0
        local f91_local8 = 1
        local f91_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f91_local7, f0_local14, 0, 1, 0, 0.1, -1) }
        f91_local0:Add(EZOP_SetAct_StandShoot(f91_arg0, f91_local8, f91_local7, f91_local9))
        return f91_local0
    end,
    [9210] = function(f92_arg0, f92_arg1)
        local f92_local0 = EZOPArray.new()
        local f92_local1 = 3
        local f92_local2 = TARGET_ENE_0
        local f92_local3 = 180
        local f92_local4 = {}
        local f92_local5 = ChkFunc_HAGI_InsideRange
        local f92_local6 = { 0, 360, 0, 9999 }
        f92_local0:Add(EZOP_SetAct_QuickBoost(f92_arg0, f92_local1, f92_local2, f92_local3, f92_local4, f92_local5,
            f92_local6))
        local f92_local7 = TARGET_ENE_0
        local f92_local8 = 1
        local f92_local9 = { EZOP_MakeAtkOp_NpcAcShoot(f92_local7, f0_local14, 0, 1, 0, 0.1, -1) }
        f92_local0:Add(EZOP_SetAct_StandShoot(f92_arg0, f92_local8, f92_local7, f92_local9))
        return f92_local0
    end,
    [9899] = function(f93_arg0, f93_arg1)
        local f93_local0 = EZOPArray.new()
        local f93_local1 = 1
        local f93_local2 = TARGET_ENE_0
        f93_local0:Add(EZOP_SetAct_Wait(f93_arg0, f93_local1, f93_local2))
        return f93_local0
    end,
    [9999] = function(ai, f94_arg1)
        local f94_local0 = EZOPArray.new()
        local random = ai:GetRandam_Int(0, 3)
        ai:SetNaviRouteSearchType(AI_NAVIGATE_SEARCH_TYPE_MESH)
        local f94_local2 = TARGET_ENE_0
        local f94_local3 = AI_TURN_TARGET_TYPE_TARGET_DIRECTION
        local f94_local4 = EZOP_MOVETYPE._BOOST
        local f94_local5 = false

        local f94_local6 = function(f95_arg0)
            EZOP_UseInterrupt(f95_arg0, INTERUPT_DangerousBullet)
        end

        local f94_local7 = { f0_local23, f0_local21 }
        local f94_local8 = true
        if ai:GetRandam_Int(0, 1) == 0 then
            f94_local5 = true
        end
        local f94_local9 = 1.5
        local f94_local10 = { EZOP_MakeAtkOp_NpcAcShoot(f94_local2, f0_local13, 0, 0, 0, 0.04, -1) }
        f94_local0:Add(EZOP_SetAct_SideWayMove(ai, f94_local9, f94_local2, f94_local3, f94_local4, f94_local5,
            f94_local10, f94_local6, f94_local7, TransAct, f94_local8))
        return f94_local0
    end
}

OpSetArr[f0_local0] = f0_local24
