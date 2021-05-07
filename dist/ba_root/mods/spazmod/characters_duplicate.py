# -*- coding: utf-8 -*-
# ba_meta require api 6
from __future__ import annotations
from typing import TYPE_CHECKING
import _ba,ba,bastd
from bastd.actor.spazappearance import *
if TYPE_CHECKING:
    from typing import List, Optional, Tuple


def add_characters():

    # Zoe #######################################
    t = Appearance('Zoe_mod')
    t.color_texture = 'zoeColor'
    t.color_mask_texture = 'zoeColorMask'
    t.default_color = (0.6, 0.6, 0.6)
    t.default_highlight = (0, 1, 0)
    t.icon_texture = 'zoeIcon'
    t.icon_mask_texture = 'zoeIconColorMask'
    t.head_model = 'zoeHead'
    t.torso_model = 'zoeTorso'
    t.pelvis_model = 'zoePelvis'
    t.upper_arm_model = 'zoeUpperArm'
    t.forearm_model = 'zoeForeArm'
    t.hand_model = 'zoeHand'
    t.upper_leg_model = 'zoeUpperLeg'
    t.lower_leg_model = 'zoeLowerLeg'
    t.toes_model = 'zoeToes'
    t.jump_sounds = ['zoeJump01', 'zoeJump02', 'zoeJump03']
    t.attack_sounds = [
        'zoeAttack01', 'zoeAttack02', 'zoeAttack03', 'zoeAttack04'
    ]
    t.impact_sounds = [
        'zoeImpact01', 'zoeImpact02', 'zoeImpact03', 'zoeImpact04'
    ]
    t.death_sounds = ['zoeDeath01']
    t.pickup_sounds = ['zoePickup01']
    t.fall_sounds = ['zoeFall01']
    t.style = 'female'

    # Ninja ##########################################
    t = Appearance('Snake Shadow_mod')
    t.color_texture = 'ninjaColor'
    t.color_mask_texture = 'ninjaColorMask'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.55, 0.8, 0.55)
    t.icon_texture = 'ninjaIcon'
    t.icon_mask_texture = 'ninjaIconColorMask'
    t.head_model = 'ninjaHead'
    t.torso_model = 'ninjaTorso'
    t.pelvis_model = 'ninjaPelvis'
    t.upper_arm_model = 'ninjaUpperArm'
    t.forearm_model = 'ninjaForeArm'
    t.hand_model = 'ninjaHand'
    t.upper_leg_model = 'ninjaUpperLeg'
    t.lower_leg_model = 'ninjaLowerLeg'
    t.toes_model = 'ninjaToes'
    ninja_attacks = ['ninjaAttack' + str(i + 1) + '' for i in range(7)]
    ninja_hits = ['ninjaHit' + str(i + 1) + '' for i in range(8)]
    ninja_jumps = ['ninjaAttack' + str(i + 1) + '' for i in range(7)]
    t.jump_sounds = ninja_jumps
    t.attack_sounds = ninja_attacks
    t.impact_sounds = ninja_hits
    t.death_sounds = ['ninjaDeath1']
    t.pickup_sounds = ninja_attacks
    t.fall_sounds = ['ninjaFall1']
    t.style = 'ninja'

    # Barbarian #####################################
    t = Appearance('Kronk_mod')
    t.color_texture = 'kronk'
    t.color_mask_texture = 'kronkColorMask'
    t.default_color = (0.4, 0.5, 0.4)
    t.default_highlight = (1, 0.5, 0.3)
    t.icon_texture = 'kronkIcon'
    t.icon_mask_texture = 'kronkIconColorMask'
    t.head_model = 'kronkHead'
    t.torso_model = 'kronkTorso'
    t.pelvis_model = 'kronkPelvis'
    t.upper_arm_model = 'kronkUpperArm'
    t.forearm_model = 'kronkForeArm'
    t.hand_model = 'kronkHand'
    t.upper_leg_model = 'kronkUpperLeg'
    t.lower_leg_model = 'kronkLowerLeg'
    t.toes_model = 'kronkToes'
    kronk_sounds = [
        'kronk1', 'kronk2', 'kronk3', 'kronk4', 'kronk5', 'kronk6', 'kronk7',
        'kronk8', 'kronk9', 'kronk10'
    ]
    t.jump_sounds = kronk_sounds
    t.attack_sounds = kronk_sounds
    t.impact_sounds = kronk_sounds
    t.death_sounds = ['kronkDeath']
    t.pickup_sounds = kronk_sounds
    t.fall_sounds = ['kronkFall']
    t.style = 'kronk'

    # Chef ###########################################
    t = Appearance('Mel_mod')
    t.color_texture = 'melColor'
    t.color_mask_texture = 'melColorMask'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.1, 0.6, 0.1)
    t.icon_texture = 'melIcon'
    t.icon_mask_texture = 'melIconColorMask'
    t.head_model = 'melHead'
    t.torso_model = 'melTorso'
    t.pelvis_model = 'kronkPelvis'
    t.upper_arm_model = 'melUpperArm'
    t.forearm_model = 'melForeArm'
    t.hand_model = 'melHand'
    t.upper_leg_model = 'melUpperLeg'
    t.lower_leg_model = 'melLowerLeg'
    t.toes_model = 'melToes'
    mel_sounds = [
        'mel01', 'mel02', 'mel03', 'mel04', 'mel05', 'mel06', 'mel07', 'mel08',
        'mel09', 'mel10'
    ]
    t.attack_sounds = mel_sounds
    t.jump_sounds = mel_sounds
    t.impact_sounds = mel_sounds
    t.death_sounds = ['melDeath01']
    t.pickup_sounds = mel_sounds
    t.fall_sounds = ['melFall01']
    t.style = 'mel'

    # Pirate #######################################
    t = Appearance('Jack Morgan_mod')
    t.color_texture = 'jackColor'
    t.color_mask_texture = 'jackColorMask'
    t.default_color = (1, 0.2, 0.1)
    t.default_highlight = (1, 1, 0)
    t.icon_texture = 'jackIcon'
    t.icon_mask_texture = 'jackIconColorMask'
    t.head_model = 'jackHead'
    t.torso_model = 'jackTorso'
    t.pelvis_model = 'kronkPelvis'
    t.upper_arm_model = 'jackUpperArm'
    t.forearm_model = 'jackForeArm'
    t.hand_model = 'jackHand'
    t.upper_leg_model = 'jackUpperLeg'
    t.lower_leg_model = 'jackLowerLeg'
    t.toes_model = 'jackToes'
    hit_sounds = [
        'jackHit01', 'jackHit02', 'jackHit03', 'jackHit04', 'jackHit05',
        'jackHit06', 'jackHit07'
    ]
    sounds = ['jack01', 'jack02', 'jack03', 'jack04', 'jack05', 'jack06']
    t.attack_sounds = sounds
    t.jump_sounds = sounds

    t.impact_sounds = hit_sounds
    t.death_sounds = ['jackDeath01']
    t.pickup_sounds = sounds
    t.fall_sounds = ['jackFall01']
    t.style = 'pirate'

    # Santa ######################################
    t = Appearance('Santa Claus_mod')
    t.color_texture = 'santaColor'
    t.color_mask_texture = 'santaColorMask'
    t.default_color = (1, 0, 0)
    t.default_highlight = (1, 1, 1)
    t.icon_texture = 'santaIcon'
    t.icon_mask_texture = 'santaIconColorMask'
    t.head_model = 'santaHead'
    t.torso_model = 'santaTorso'
    t.pelvis_model = 'kronkPelvis'
    t.upper_arm_model = 'santaUpperArm'
    t.forearm_model = 'santaForeArm'
    t.hand_model = 'santaHand'
    t.upper_leg_model = 'santaUpperLeg'
    t.lower_leg_model = 'santaLowerLeg'
    t.toes_model = 'santaToes'
    hit_sounds = ['santaHit01', 'santaHit02', 'santaHit03', 'santaHit04']
    sounds = ['santa01', 'santa02', 'santa03', 'santa04', 'santa05']
    t.attack_sounds = sounds
    t.jump_sounds = sounds
    t.impact_sounds = hit_sounds
    t.death_sounds = ['santaDeath']
    t.pickup_sounds = sounds
    t.fall_sounds = ['santaFall']
    t.style = 'santa'

    # Snowman ###################################
    t = Appearance('Frosty_mod')
    t.color_texture = 'frostyColor'
    t.color_mask_texture = 'frostyColorMask'
    t.default_color = (0.5, 0.5, 1)
    t.default_highlight = (1, 0.5, 0)
    t.icon_texture = 'frostyIcon'
    t.icon_mask_texture = 'frostyIconColorMask'
    t.head_model = 'frostyHead'
    t.torso_model = 'frostyTorso'
    t.pelvis_model = 'frostyPelvis'
    t.upper_arm_model = 'frostyUpperArm'
    t.forearm_model = 'frostyForeArm'
    t.hand_model = 'frostyHand'
    t.upper_leg_model = 'frostyUpperLeg'
    t.lower_leg_model = 'frostyLowerLeg'
    t.toes_model = 'frostyToes'
    frosty_sounds = [
        'frosty01', 'frosty02', 'frosty03', 'frosty04', 'frosty05'
    ]
    frosty_hit_sounds = ['frostyHit01', 'frostyHit02', 'frostyHit03']
    t.attack_sounds = frosty_sounds
    t.jump_sounds = frosty_sounds
    t.impact_sounds = frosty_hit_sounds
    t.death_sounds = ['frostyDeath']
    t.pickup_sounds = frosty_sounds
    t.fall_sounds = ['frostyFall']
    t.style = 'frosty'

    # Skeleton ################################
    t = Appearance('Bones_mod')
    t.color_texture = 'bonesColor'
    t.color_mask_texture = 'bonesColorMask'
    t.default_color = (0.6, 0.9, 1)
    t.default_highlight = (0.6, 0.9, 1)
    t.icon_texture = 'bonesIcon'
    t.icon_mask_texture = 'bonesIconColorMask'
    t.head_model = 'bonesHead'
    t.torso_model = 'bonesTorso'
    t.pelvis_model = 'bonesPelvis'
    t.upper_arm_model = 'bonesUpperArm'
    t.forearm_model = 'bonesForeArm'
    t.hand_model = 'bonesHand'
    t.upper_leg_model = 'bonesUpperLeg'
    t.lower_leg_model = 'bonesLowerLeg'
    t.toes_model = 'bonesToes'
    bones_sounds = ['bones1', 'bones2', 'bones3']
    bones_hit_sounds = ['bones1', 'bones2', 'bones3']
    t.attack_sounds = bones_sounds
    t.jump_sounds = bones_sounds
    t.impact_sounds = bones_hit_sounds
    t.death_sounds = ['bonesDeath']
    t.pickup_sounds = bones_sounds
    t.fall_sounds = ['bonesFall']
    t.style = 'bones'

    # Bear ###################################
    t = Appearance('Bernard_mod')
    t.color_texture = 'bearColor'
    t.color_mask_texture = 'bearColorMask'
    t.default_color = (0.7, 0.5, 0.0)
    t.icon_texture = 'bearIcon'
    t.icon_mask_texture = 'bearIconColorMask'
    t.head_model = 'bearHead'
    t.torso_model = 'bearTorso'
    t.pelvis_model = 'bearPelvis'
    t.upper_arm_model = 'bearUpperArm'
    t.forearm_model = 'bearForeArm'
    t.hand_model = 'bearHand'
    t.upper_leg_model = 'bearUpperLeg'
    t.lower_leg_model = 'bearLowerLeg'
    t.toes_model = 'bearToes'
    bear_sounds = ['bear1', 'bear2', 'bear3', 'bear4']
    bear_hit_sounds = ['bearHit1', 'bearHit2']
    t.attack_sounds = bear_sounds
    t.jump_sounds = bear_sounds
    t.impact_sounds = bear_hit_sounds
    t.death_sounds = ['bearDeath']
    t.pickup_sounds = bear_sounds
    t.fall_sounds = ['bearFall']
    t.style = 'bear'

    # Penguin ###################################
    t = Appearance('Pascal_mod')
    t.color_texture = 'penguinColor'
    t.color_mask_texture = 'penguinColorMask'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)
    t.icon_texture = 'penguinIcon'
    t.icon_mask_texture = 'penguinIconColorMask'
    t.head_model = 'penguinHead'
    t.torso_model = 'penguinTorso'
    t.pelvis_model = 'penguinPelvis'
    t.upper_arm_model = 'penguinUpperArm'
    t.forearm_model = 'penguinForeArm'
    t.hand_model = 'penguinHand'
    t.upper_leg_model = 'penguinUpperLeg'
    t.lower_leg_model = 'penguinLowerLeg'
    t.toes_model = 'penguinToes'
    penguin_sounds = ['penguin1', 'penguin2', 'penguin3', 'penguin4']
    penguin_hit_sounds = ['penguinHit1', 'penguinHit2']
    t.attack_sounds = penguin_sounds
    t.jump_sounds = penguin_sounds
    t.impact_sounds = penguin_hit_sounds
    t.death_sounds = ['penguinDeath']
    t.pickup_sounds = penguin_sounds
    t.fall_sounds = ['penguinFall']
    t.style = 'penguin'

    # Ali ###################################
    t = Appearance('Taobao Mascot_mod')
    t.color_texture = 'aliColor'
    t.color_mask_texture = 'aliColorMask'
    t.default_color = (1, 0.5, 0)
    t.default_highlight = (1, 1, 1)
    t.icon_texture = 'aliIcon'
    t.icon_mask_texture = 'aliIconColorMask'
    t.head_model = 'aliHead'
    t.torso_model = 'aliTorso'
    t.pelvis_model = 'aliPelvis'
    t.upper_arm_model = 'aliUpperArm'
    t.forearm_model = 'aliForeArm'
    t.hand_model = 'aliHand'
    t.upper_leg_model = 'aliUpperLeg'
    t.lower_leg_model = 'aliLowerLeg'
    t.toes_model = 'aliToes'
    ali_sounds = ['ali1', 'ali2', 'ali3', 'ali4']
    ali_hit_sounds = ['aliHit1', 'aliHit2']
    t.attack_sounds = ali_sounds
    t.jump_sounds = ali_sounds
    t.impact_sounds = ali_hit_sounds
    t.death_sounds = ['aliDeath']
    t.pickup_sounds = ali_sounds
    t.fall_sounds = ['aliFall']
    t.style = 'ali'

    # cyborg ###################################
    t = Appearance('B-9000_mod')
    t.color_texture = 'cyborgColor'
    t.color_mask_texture = 'cyborgColorMask'
    t.default_color = (0.5, 0.5, 0.5)
    t.default_highlight = (1, 0, 0)
    t.icon_texture = 'cyborgIcon'
    t.icon_mask_texture = 'cyborgIconColorMask'
    t.head_model = 'cyborgHead'
    t.torso_model = 'cyborgTorso'
    t.pelvis_model = 'cyborgPelvis'
    t.upper_arm_model = 'cyborgUpperArm'
    t.forearm_model = 'cyborgForeArm'
    t.hand_model = 'cyborgHand'
    t.upper_leg_model = 'cyborgUpperLeg'
    t.lower_leg_model = 'cyborgLowerLeg'
    t.toes_model = 'cyborgToes'
    cyborg_sounds = ['cyborg1', 'cyborg2', 'cyborg3', 'cyborg4']
    cyborg_hit_sounds = ['cyborgHit1', 'cyborgHit2']
    t.attack_sounds = cyborg_sounds
    t.jump_sounds = cyborg_sounds
    t.impact_sounds = cyborg_hit_sounds
    t.death_sounds = ['cyborgDeath']
    t.pickup_sounds = cyborg_sounds
    t.fall_sounds = ['cyborgFall']
    t.style = 'cyborg'

    # Agent ###################################
    t = Appearance('Agent Johnson_mod')
    t.color_texture = 'agentColor'
    t.color_mask_texture = 'agentColorMask'
    t.default_color = (0.3, 0.3, 0.33)
    t.default_highlight = (1, 0.5, 0.3)
    t.icon_texture = 'agentIcon'
    t.icon_mask_texture = 'agentIconColorMask'
    t.head_model = 'agentHead'
    t.torso_model = 'agentTorso'
    t.pelvis_model = 'agentPelvis'
    t.upper_arm_model = 'agentUpperArm'
    t.forearm_model = 'agentForeArm'
    t.hand_model = 'agentHand'
    t.upper_leg_model = 'agentUpperLeg'
    t.lower_leg_model = 'agentLowerLeg'
    t.toes_model = 'agentToes'
    agent_sounds = ['agent1', 'agent2', 'agent3', 'agent4']
    agent_hit_sounds = ['agentHit1', 'agentHit2']
    t.attack_sounds = agent_sounds
    t.jump_sounds = agent_sounds
    t.impact_sounds = agent_hit_sounds
    t.death_sounds = ['agentDeath']
    t.pickup_sounds = agent_sounds
    t.fall_sounds = ['agentFall']
    t.style = 'agent'

    # Wizard ###################################
    t = Appearance('Grumbledorf_mod')
    t.color_texture = 'wizardColor'
    t.color_mask_texture = 'wizardColorMask'
    t.default_color = (0.2, 0.4, 1.0)
    t.default_highlight = (0.06, 0.15, 0.4)
    t.icon_texture = 'wizardIcon'
    t.icon_mask_texture = 'wizardIconColorMask'
    t.head_model = 'wizardHead'
    t.torso_model = 'wizardTorso'
    t.pelvis_model = 'wizardPelvis'
    t.upper_arm_model = 'wizardUpperArm'
    t.forearm_model = 'wizardForeArm'
    t.hand_model = 'wizardHand'
    t.upper_leg_model = 'wizardUpperLeg'
    t.lower_leg_model = 'wizardLowerLeg'
    t.toes_model = 'wizardToes'
    wizard_sounds = ['wizard1', 'wizard2', 'wizard3', 'wizard4']
    wizard_hit_sounds = ['wizardHit1', 'wizardHit2']
    t.attack_sounds = wizard_sounds
    t.jump_sounds = wizard_sounds
    t.impact_sounds = wizard_hit_sounds
    t.death_sounds = ['wizardDeath']
    t.pickup_sounds = wizard_sounds
    t.fall_sounds = ['wizardFall']
    t.style = 'spaz'

    # Pixie ###################################
    t = Appearance('Pixel_mod')
    t.color_texture = 'pixieColor'
    t.color_mask_texture = 'pixieColorMask'
    t.default_color = (0, 1, 0.7)
    t.default_highlight = (0.65, 0.35, 0.75)
    t.icon_texture = 'pixieIcon'
    t.icon_mask_texture = 'pixieIconColorMask'
    t.head_model = 'pixieHead'
    t.torso_model = 'pixieTorso'
    t.pelvis_model = 'pixiePelvis'
    t.upper_arm_model = 'pixieUpperArm'
    t.forearm_model = 'pixieForeArm'
    t.hand_model = 'pixieHand'
    t.upper_leg_model = 'pixieUpperLeg'
    t.lower_leg_model = 'pixieLowerLeg'
    t.toes_model = 'pixieToes'
    pixie_sounds = ['pixie1', 'pixie2', 'pixie3', 'pixie4']
    pixie_hit_sounds = ['pixieHit1', 'pixieHit2']
    t.attack_sounds = pixie_sounds
    t.jump_sounds = pixie_sounds
    t.impact_sounds = pixie_hit_sounds
    t.death_sounds = ['pixieDeath']
    t.pickup_sounds = pixie_sounds
    t.fall_sounds = ['pixieFall']
    t.style = 'pixie'

    # Bunny ###################################
    t = Appearance('Easter Bunny_mod')
    t.color_texture = 'bunnyColor'
    t.color_mask_texture = 'bunnyColorMask'
    t.default_color = (1, 1, 1)
    t.default_highlight = (1, 0.5, 0.5)
    t.icon_texture = 'bunnyIcon'
    t.icon_mask_texture = 'bunnyIconColorMask'
    t.head_model = 'bunnyHead'
    t.torso_model = 'bunnyTorso'
    t.pelvis_model = 'bunnyPelvis'
    t.upper_arm_model = 'bunnyUpperArm'
    t.forearm_model = 'bunnyForeArm'
    t.hand_model = 'bunnyHand'
    t.upper_leg_model = 'bunnyUpperLeg'
    t.lower_leg_model = 'bunnyLowerLeg'
    t.toes_model = 'bunnyToes'
    bunny_sounds = ['bunny1', 'bunny2', 'bunny3', 'bunny4']
    bunny_hit_sounds = ['bunnyHit1', 'bunnyHit2']
    t.attack_sounds = bunny_sounds
    t.jump_sounds = ['bunnyJump']
    t.impact_sounds = bunny_hit_sounds
    t.death_sounds = ['bunnyDeath']
    t.pickup_sounds = bunny_sounds
    t.fall_sounds = ['bunnyFall']
    t.style = 'bunny'

# ba_meta export plugin
class unlock_characters(ba.Plugin):
    def on_app_launch(self):
        add_characters()
