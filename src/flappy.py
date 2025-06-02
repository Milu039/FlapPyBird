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
    Skin,
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
    
    def skill_interface_buttons(self):
        """Create skill interface using images from config with vertical layout like first image"""
        buttons = []

        # Get skill images from config
        skills = self.config.images.skills

        # Vertical layout positions like the first image
        start_x = 80  # Left margin
        start_y = 200  # Starting Y position
        button_height = 80  # Height of each skill button frame
        button_width = 400  # Width of each skill button frame
        spacing = 20  # Space between buttons

        # Calculate positions for vertical layout
        positions = []
        for i in range(5):
            y_pos = start_y + (button_height + spacing) * i
            positions.append((start_x, y_pos))

        # Map skills to positions
        skill_order = [
            "speed_boost",
            "penetration", 
            "pipe_shift",
            "time_freeze",
            "teleport"
        ]

        # Skill display names
        skill_names = [
            "Speed boost",
            "Penetration",
            "Pipe shift", 
            "Time Freeze",
            "Teleport"
        ]

        for i, (skill_id, pos) in enumerate(zip(skill_order, positions)):
            img = skills[skill_id]
            # Position icon with some padding from the left edge of frame
            icon_x = pos[0] + 20
            icon_y = pos[1] + (button_height - img.get_height()) // 2  # Center vertically in frame
            img_rect = img.get_rect(topleft=(icon_x, icon_y))
            
            # Create frame rectangle
            frame_rect = pygame.Rect(pos[0], pos[1], button_width, button_height)
            
            skill_name = skill_names[i]
            buttons.append((img, img_rect, skill_id, skill_name, (icon_x, icon_y), frame_rect))

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

    def get_player_id(self, data):
        return self.network.send_receive_id(data)
    
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
                        return
                    if multi_button_rect.collidepoint(event.pos):
                        self.network = Network()
                        await self.game_room_interface()
                        return
                    if skill_button_rect.collidepoint(event.pos):
                        # Run the main skill interface
                        await self.main_skill_interface()
                        return
                    
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
                            return
                    if self.is_tap_event(event):
                        await self.play()
                        return

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
            return
        elif self.gamemode == "Multi":
            await self.multi_gameplay()
            return

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
                        return
                    elif self.button.rectRestart and self.button.rectRestart.collidepoint(event.pos):
                        self.restart()
                        await self.solo_ready_interface()
                        return
                    elif self.button.rectQuit and self.button.rectQuit.collidepoint(event.pos):
                        self.restart()
                        #after click back to main
                        await self.main_interface()
                        return
            
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
        return

    async def solo_gameplay(self):
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            btnBack, rectBack = self.back_button()
            if self.player.collided(self.pipes, self.floor):
                #if flappy hit ground or pipe, end this and run the game over()
                await self.solo_game_over()
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    await self.game_pause()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        await self.game_pause()
                        return
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
                        return
                    elif self.button.rectQuit and self.button.rectQuit.collidepoint(event.pos):
                        self.restart()
                        #after click back to main
                        await self.main_interface()
                        return

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
        
        # Initialize timing for room list updates
        last_room_update = 0
        update_interval = 1.0  # Update room list every 1 second
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Request initial room list
        self.network.send(self.mode.get_mode())
        room_list_data = self.network.receive_room_list()
        self.message.set_rooms(room_list_data)
        
        while True:
            # Get current time
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Only request room list update periodically
            if current_time - last_room_update >= update_interval:
                try:
                    # Set socket to non-blocking for this check
                    self.network.client.settimeout(0.05)  # 50ms timeout
                    self.network.send(self.mode.get_mode())
                    room_list_data = self.network.receive_room_list()
                    self.message.set_rooms(room_list_data)
                    last_room_update = current_time
                except:
                    # If timeout or error, just continue with existing room list
                    pass
                finally:
                    # Reset socket to blocking mode
                    self.network.client.settimeout(None)

            btnBack, rectBack = self.back_button()

            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self.check_quit_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rectBack.collidepoint(event.pos):
                        await self.main_interface()
                        return

                    for i, rect in enumerate(self.message.rectRoom):
                        if rect.collidepoint(event.pos):
                            self.selected_room = i  # Set selected index

                    if self.button.rectCreate.collidepoint(event.pos):
                        await self.create_room_interface()
                        return

                    if self.button.rectJoin.collidepoint(event.pos) and self.selected_room is not None:
                        self.roomPassword = self.message.rooms[self.selected_room].split(':')[2].strip()
                        if self.roomPassword == "":
                            self.message.room_num = self.message.rooms[self.selected_room].split(':')[1].strip()
                            # Add a small delay to ensure room list updates have stopped
                            await asyncio.sleep(0.1)
                            reply = self.get_player_id(f"Join Room:{self.message.room_num}")
                            permission = reply.split(":")[3]
                            await self.room_lobby_interface(permission)
                            return
                        else:
                            self.message.show_password_prompt = True
                            self.message.txtPassword = ""
                            self.message.password_error = False
                            self.button.show_password_prompt = True
                            self.message.password_active = True

                    if self.message.show_password_prompt:
                        if self.message.password_input_rect.collidepoint(event.pos):
                            self.message.password_active = True
                        else:
                            self.message.password_active = False

                    if self.message.show_password_prompt and self.button.show_password_prompt:
                        if hasattr(self.button, "rectEnter") and self.button.rectEnter.collidepoint(event.pos):
                            if self.message.txtPassword == self.roomPassword:
                                self.message.show_password_prompt = False
                                self.button.show_password_prompt = False
                                self.message.password_active = False
                                self.message.password_error = False
                                self.message.room_num = self.message.rooms[self.selected_room].split(':')[1].split(',')[0].strip()
                                reply = self.get_player_id(f"Join Room:{self.message.room_num}")
                                permission = reply.split(":")[3]
                                await self.room_lobby_interface(permission)
                                return
                            else:
                                self.message.password_error = True

                        elif hasattr(self.button, "rectCancel") and self.button.rectCancel.collidepoint(event.pos):
                            self.message.show_password_prompt = False
                            self.button.show_password_prompt = False
                            self.message.password_active = False
                            self.message.password_error = False

                if event.type == pygame.KEYDOWN and self.message.show_password_prompt and self.message.password_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.message.txtPassword = self.message.txtPassword[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.message.txtPassword == self.roomPassword:
                            self.message.show_password_prompt = False
                            self.button.show_password_prompt = False
                            self.message.password_active = False
                            self.message.password_error = False
                            self.message.room_num = self.message.rooms[self.selected_room].split(':')[1].split(',')[0].strip()
                            reply = self.get_player_id(f"Join Room:{self.message.room_num}")
                            permission = reply.split(":")[3]
                            await self.room_lobby_interface(permission)
                            return
                        else:
                            self.message.password_error = True
                    else:
                        self.message.txtPassword += event.unicode

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
                        self.network.send(f"Remove Room:{self.message.random_number}")
                        await self.game_room_interface()
                        return

                    if self.message.password_input_rect.collidepoint(event.pos):
                        self.message.password_active = True
                    else:
                        self.message.password_active = False

                    if self.button.rectCreate.collidepoint(event.pos):
                        self.network.kicked = False
                        self.message.password_active = False
                        reply = self.get_player_id(f"Create Room:{self.message.random_number}:{self.message.txtPassword}")
                        permission = reply.split(":")[3]
                        await self.room_lobby_interface(permission)
                        return

                if event.type == pygame.KEYDOWN and self.message.password_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.message.txtPassword = self.message.txtPassword[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.network.kicked = False
                        self.message.password_active = False
                        reply = self.get_player_id(f"Create Room:{self.message.random_number}:{self.message.txtPassword}")
                        permission = reply.split(":")[3]
                        await self.room_lobby_interface(permission)
                        return
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
            # Safety check for network ID
            if not self.network.id or self.network.id == "":
                print("Warning: Network ID is empty, defaulting to 0")
                self.network.id = "0"
            
            self.skin = Skin(self.config, self.network.id)
            self.mode.set_mode(f"Room Lobby: {state}")
            self.message.set_mode(self.mode.get_mode())
            self.container.set_mode(self.mode.get_mode())
            self.button.set_mode(self.mode.get_mode())
            self.message.player_id = self.network.id
            self.button.player_id = self.network.id
            
            # Initialize player name only if not already set
            if not hasattr(self.message, 'txtPlayerName') or not self.message.txtPlayerName:
                # Handle case where ID might be empty or invalid
                try:
                    player_number = int(self.network.id) + 1
                except (ValueError, TypeError):
                    player_number = 1  # Default to Player 1 if ID is invalid
                self.message.txtPlayerName = f"Player {player_number}"
            
            # Start the listener thread once when entering the lobby
            if not hasattr(self, '_lobby_listener_started'):
                self.network.start_lobby_listener()
                self._lobby_listener_started = True

            # Initialize player name if not already set
            if not hasattr(self.message, 'txtPlayerName') or not self.message.txtPlayerName:
                self.message.txtPlayerName = f"Player {int(self.network.id) + 1}"   

            while True:
           
                # Check if kicked
                if hasattr(self.network, "kicked") and self.network.kicked:
                    print("You have been kicked from the room.")
                    self.network.kicked = False  # Reset for future
                    # Cleanup before returning
                    self.network.stop_lobby_listener()
                    self._lobby_listener_started = False
                    await self.game_room_interface()
                    return
                
                # Check if room closed
                if hasattr(self.network, "room_closed") and self.network.room_closed:
                    print("Room has been closed by the host.")
                    self.network.room_closed = False  # Reset for future
                    # Cleanup before returning
                    self.network.stop_lobby_listener()
                    self._lobby_listener_started = False
                    await self.game_room_interface()
                    return
                
                if not self.message.change_name_active:
                    for p in self.network.lobby_state:
                        if p["player_id"] == int(self.network.id):
                            if p["name"] and p["name"].strip():
                                self.message.txtPlayerName = p["name"]

                btnBack, rectBack = self.back_button()

                if state == "host":
                    self.button.roomCapacity = int(len(self.network.lobby_state))
                    self.button.ready_count = sum(1 for player in self.network.lobby_state if player["ready"])

                for event in pygame.event.get():
                    self.check_quit_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if rectBack.collidepoint(event.pos):
                            if state == "host":
                                self.network.send(f"Remove Room:{self.message.room_num}")
                                self.network.stop_lobby_listener()
                                self._lobby_listener_started = False
                            elif state == "member":
                                self.network.send(f"Leave Room:{self.message.room_num}:{self.network.id}")
                                self.network.stop_lobby_listener()
                                self._lobby_listener_started = False
                            await self.game_room_interface()
                            return

                        if self.button.rectNextSkin.collidepoint(event.pos):
                            self.skin.next()
                        elif self.button.rectPreSkin.collidepoint(event.pos):
                            self.skin.previous()

                        if hasattr(self.message, "rectPlayer") and self.message.rectPlayer.collidepoint(event.pos):
                            self.message.show_name_prompt = True
                            self.message.txtPlayerName = self.message.txtPlayerName
                            self.message.name_error = False
                            self.button.show_name_prompt = True
                            self.message.change_name_active = True
                        else:
                            self.message.change_name_active = False

                        if self.message.name_input_rect.collidepoint(event.pos):
                            self.message.change_name_active = True
                        else:
                            self.message.change_name_active = False

                        if self.message.show_name_prompt and self.button.show_name_prompt:
                            if hasattr(self.button, "rectEnter") and self.button.rectEnter.collidepoint(event.pos):
                                if self.message.txtPlayerName != "":
                                    self.message.show_name_prompt = False
                                    self.button.show_name_prompt = False
                                    self.message.change_name_active = False
                                    self.message.txtPlayerName = self.message.txtPlayerName
                                else:
                                    self.message.name_error = True

                            elif hasattr(self.button, "rectCancel") and self.button.rectCancel.collidepoint(event.pos):
                                self.message.show_name_prompt = False
                                self.button.show_name_prompt = False
                                self.message.change_name_active = False
                                self.message.name_error = False

                        for i, rect in enumerate(self.button.rectKicks):
                            if rect.collidepoint(event.pos):
                                target_id = self.button.kick_targets[i]
                                self.network.send(f"Kick:{self.message.room_num}:{target_id}")
                                break

                        if int(self.network.id) > 0:
                            if not self.button.isReady and hasattr(self.button, "rectReady") and self.button.rectReady.collidepoint(event.pos):
                                self.message.isHost = False
                                self.message.isReady = True
                                self.button.isReady = True

                            elif self.button.isReady and hasattr(self.button, "rectCancel") and self.button.rectCancel.collidepoint(event.pos):
                                self.message.isHost = False
                                self.message.isReady = False
                                self.button.isReady = False
                        else:
                            self.message.isHost = True
                            self.message.isReady = False
                        
                        if hasattr(self.button, "rectStart") and self.button.rectStart.collidepoint(event.pos):
                            self.network.stop_lobby_listener()
                            self._lobby_listener_started = False
                            await self.multi_gameplay()
                            return

                    if event.type == pygame.KEYDOWN and self.message.show_name_prompt and self.message.change_name_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.message.txtPlayerName = self.message.txtPlayerName[:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.message.txtPlayerName != "":
                                self.message.show_name_prompt = False
                                self.button.show_name_prompt = False
                                self.message.change_name_active = False
                                self.message.txtPlayerName = self.message.txtPlayerName
                            else:
                                    self.message.name_error = True
                        else:
                            self.message.txtPlayerName += event.unicode

                self.network.send(f"Update:{self.message.room_num}:{self.network.id}:{self.message.txtPlayerName}:{self.skin.get_skin_id()}:{self.message.isReady}:{self.message.isHost}")
                
                self.background.tick()
                self.floor.tick()
                self.container.tick()
                self.skin.tick()
                self.config.screen.blit(btnBack, rectBack)
                

                # Draw all players
                if state == "host":
                    self.button.update_kick_buttons(self.network.lobby_state)
                self.skin.draw_other(self.network.lobby_state)
                self.message.draw_name(self.network.lobby_state)
                self.message.tick()
                self.button.tick()
                

                pygame.display.update()
                await asyncio.sleep(0)
                self.config.tick()

    async def multi_gameplay(self):
        self.player.set_mode(PlayerMode.MULTI)
        countdown_timer = CountdownTimer(self.config)
        countdown_timer.pause_with_countdown()
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

    def get_skill_description(self, skill_id):
        """Get description for a specific skill"""
        descriptions = {
            "speed_boost": [
                " ",
                "Speed up the player in 5 seconds",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                "*only available for multi"
            ],
            "penetration": [
                " ",
                "Ignore the pipe for 3 seconds",
                " ",
                " ",
                " ",
                " ",
                " ",
                " ",
                "*only available for multi"
            ],
            "pipe_shift": [
                " ",
                "Change the position of the pipe",
                "either up or down during the ",
                "game",
                " ",
                " ",
                " ",
                " ",
                "*only available for multi"
            ],
            "time_freeze": [
                " ",
                "Freeze the first player for 2",
                "seconds",
                " ",
                " ",
                " ",
                " ",
                " ",
                "*only available for multi"
            ],
            "teleport": [
                " ",
                "Teleport the player in front to",
                "the back",
                " ",
                " ",
                " ",
                " ",
                " ",
                "*only available for multi"
            ]
        }
        return descriptions.get(skill_id, ["Skill not found"])

    async def main_skill_interface(self):
        """Main skill interface with 5 skill buttons"""
        self.mode.set_mode("Main Skill")
        selected_skill = None  # Track which skill is selected for description

        while True:
            back_button_surf, back_button_rect = self.back_button()
            skill_buttons = self.skill_interface_buttons()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if back_button_rect.collidepoint(event.pos):
                        await self.main_interface()

                    # Check which skill button was clicked
                    for img, img_rect, skill_id, skill_name, pos, frame_rect in skill_buttons:
                        if frame_rect.collidepoint(event.pos):
                            # Toggle selection
                            if selected_skill == skill_id:
                                selected_skill = None
                            else:
                                selected_skill = skill_id

            self.background.tick()
            self.floor.tick()

            # Draw skill ability title image (only once, smaller size)
            skill_ability_img = self.config.images.message["skill_ability"]
            # Scale down the title image to make it smaller
            scaled_title = pygame.transform.scale(skill_ability_img, (350, 70))
            title_rect = scaled_title.get_rect(centerx=self.config.window.width // 2, y=50)
            self.config.screen.blit(scaled_title, title_rect)

            # Create font for skill names
            skill_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 16)

            # Draw skill buttons with frames, icons and names
            for img, img_rect, skill_id, skill_name, pos, frame_rect in skill_buttons:
                # Determine if this skill is selected
                is_selected = (selected_skill == skill_id)
                
                # Main frame colors (always the same)
                main_frame_color = (221, 216, 148)  # Default color #DDD894
                border_radius = 15
                
                # Draw main frame behind the skill
                pygame.draw.rect(self.config.screen, main_frame_color, frame_rect, border_radius=border_radius)
                pygame.draw.rect(self.config.screen, (0, 0, 0), frame_rect, width=2, border_radius=border_radius)
                
                # Create smaller inner frame for content (icon + text area)
                inner_padding_left = -2   # Distance from left edge of main frame
                inner_padding_top = 2     # Distance from top edge of main frame
                inner_padding_right = 13 # Distance from right edge of main frame  
                inner_padding_bottom = 15 # Distance from bottom edge of main frame
                
                inner_frame_x = pos[0] + inner_padding_left
                inner_frame_y = pos[1] + inner_padding_top
                inner_frame_width = 380 - inner_padding_left - inner_padding_right
                inner_frame_height = 80 - inner_padding_top - inner_padding_bottom
                inner_frame_rect = pygame.Rect(inner_frame_x, inner_frame_y, inner_frame_width, inner_frame_height)

                # Inner frame colors based on selection
                if is_selected:
                    inner_frame_color = (204, 192, 148)  # 25% blend of #533000 with original beige
                    inner_border_width = 0
                else:
                    inner_frame_color = main_frame_color  # Same as main frame (invisible effect)
                    inner_border_width = 0  # No border when not selected
                
                # Draw inner frame
                inner_border_radius = 10
                pygame.draw.rect(self.config.screen, inner_frame_color, inner_frame_rect, border_radius=inner_border_radius)
                if inner_border_width > 0:
                    pygame.draw.rect(self.config.screen, (0, 0, 0), inner_frame_rect, width=inner_border_width, border_radius=inner_border_radius)
                
                # Draw skill icon (no tinting needed since we have inner frame)
                self.config.screen.blit(img, img_rect)
                
                # Draw skill name next to the icon
                text_surf = skill_font.render(skill_name, True, (0, 0, 0))  # Always black text
                text_x = pos[0] + img.get_width() + 20  # Position text to the right of icon
                text_y = pos[1] + (img.get_height() - text_surf.get_height()) // 2  # Center vertically with icon
                self.config.screen.blit(text_surf, (text_x, text_y))

            # Draw video and description frame if a skill is selected
            if selected_skill:
                # Main info frame position (beside the skill buttons)
                info_frame_x = 520  # Right of skill buttons
                info_frame_y = 200  # Same as first skill button
                info_frame_width = 480
                info_frame_height = 480
                
                # Draw main info frame with same color
                info_frame_rect = pygame.Rect(info_frame_x, info_frame_y, info_frame_width, info_frame_height)
                frame_color = (221, 216, 148)  # Same color as skill buttons
                border_radius = 15
                pygame.draw.rect(self.config.screen, frame_color, info_frame_rect, border_radius=border_radius)
                pygame.draw.rect(self.config.screen, (0, 0, 0), info_frame_rect, width=2, border_radius=border_radius)
                
                # Video area (upper part of the frame)
                video_area_x = info_frame_x + 20
                video_area_y = info_frame_y + 20
                video_area_width = info_frame_width - 40
                video_area_height = 180  # Space reserved for video
                
                # Draw placeholder for video area (you can replace this with actual video rendering)
                video_placeholder_rect = pygame.Rect(video_area_x, video_area_y, video_area_width, video_area_height)
                pygame.draw.rect(self.config.screen, (200, 200, 200), video_placeholder_rect)  # Light gray placeholder
                pygame.draw.rect(self.config.screen, (0, 0, 0), video_placeholder_rect, width=2)
                
                # Add "VIDEO PREVIEW" text in the placeholder
                video_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 12)
                video_text = video_font.render("VIDEO PREVIEW", True, (100, 100, 100))
                video_text_rect = video_text.get_rect(center=video_placeholder_rect.center)
                self.config.screen.blit(video_text, video_text_rect)
                
                # Description area (lower part of the frame)
                desc_start_y = video_area_y + video_area_height + 20  # Start below video area with some spacing
                
                # Get description text
                description_lines = self.get_skill_description(selected_skill)
                
                # Draw description text
                desc_font = pygame.font.Font("assets/font/PressStart2P-Regular.ttf", 14)
                line_height = 25
                
                for i, line in enumerate(description_lines):
                    if line:  # Skip empty lines for spacing
                        text_surf = desc_font.render(line, True, (0, 0, 0))
                        text_x = info_frame_x + 20  # Padding from left edge
                        text_y = desc_start_y + (i * line_height)
                        # Make sure text doesn't go outside the frame
                        if text_y + text_surf.get_height() < info_frame_y + info_frame_height - 20:
                            self.config.screen.blit(text_surf, (text_x, text_y))

            # Draw back button
            self.config.screen.blit(back_button_surf, back_button_rect)

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

        