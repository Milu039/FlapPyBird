import asyncio
import sys
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Title,
    Container,
    Floor,
    ScoreBoard,
    Medal,
    Pipes,
    Player,
    PlayerMode,
    Score,
    Message,
    Button,
    Timer,
    CountdownTimer,
)
from .utils import GameConfig, Images, Sounds, Window, Mode, Network
    
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
    
    # New skill interface buttons
    def skill_interface_buttons(self):
        """Create skill interface using images from config"""
        buttons = []

        # Get skill images from config
        skills = self.config.images.skills
        messages = self.config.images.message

        # Set interface mode
        self.mode.set_mode("Skill Ability")
        self.message.set_mode(self.mode.get_mode())

        # Skill positions (adjust these values based on your image sizes)
        positions = [
            (self.config.window.width // 2 - 200, 200),  # Speed Boost
            (self.config.window.width // 2 + 50, 200),  # Penetration
            (self.config.window.width // 2 - 150, 400),  # Pipe Shift
            (self.config.window.width // 2 + 50, 400),  # Time Freeze
            (self.config.window.width // 2 - 75, 550)  # Teleport (center bottom)
        ]

        # Map skills to positions
        skill_order = [
            "speed_boost",
            "penetration",
            "pipe_shift",
            "time_freeze",
            "teleport"
        ]

        for skill_id, pos in zip(skill_order, positions):
            img = skills[skill_id]
            img_rect = img.get_rect(topleft=pos)
            buttons.append((img, img_rect, skill_id))

        return buttons

    def individual_skill_button(self, skill_name):
        """Create button for individual skill interface"""
        FONT = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 24)
        WHITE = (255, 255, 255)
        text_surf = FONT.render(f"{skill_name.upper()} SKILL", True, WHITE)
        text_rect = text_surf.get_rect(
            centerx=self.config.window.width // 2,
            centery=self.config.window.height // 2
        )
        return text_surf, text_rect
    
    def back_button(self):
        btnBack = self.config.images.buttons["back"]
        posBack = (30, 30)
        rectBack = pygame.Rect(posBack[0], posBack[1], btnBack.get_width(), btnBack.get_height())
        return btnBack, rectBack

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
    
    def restart(self):
        self.container = Container(self.config, self.mode)
        self.floor = Floor(self.config)
        self.message = Message(self.config, self.mode)
        self.player = Player(self.config)
        self.score = Score(self.config, self.player)
        self.pipes = Pipes(self.config)
        self.medal = Medal(self.config, self.score)
        self.button = Button(self.config, self.mode)
        self.timer = Timer(self.config)
        self.countdown = CountdownTimer(self.config)
    
    async def start(self):
        while True:
                self.mode = Mode()
                self.background = Background(self.config)
                self.title = Title(self.config)
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #click the solo button , run solo_ready_interface screen
                    if solo_button_rect.collidepoint(event.pos):
                        await self.solo_ready_interface()
                    if multi_button_rect.collidepoint(event.pos):
                        self.network = Network()
                        await self.game_room_interface()
                    if skill_button_rect.collidepoint(event.pos):
                        # Run the main skill interface
                        await self.main_skill_interface()
                    
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
            btnBack, rectBack = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if rectBack.collidepoint(event.pos):
                            self.restart()
                            await self.main_interface()
                    if self.is_tap_event(event):
                        await self.play()

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.message.tick()
            self.config.screen.blit(btnBack, rectBack)
            
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.rectResume and self.button.rectResume.collidepoint(event.pos):
                        await self.game_resume()
                    elif self.button.rectRestart and self.button.rectRestart.collidepoint(event.pos):
                        self.restart()
                        await self.solo_ready_interface()
                    elif self.button.rectQuit and self.button.rectQuit.collidepoint(event.pos):
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
            btnBack, rectBack = self.back_button()
            if self.player.collided(self.pipes, self.floor):
                #if flappy hit ground or pipe, end this and run the game over()
                await self.solo_game_over()

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    await self.game_pause()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        await self.game_pause()
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.config.screen.blit(btnBack, rectBack)
            
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.rectRestart and self.button.rectRestart.collidepoint(event.pos):
                        self.restart()
                        await self.solo_ready_interface()
                    elif self.button.rectQuit and self.button.rectQuit.collidepoint(event.pos):
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

    async def game_room_interface(self): # receive the room list from the server
        self.restart()
        self.mode.set_mode("Game Room")
        self.message.set_mode(self.mode.get_mode())
        self.container.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())
        self.selected_room = None
        
        while True:
            self.network.send(self.mode.get_mode())
            room_list_data = self.network.receive_room_list()
            self.message.set_rooms(room_list_data)
            btnBack, rectBack = self.back_button()
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        self.restart()
                        await self.main_interface()

                    for i, rect in enumerate(self.message.rectRoom):
                        if rect.collidepoint(event.pos):
                            self.selected_room = i  # Set selected index

                    if self.button.rectCreate.collidepoint(event.pos):
                        await self.create_room_interface()

                    if self.button.rectJoin.collidepoint(event.pos) and self.selected_room != None:
                        await self.room_lobby_interface("member")

            self.background.tick()
            self.message.tick()
            self.floor.tick()
            self.container.tick()
            self.message.draw(selected_room=self.selected_room, mouse_pos=mouse_pos)
            self.config.screen.blit(btnBack, rectBack)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def create_room_interface(self): # send the create room request to the server
        self.mode.set_mode("Create Room")
        self.message.set_mode(self.mode.get_mode())
        self.container.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())

        while True:
            btnBack, rectBack = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        await self.game_room_interface()

                    if self.message.password_input_rect.collidepoint(event.pos):
                        self.message.password_active = True
                    else:
                        self.message.password_active = False

                    if self.button.rectCreate.collidepoint(event.pos):
                        self.message.password_active = False
                        self.network.send(f"Create Room: {self.message.random_number}, {self.message.txtPassword}")
                        await self.room_lobby_interface("host")

                if event.type == pygame.KEYDOWN and self.message.password_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.message.txtPassword = self.message.txtPassword[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.message.password_active = False
                        self.network.send(f"Create Room: {self.message.random_number} {self.message.txtPassword}")
                        await self.room_lobby_interface("host")
                    else:
                        self.message.txtPassword += event.unicode

            self.background.tick()
            self.container.tick()
            self.message.tick()
            self.floor.tick()
            self.config.screen.blit(btnBack, rectBack)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def room_lobby_interface(self, state):
        self.mode.set_mode(f"Room Lobby: {state}")
        self.message.set_mode(self.mode.get_mode())
        self.button.set_mode(self.mode.get_mode())

        while True:
            btnBack, rectBack = self.back_button()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        await self.game_room_interface()
                    if self.button.rectReady.collidepoint(event.pos):
                        await self.multi_gameplay()

            self.background.tick()
            self.message.tick()
            self.container.tick()
            self.floor.tick()
            self.config.screen.blit(btnBack, rectBack)
            self.button.tick()
            
            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def multi_gameplay(self):
        self.player.set_mode(PlayerMode.NORMAL)
        while True:
            if self.player.collided_push(self.pipes):
                pass
            if self.player.respawn(self.config):
                pass    
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
                if self.is_tap_event(event):
                    if self.button.rectRestart and self.button.rectRestart.collidepoint(event.pos):
                        self.restart()
                        await self.room_lobby_interface()
                    elif self.button.rectQuit and self.button.rectQuit.collidepoint(event.pos):
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

    async def main_skill_interface(self):
        """Main skill interface with 5 skill buttons"""
        self.mode.set_mode("Main Skill")

        while True:
            back_button_surf, back_button_rect = self.back_button()
            skill_buttons = self.skill_interface_buttons()

            title_img = self.config.images.message["skill_ability"]
            title_rect = title_img.get_rect(centerx=self.config.window.width // 2, top=50)

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if back_button_rect.collidepoint(event.pos):
                        await self.main_interface()

                    # Check which skill button was clicked
                    for text_surf, text_rect, skill_id in skill_buttons:
                        if text_rect.collidepoint(event.pos):
                            await self.individual_skill_interface(skill_id)

            self.background.tick()
            self.floor.tick()
            self.message.tick()

            # Draw title
            title_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 32)
            title_surf = title_font.render("SKILL TUTORIAL", True, (255, 255, 255))
            title_rect = title_surf.get_rect(centerx=self.config.window.width // 2, y=100)
            self.config.screen.blit(title_surf, title_rect)

            # Draw skill buttons
            for text_surf, text_rect, _ in skill_buttons:
                # Draw button background (optional - you can use sprites here)
                pygame.draw.rect(self.config.screen, (100, 100, 100), text_rect.inflate(20, 10))
                pygame.draw.rect(self.config.screen, (255, 255, 255), text_rect.inflate(20, 10), 2)
                self.config.screen.blit(text_surf, text_rect)

            # Draw back button
            self.config.screen.blit(back_button_surf, back_button_rect)

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def individual_skill_interface(self, skill_name):
        """Individual skill interface for each skill"""
        self.mode.set_mode(f"{skill_name.title()} Skill")

        while True:
            back_button_surf, back_button_rect = self.back_button()
            skill_text_surf, skill_text_rect = self.individual_skill_button(skill_name)

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if back_button_rect.collidepoint(event.pos):
                        await self.main_skill_interface()

            self.background.tick()
            self.floor.tick()

            # Draw skill-specific content
            title_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 28)
            title_surf = title_font.render(f"{skill_name.upper().replace('_', ' ')} TUTORIAL", True, (255, 255, 255))
            title_rect = title_surf.get_rect(centerx=self.config.window.width // 2, y=150)
            self.config.screen.blit(title_surf, title_rect)

            # Add skill-specific instructions based on skill type
            instruction_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 16)
            instructions = self.get_skill_instructions(skill_name)

            y_offset = 250
            for instruction in instructions:
                instruction_surf = instruction_font.render(instruction, True, (255, 255, 255))
                instruction_rect = instruction_surf.get_rect(centerx=self.config.window.width // 2, y=y_offset)
                self.config.screen.blit(instruction_surf, instruction_rect)
                y_offset += 40

            # Draw back button
            self.config.screen.blit(back_button_surf, back_button_rect)

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def get_skill_instructions(self, skill_name):
        """Get instructions for each skill"""
        instructions = {
            "speed_boost": [
                "Speed Boost increases your movement speed",
                "Press SHIFT to activate speed boost",
                "Duration: 5 seconds",
                "Cooldown: 10 seconds"
            ],
            "destination": [
                "Destination teleports you to a safe location",
                "Press D to activate destination",
                "Automatically finds safe spot",
                "Cooldown: 15 seconds"
            ],
            "time_freeze": [
                "Time Freeze stops all obstacles",
                "Press T to activate time freeze",
                "Duration: 3 seconds",
                "Cooldown: 20 seconds"
            ],
            "power_fruit": [
                "Power Fruit gives temporary invincibility",
                "Press F to activate power fruit",
                "Duration: 4 seconds",
                "Cooldown: 25 seconds"
            ],
            "teleport": [
                "Teleport moves you instantly forward",
                "Press E to activate teleport",
                "Distance: Fixed amount forward",
                "Cooldown: 8 seconds"
            ]
        }

        return instructions.get(skill_name, ["Instructions not available"])
