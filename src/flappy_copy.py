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
)
from .utils import GameConfig, Images, Sounds, Window, MultiplayerManager

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
        
        # Initialize multiplayer as None - will be set when mode is selected
        self.multiplayer = None
        self.is_multiplayer = False

    async def start(self):
        while True:
            self.restart()
            await self.main_interface()

    #first interface 
    async def main_interface(self):
        while True:
            
            # Get both surface and rect
            solo_text_surf, solo_button_rect = self.solo_button()
            multi_text_surf, multi_button_rect = self.multi_button()
            
            for event in pygame.event.get():
                self.check_quit_event(event)
                #click the solo button , run splash screen
                if event.type == pygame.MOUSEBUTTONDOWN and solo_button_rect.collidepoint(event.pos):
                    self.is_multiplayer = False
                    await self.splash()
                if event.type == pygame.MOUSEBUTTONDOWN and multi_button_rect.collidepoint(event.pos):
                    # Enter server address if multiplayer selected
                    self.is_multiplayer = True
                    await self.connect_screen()
                    
            self.background.tick()
            self.floor.tick()
            self.title.tick()
            
            # Draw the button
            self.config.screen.blit(solo_text_surf, solo_button_rect)
            self.config.screen.blit(multi_text_surf, multi_button_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
            
    async def connect_screen(self):
        """Screen for entering server address"""
        font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 20)
        input_text = "localhost"  # Default server
        input_active = True
        connection_failed = False
        
        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return  # Go back to main interface
                    elif event.key == pygame.K_RETURN:
                        # Try to connect to server
                        try:
                            self.multiplayer = MultiplayerManager(self.config, input_text)
                            if self.multiplayer.is_connected():
                                await self.splash()  # Connected, go to splash screen
                                return
                            else:
                                connection_failed = True
                        except Exception as e:
                            print(f"Connection error: {e}")
                            connection_failed = True
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        # Add character to input_text if it's a valid character
                        if event.unicode.isprintable():
                            input_text += event.unicode
            
            # Draw the screen
            self.background.tick()
            self.floor.tick()
            
            # Render input box
            text_surface = font.render("Enter Server IP:", True, (255, 255, 255))
            self.config.screen.blit(text_surface, (self.config.window.width/4, self.config.window.height/3))
            
            pygame.draw.rect(self.config.screen, (255, 255, 255), 
                             [self.config.window.width/4, self.config.window.height/3 + 40, 
                              self.config.window.width/2, 40], 2)
                              
            input_surface = font.render(input_text, True, (255, 255, 255))
            self.config.screen.blit(input_surface, (self.config.window.width/4 + 10, 
                                                  self.config.window.height/3 + 50))
                                                  
            # Show instruction
            instr_surface = font.render("Press ENTER to connect", True, (255, 255, 255))
            self.config.screen.blit(instr_surface, (self.config.window.width/4, 
                                                  self.config.window.height/3 + 100))
                                                  
            # Show error message if connection failed
            if connection_failed:
                error_surface = font.render("Connection failed!", True, (255, 0, 0))
                self.config.screen.blit(error_surface, (self.config.window.width/4, 
                                                      self.config.window.height/3 + 150))
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()
     
    #create the solo button 
    def solo_button(self):
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
        WHITE = (255,255,255)
        text_surf = FONT.render("SOLO", True, WHITE)
        text_rect = text_surf.get_rect(topleft=(self.config.window.width*0.45, self.config.window.height*0.4))
        return text_surf, text_rect

     #create the solo button 
    def multi_button(self):
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 22)
        WHITE = (255,255,255)
        text_surf = FONT.render("MULTI", True, WHITE)
        text_rect = text_surf.get_rect(topleft=(self.config.window.width*0.45, self.config.window.height*0.45))
        return text_surf, text_rect
    
    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""

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
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                #if flappy hit ground or pipe, end this and run the game over()
                await self.game_over()

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()

            # Update multiplayer if active
            if self.is_multiplayer and self.multiplayer:
                self.multiplayer.update(self.player)

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            
            # Draw remote players if in multiplayer mode
            if self.is_multiplayer and self.multiplayer:
                self.multiplayer.draw_remote_players()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

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
        self.background = Background(self.config)
        self.title = Title(self.config)
        self.floor = Floor(self.config)
        self.player = Player(self.config)
        self.welcome_message = WelcomeMessage(self.config)
        self.pipes = Pipes(self.config)
        self.game_over_message = GameOver(self.config)
        self.scoreboard = ScoreBoard(self.config)
        self.score = Score(self.config, self.player)
        self.medal = Medal(self.config, self.score)
        self.button = Button(self.config)