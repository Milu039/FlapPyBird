import pygame
import random as Random
from ..utils import GameConfig
from .entity import Entity
from .player import Player

class Skill(Entity):
    def __init__(self, config: GameConfig, player: Player) -> None:
        super().__init__(config)
        self.player = player
        self.skill_box = config.images.skills["skill_box"]
        self.skill_images = {
            "speed_boost": config.images.skills["speed_boost"],
            "time_freeze": config.images.skills["time_freeze"],
            #"teleport": config.images.skills["teleport"],
            #"penetration": config.images.skills["penetration"]
        }
        self.available_skills = [None, None]
        self.last_skill_spawn_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_skill_spawn_time >= 5000:
            self.add_random_skill()
            self.last_skill_spawn_time = current_time

    def add_random_skill(self):
        import random
        skill_name = random.choice(list(self.skill_images.keys()))
        if None in self.available_skills:
            empty_index = self.available_skills.index(None)
            self.available_skills[empty_index] = skill_name

    def use_skill(self, index):
        if index not in [0, 1]:
            return
        skill = self.available_skills[index]
        if skill is None:
            return  # No skill in that slot

        print(f"Player {self.player.id} using skill: {skill}")

        if skill == "penetration":
            self.player.penetration_active = True
            self.player.penetration_timer = 3.0  # seconds
        elif skill == "speed_boost":
            self.player.vel_x = 2
            self.player.speed_boost_active = True
            self.player.speed_boost_timer = 5.0 * self.player.config.fps
        elif skill == "time_freeze":
            # Send freeze command to server - server will target player with highest X
            if hasattr(self.player, 'network') and self.player.network and self.player.network.running:
                room_num = self.player.network.room_num
                user_id = self.player.network.id
                self.player.network.send(f"UseFreeze:{room_num}:{user_id}")
                print(f"DEBUG: Player {user_id} used freeze skill - will target player with highest X")
        elif skill == "teleport":
            pass
            
        # Clear used skill
        self.available_skills[index] = None
    
    def draw(self):
        pos_skill_box_1 = (50, 650)
        pos_skill_box_2 = (200, 650)
        self.config.screen.blit(self.skill_box, pos_skill_box_1)
        self.config.screen.blit(self.skill_box, pos_skill_box_2)

        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 26)
        key1 = FONT.render("1", True, (0, 0, 0))
        key2 = FONT.render("2", True, (0, 0, 0))
        self.config.screen.blit(key1, (70, 620))
        self.config.screen.blit(key2, (225, 620))

        # Draw skill images if any
        if self.available_skills[0]:
            self.config.screen.blit(self.skill_images[self.available_skills[0]], (50, 650))
        if self.available_skills[1]:
            self.config.screen.blit(self.skill_images[self.available_skills[1]], (200, 650))