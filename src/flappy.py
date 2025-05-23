import asyncio
import sys
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Title,
    Floor,
    GameOver,
    ScoreBoard,
    Medal,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
    Button,
    ButtonMode,
)
from .utils import GameConfig, Images, Sounds, Window
    
class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(1024, 768)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images(window.width, window.height)

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    async def start(self):
        while True:
                self.background = Background(self.config)
                self.title = Title(self.config)
                self.welcome_message = WelcomeMessage(self.config)
                self.game_over_message = GameOver(self.config)
                self.scoreboard = ScoreBoard(self.config)
                self.restart()
                await self.main_interface()

    #first interface 
    async def main_interface(self):
        while True:
            
            # Get both surface and rect
            solo_text_surf, solo_button_rect = self.solo_button()
            multi_text_surf, multi_button_rect = self.multi_button()
            skill_text_surf, skill_button_rect = self.skill_button()
            
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    #click the solo button , run splash screen
                    if solo_button_rect.collidepoint(event.pos):
                        await self.splash()
                    if multi_button_rect.collidepoint(event.pos):
                        await self.game_room_interface()
                    if skill_button_rect.collidepoint(event.pos):
                        # Run the skill tutorial
                        pass
                    
            self.background.tick()
            self.floor.tick()
            self.title.tick()
            
            # Draw the button
            self.config.screen.blit(solo_text_surf, solo_button_rect)
            self.config.screen.blit(multi_text_surf, multi_button_rect)
            self.config.screen.blit(skill_text_surf, skill_button_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
          
    async def game_room_interface(self):
        self.button.set_mode(ButtonMode.MULTI)
        
        while True:  
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)

            self.background.tick()
            self.floor.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

     #create the solo button 
    def solo_button(self):
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
        WHITE = (255,255,255)
        text_surf = FONT.render("SOLO", True, WHITE)
        text_rect = text_surf.get_rect(
            centerx=self.config.window.width // 2,
            centery=self.config.window.height // 2 - 60 
        )
        return text_surf, text_rect

     #create the solo button 
    def multi_button(self):
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
        WHITE = (255,255,255)
        text_surf = FONT.render("MULTI", True, WHITE)
        text_rect = text_surf.get_rect(
            centerx=self.config.window.width // 2,
            centery=self.config.window.height // 2
        )
        return text_surf, text_rect

    def skill_button(self):
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
        WHITE = (255, 255, 255)
        text_surf = FONT.render("SKILL TUTORIAL", True, WHITE)
        text_rect = text_surf.get_rect(
            centerx=self.config.window.width // 2,
            centery=self.config.window.height // 2 + 60
        )
        return text_surf, text_rect
    
    def back_button(self):
        back_button = self.config.images.buttons["back"]
        back_pos = (30, 30)
        back_rect = pygame.Rect(back_pos[0], back_pos[1], back_button.get_width(), back_button.get_height())
        return back_button, back_rect
    
    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""
        self.player.set_mode(PlayerMode.SHM)

        while True:
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if back_button_rect.collidepoint(event.pos):
                        self.restart()
                        await self.main_interface()
                    #after click run the play() and start the game
                    await self.play()

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def multi_interface(self):
        #show lobby game room interface 

        self.player.set_mode(PlayerMode.SHM)

        while True:
            
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    #after click run the play() and start the game
                    await self.play()

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.score.reset()
        await self.solo_gameplay()

    async def game_pause(self):
        self.player.set_mode(PlayerMode.PAUSE)
        self.pipes.stop()
        self.floor.stop()
        self.button.set_mode(ButtonMode.PAUSE)

        while True:
            for event in pygame.event.get():
                if self.is_tap_event(event):
                    if self.button.resume_rect and self.button.resume_rect.collidepoint(event.pos):
                        await self.game_resume()
                    elif self.button.restart_rect and self.button.restart_rect.collidepoint(event.pos):
                        self.restart()
                        await self.splash()
                    elif self.button.quit_rect and self.button.quit_rect.collidepoint(event.pos):
                        self.restart()
                        #after click back to main
                        await self.main_interface()
            
            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.button.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)
    
    async def game_resume(self):
        self.pipes.resume()
        self.floor.resume()
        await self.solo_gameplay()

    async def game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()
        self.button.set_mode(ButtonMode.SOLO_GAME_OVER)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.button.restart_rect.collidepoint(event.pos):
                        self.restart()
                        await self.splash()
                    elif self.button.quit_rect.collidepoint(event.pos):
                        self.restart()
                        #after click back to main
                        await self.main_interface()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.player.tick()
            self.game_over_message.tick()
            self.scoreboard.tick()
            self.score.tick()
            self.medal.tick()
            self.button.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)

    def restart(self):
        self.floor = Floor(self.config)
        self.player = Player(self.config)
        self.score = Score(self.config, self.player)
        self.pipes = Pipes(self.config)
        self.medal = Medal(self.config, self.score)
        self.button = Button(self.config)

    async def solo_gameplay(self):
        self.player.set_mode(PlayerMode.NORMAL)
        self.button.set_mode(ButtonMode.DEFAULT)

        while True:
            back_button_surf, back_button_rect = self.back_button()
            if self.player.collided(self.pipes, self.floor):
                #if flappy hit ground or pipe, end this and run the game over()
                await self.game_over()

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    await self.game_pause()
                if self.is_tap_event(event):
                    if back_button_rect.collidepoint(event.pos):
                        await self.game_pause()
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
