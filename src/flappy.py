import asyncio
import sys
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Title,
    Floor,
    ScoreBoard,
    Medal,
    Pipes,
    Player,
    PlayerMode,
    Score,
    Message,
    RoomList,
    Button,
    Timer,
)
from .utils import GameConfig, Images, Sounds, Window, Mode
    
class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(1024, 768)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

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
    
    def click_event(self):
        click,_,_ = pygame.mouse.get_pressed()
        return click
    
    def restart(self):
        self.floor = Floor(self.config)
        self.player = Player(self.config)
        self.score = Score(self.config, self.player)
        self.pipes = Pipes(self.config)
        self.medal = Medal(self.config, self.score)
        self.button = Button(self.config, self.mode)
        self.timer = Timer(self.config)
    
    async def start(self):
        while True:
                self.mode = Mode()
                self.background = Background(self.config)
                self.title = Title(self.config)
                self.message = Message(self.config, self.mode)
                self.room_list = RoomList(self.config)
                self.scoreboard = ScoreBoard(self.config)
                self.mode.set_mode("Default")
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
                    #click the solo button , run solo_ready_interface screen
                    if solo_button_rect.collidepoint(event.pos):
                        await self.solo_ready_interface()
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

    async def solo_ready_interface(self):
        """Shows welcome solo_ready_interface screen animation of flappy bird"""
        self.player.set_mode(PlayerMode.SHM)
        self.mode.set_mode("Solo")
        self.message.set_mode(self.mode.get_mode())

        while True:
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if back_button_rect.collidepoint(event.pos):
                        self.restart()
                        await self.main_interface()
                if self.is_tap_event(event):
                    #after click run the play() and start the game
                    await self.play()

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.message.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def play(self):
        self.gamemode = self.mode.get_mode()
        if self.gamemode == "Solo":
            self.score.reset()
            await self.solo_gameplay()
        elif self.gamemode == "Multi":
            await self.multi_gameplay()

    async def game_pause(self):
        self.player.set_mode(PlayerMode.PAUSE)
        self.pipes.stop()
        self.floor.stop()
        self.mode.set_mode("Pause")
        self.button.set_mode(self.mode.get_mode())

        while True:
            for event in pygame.event.get():
                if self.click_event():
                    if self.button.resume_rect.collidepoint(event.pos):
                        await self.game_resume()
                    elif self.button.restart_rect.collidepoint(event.pos):
                        self.restart()
                        await self.solo_ready_interface()
                    elif self.button.quit_rect.collidepoint(event.pos):
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

    async def solo_gameplay(self):
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            back_button_surf, back_button_rect = self.back_button()
            if self.player.collided(self.pipes, self.floor):
                #if flappy hit ground or pipe, end this and run the game over()
                await self.solo_game_over()

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    await self.game_pause()
                if self.click_event():
                    if back_button_rect.collidepoint(event.pos):
                        await self.game_pause()
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def solo_game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()
        self.mode.set_mode("Solo GameOver")
        self.button.set_mode(self.mode.get_mode())
        self.message.set_mode(self.mode.get_mode())

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if self.button.restart_rect.collidepoint(event.pos):
                        self.restart()
                        await self.solo_ready_interface()
                    if self.button.quit_rect.collidepoint(event.pos):
                        self.restart()
                        #after click back to main
                        await self.main_interface()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.player.tick()
            self.message.tick()
            self.scoreboard.tick()
            self.score.tick()
            self.medal.tick()
            self.button.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)

    async def game_room_interface(self):
        #self.button.set_mode(ButtonMode.MULTI)
        self.mode.set_mode("Game Room")
        self.message.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())
        
        while True:  
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if back_button_rect.collidepoint(event.pos):
                        self.restart()
                        await self.main_interface()
                    if self.button.create_rect.collidepoint(event.pos):
                        await self.create_room_interface()
                    if self.button.join_rect.collidepoint(event.pos):
                        await self.join_room_interface()

            self.background.tick()
            self.message.tick()
            self.room_list.tick()
            self.floor.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
    
    async def create_room_interface(self):
        self.mode.set_mode("Create Room")
        self.message.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())

        while True:
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if back_button_rect.collidepoint(event.pos):
                        await self.game_room_interface()
                    if self.button.create_rect.collidepoint(event.pos):
                        await self.join_room_interface()

            self.background.tick()
            self.room_list.tick()
            self.message.tick()
            self.floor.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def join_room_interface(self):
        self.mode.set_mode("Room Lobby")
        self.message.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())

        while True:
            back_button_surf, back_button_rect = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if back_button_rect.collidepoint(event.pos):
                        await self.game_room_interface()
                    if self.button.ready_rect.collidepoint(event.pos):
                        await self.multi_gameplay()

            self.background.tick()
            self.message.tick()
            self.room_list.tick()
            self.floor.tick()
            self.config.screen.blit(back_button_surf, back_button_rect)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def multi_gameplay(self):
        self.player.set_mode(PlayerMode.NORMAL)
        while True:
            if self.player.collided(self.pipes, self.floor):
                #if flappy push by the pipes
                await self.solo_game_over()

            if self.timer.time_up():
                await self.leaderboard_interface()

            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.timer.update_timer()
            self.timer.tick()
            self.player.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def leaderboard_interface(self):
        
        self.pipes.stop()
        self.floor.stop()
        self.mode.set_mode("Leaderboard")
        self.button.set_mode(self.mode.get_mode())
        self.message.set_mode(self.mode.get_mode())

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.click_event():
                    if self.button.restart_rect.collidepoint(event.pos):
                        self.restart()
                        await self.join_room_interface()
                    elif self.button.quit_rect.collidepoint(event.pos):
                        self.restart()
                        await self.game_room_interface()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.player.tick()
            self.message.tick()
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()