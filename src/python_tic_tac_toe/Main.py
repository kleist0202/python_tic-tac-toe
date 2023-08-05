import pygame
import sys
from python_tic_tac_toe.gui import Color, Colors
from python_tic_tac_toe.Fps import Fps
from python_tic_tac_toe.TicTacToe import TicTacToe

import asyncio
import websockets
import pickle
import nepygui
import argparse


class Com:
    def __init__(self, screen, game, window) -> None:
        self.screen = screen
        self.game = game
        self.window = window

        self.current_count = self.count_fields(self.game.g)
        self.current_mng = self.game.mng_pressed

    def count_fields(self, L):
        count = 0
        for i in range(3):
            for j in range(3):
                if L[i][j] == "":
                    count += 1
        return count

    async def hosted_game(self, websocket, path):
        rt = asyncio.ensure_future(self.recive(websocket))
        st = asyncio.ensure_future(self.send(websocket))
        await self.game_loop(websocket, "player_1")

        done, pending = await asyncio.wait(
            [rt, st],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def hello_host(self, uri):
        async with websockets.connect(uri) as websocket:
            rt = asyncio.ensure_future(self.recive(websocket))
            st = asyncio.ensure_future(self.send(websocket))
            await self.game_loop(websocket, "player_2")

            done, pending = await asyncio.wait(
                [rt, st],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    async def game_loop(self, websocket, player):
        print('starting game loop...')
        self.game.draw_grid(player, self.screen, self.window)
        while True:
            await websocket.send('{"message":"PING"}')
            # self.game.window_resize_callback(
            #     self.screen.get_size(), self.game.calc_grid)

            # # fps management
            # self.fps.fps()
            # self.fps.show_fps(self.screen)
            #
            # pygame.display.flip()

            # self.clock.tick(60)
            await asyncio.sleep(0.01)

    async def recive(self, websocket):
        print('starting rcv loop...')
        while True:
            msg = await websocket.recv()
            msg = pickle.loads(msg)
            self.game.g, self.game.turn, mng_pressed = msg
            if mng_pressed:
                self.game.make_new_game()
            self.game.mng_pressed = False

            print("receive")
            await asyncio.sleep(0.01)

    async def send(self, websocket):
        print('starting send loop...')
        while True:
            if self.current_count != self.count_fields(self.game.g) or self.current_mng != self.game.mng_pressed:
                data = [self.game.g, self.game.turn,
                        self.game.mng_pressed]
                await websocket.send(pickle.dumps(data))
                print("send")
                self.current_count = self.count_fields(self.game.g)
                self.current_mng = self.game.mng_pressed
                self.game.mng_pressed = False
            await asyncio.sleep(0.01)

    def create_host(self, _, address_entry, port_entry):
        address = address_entry.get_entry_value()
        port = port_entry.get_entry_value()
        if address == "" or port == "":
            return
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(self.hosted_game, address, port))
        asyncio.get_event_loop().run_forever()

    def connect(self, _, address_entry, port_entry):
        address = address_entry.get_entry_value()
        port = port_entry.get_entry_value()
        uri = "ws://" + address + ":" + port
        asyncio.get_event_loop().run_until_complete(self.hello_host(uri))


class Tic:
    def __init__(self, window) -> None:
        self.grid_thickness = 40
        self.offset = 50
        self.squares_num = 3
        self.clickables = []
        self.vertical_lines = []
        self.horizontal_lines = []
        self.g = [["" for i in range(self.squares_num)]
                  for j in range(self.squares_num)]

        self.turn = 1
        self.player = "player_1"
        self.mark = ""
        self.running = True
        self.game_running = True
        self.mng_pressed = False

        self.player1_points = 0
        self.player2_points = 0

        self.choice = "menu"
        self.multiplayer_choice = "menu"
        self.start_multiplayer = False
        self.is_running = []
        self.window = window
        self.x_size, self.y_size = 0, 0

        # init
        self.calc_grid()

    def calc_grid(self):
        self.x_size, self.y_size = self.window.get_screen().get_size()
        self.y_offset = self.offset

        if self.x_size < self.y_size:
            smaller_dim = self.x_size
            greater_dim = self.y_size
            self.grid_thickness = greater_dim // 90

            self.grid_size = smaller_dim - 2*self.y_offset - self.grid_thickness
            self.x_offset = self.y_offset
            self.y_offset = (greater_dim - self.grid_size) / 2.0
        else:
            smaller_dim = self.y_size
            greater_dim = self.x_size
            self.grid_thickness = greater_dim // 90

            self.grid_size = smaller_dim - 2*self.y_offset - self.grid_thickness
            self.x_offset = (greater_dim - self.grid_size) / 2.0

        self.square_size = self.grid_size / self.squares_num
        if self.square_size - self.grid_thickness < 1:
            self.square_size = self.grid_thickness

    def resize_grid(self):
        self.calc_grid()
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                x = int(self.x_offset+i*self.square_size+self.grid_thickness/2)
                y = int(self.y_offset+j*self.square_size+self.grid_thickness)
                w = int(self.square_size-self.grid_thickness)
                h = int(self.square_size-self.grid_thickness)
                ci = i * 3 + j
                self.clickables[ci].set_pos(x, y)
                self.clickables[ci].set_size(w, h)

        for i, frame in enumerate(self.horizontal_lines):
            x = int(self.x_offset-self.grid_thickness/2)
            y = int(self.y_offset+i*self.square_size)
            w = int(self.grid_size+self.grid_thickness)
            h = self.grid_thickness
            frame.set_pos(x, y)
            frame.set_size(w, h)

        for i, frame in enumerate(self.vertical_lines):
            x = int(self.x_offset+i*self.square_size-self.grid_thickness/2)
            y = int(self.y_offset)
            w = self.grid_thickness
            h = int(self.grid_size+self.grid_thickness)
            frame.set_pos(x, y)
            frame.set_size(w, h)

        self.win_screen.set_pos(0, self.y_size//2-50//2)
        self.win_screen.set_size(w=self.x_size, h=self.win_screen.h)

    def init_game_grid(self):
        # draw game
        # horizontal lines
        for i in range(4):
            f = nepygui.Frame(
                    fill=Color.Black,
                    x=int(self.x_offset-self.grid_thickness/2),
                    y=int(self.y_offset+i*self.square_size),
                    w=int(self.grid_size+self.grid_thickness),
                    h=self.grid_thickness,
                    gradient=False)
            self.horizontal_lines.append(f)
            self.window.add_to_menu(f, "game")
        # vertical lines
        for i in range(4):
            f = nepygui.Frame(
                    fill=Color.Black,
                    x=int(self.x_offset+i*self.square_size-self.grid_thickness/2),
                    y=int(self.y_offset),
                    w=self.grid_thickness,
                    h=int(self.grid_size+self.grid_thickness),
                    gradient=False)
            self.vertical_lines.append(f)
            self.window.add_to_menu(f, "game")

        # buttons
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                self.clickables.append(
                    Clickable(
                        x=int(self.x_offset+i*self.square_size+self.grid_thickness/2),
                        y=int(self.y_offset+j*self.square_size+self.grid_thickness),
                        w=int(self.square_size-self.grid_thickness),
                        h=int(self.square_size-self.grid_thickness),
                        func=self.square_clicked)
                )

        for clickable in self.clickables:
            self.window.add_to_menu(clickable, "game")

        # info frames
        self.info_left_layout = nepygui.VLayout(self.window, orientation="NW")
        self.info_right_layout = nepygui.VLayout(self.window, orientation="NE")

        self.win_screen = nepygui.TextFrame(
            y=self.y_size//2-50//2, w=self.x_size, anchor="C", fontsize=20, h=50, gradient=True)

        self.win_screen_layout = nepygui.HLayout(self.window, "C")
        self.win_screen_layout.add_widget(self.win_screen)
        self.win_screen.hide(True)

        self.info_player1 = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=True,
                                      text="Player 1", w=100, h=20)
        self.info_player2 = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=True,
                                      text="Player 2", w=100, h=20)

        self.info_player1_points = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=False,
                                             text="0", w=100, h=20)
        self.info_player2_points = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=False,
                                             text="0", w=100, h=20)

        self.info_left_layout.add_widget(self.info_player1)
        self.info_left_layout.add_widget(self.info_player1_points)
        self.info_right_layout.add_widget(self.info_player2)
        self.info_right_layout.add_widget(self.info_player2_points)

        # whose turn
        self.whose_turn = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Black, fontsize=14, bold=True,
                                    text="---", w=100, h=20)
        self.whose_turn_layout = nepygui.HLayout(self.window, "N", 0, 20)
        self.whose_turn_layout.add_widget(self.whose_turn)

        # new game button
        self.new_game_button = nepygui.Button(
            w=100, h=30, text="New game", bordercolor=Color.Black, gradient=False, fill=Color.DarkGray, func=self.make_new_game)
        self.new_game_layout = nepygui.HLayout(self.window, "SW", 10, -10)
        self.new_game_layout.add_widget(self.new_game_button)
        self.new_game_button.block(True)

        # return to menu button
        self.return_to_menu_button = nepygui.Button(
            w=150, h=30, text="Return to menu", bordercolor=Color.Black, gradient=False, fill=Color.DarkGray, func=self.return_to_menu)
        self.return_to_menu_layout = nepygui.HLayout(self.window, "SE", -10, -10)
        self.return_to_menu_layout.add_widget(self.return_to_menu_button)

        self.window.add_to_menu(self.info_left_layout, "game")
        self.window.add_to_menu(self.info_right_layout, "game")
        self.window.add_to_menu(self.win_screen_layout, "game")
        self.window.add_to_menu(self.new_game_layout, "game")
        self.window.add_to_menu(self.whose_turn_layout, "game")
        self.window.add_to_menu(self.return_to_menu_layout, "game")
        self.window.resize_callback_func = self.resize_grid

        # turn init
        self.set_turn()

    def switch_to_game(self, _):
        self.info_player1_points.set_text(str(self.player1_points))
        self.info_player2_points.set_text(str(self.player2_points))
        self.window.switch_menus("game")
    
    def square_clicked(self, button):
        i_noted = 0
        j_noted = 0
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                current_index = i * 3 + j
                temp_clickable = self.clickables[current_index]
                if id(button) == id(temp_clickable):
                    i_noted = i
                    j_noted = j
                    break

        if button.get_mark() == "":
            if self.player == "player_1":
                button.set_mark("X")
                self.g[i_noted][j_noted] = "X"
            elif self.player == "player_2":
                button.set_mark("O")
                self.g[i_noted][j_noted] = "O"
            else:
                raise Exception

            self.check_result()

            if self.player == "player_2":
                self.player = "player_1"
            elif self.player == "player_1":
                self.player = "player_2"

            self.set_turn()

    def make_new_game(self, _):
        self.mng_pressed = True
        self.game_running = True
        self.win_screen.hide(True)
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                self.g[i][j] = ""
                self.clickables[i * 3 + j].set_mark("")

        for clickable in self.clickables:
            clickable.block(False)

        self.new_game_button.block(True)

    def return_to_menu(self, _):
        self.player1_points = 0
        self.player2_points = 0
        self.window.switch_menus("default")
        self.make_new_game(None)

    def set_turn(self):
        if self.player == "player_1":
            self.whose_turn.set_text("<---")
            self.whose_turn.set_color(Color.Blue)
        elif self.player == "player_2":
            self.whose_turn.set_text("--->")
            self.whose_turn.set_color(Color.Red)
        else:
            raise Exception

    def check_result(self):
        if self.check_vertical(self.g, "X") or self.check_horizontal(self.g, "X") or self.check_diagonally(self.g, "X"):
            if self.game_running:
                self.resize_grid()
                self.player1_points += 1
                self.win_screen.set_text("Player 1 has won!")
                self.win_screen.set_color(Color.Blue)
            self.game_running = False
            self.win_screen.set_size(w=self.x_size, h=50)
        elif self.check_vertical(self.g, "O") or self.check_horizontal(self.g, "O") or self.check_diagonally(self.g, "O"):
            if self.game_running:
                self.resize_grid()
                self.player2_points += 1
                self.win_screen.set_text("Player 2 has won!")
                self.win_screen.set_color(Color.Red)
            self.game_running = False
        elif self.draw_check():
            if self.game_running:
                self.resize_grid()
                self.win_screen.set_text("Draw")
                self.win_screen.set_color(Color.Black)
            self.game_running = False
        else:
            pass

        if not self.game_running:
            self.win_screen.hide(False)
            for clickable in self.clickables:
                clickable.block(True)
            self.new_game_button.block(False)

        self.info_player1_points.set_text(str(self.player1_points))
        self.info_player2_points.set_text(str(self.player2_points))

    def check_vertical(self, whole, mark):
        for row in whole:
            if all(x == mark for x in row):
                return True
        return False

    def check_horizontal(self, whole, mark):
        return all(elem[0] == mark for elem in whole) or \
            all(elem[1] == mark for elem in whole) or \
            all(elem[2] == mark for elem in whole)

    def check_diagonally(self, whole, mark):
        if whole[0][0] == whole[1][1] == whole[2][2] == mark:
            return True
        elif whole[0][2] == whole[1][1] == whole[2][0] == mark:
            return True
        else:
            return False

    def draw_check(self):
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                if self.g[i][j] == "":
                    return False
        return True


class Clickable(nepygui.Button):
    def __init__(self, *, x, y, w, h, func) -> None:
        super().__init__(x=x, y=y, w=w, h=h, func=func)
        self.mark = ""

    def set_mark(self, mark):
        self.mark = mark

    def get_mark(self):
        return self.mark

    def get_rect(self):
        return self.x, self.y, self.w, self.h

    def draw(self, display, mouse_pos, mouse_key, keys=0, delta_time=0, event_list=[]):
        nepygui.Button.draw(self, display, mouse_pos, mouse_key)
        self.draw_mark(display)

    def draw_mark(self, screen):
        if self.mark == "X":
            self.draw_X(screen, int(self.w/7))
        elif self.mark == "O":
            self.draw_O(screen, self.w/2.5)
        else:
            pass

    def draw_O(self, screen, r):
        pygame.draw.circle(screen, Color.Red, (self.x+self.w/2, self.y+self.h/2), r, int(self.w/10))

    def draw_X(self, screen, t):
        space = self.w/7
        pygame.draw.line(screen, Color.Blue, (self.x+space, self.y +
                         space), (self.x+self.w-space, self.y+self.h-space), t)
        pygame.draw.line(screen, Color.Blue, (self.x+space, self.y +
                         self.h-space), (self.x+self.w-space, self.y+space), t)

def main():
    p = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    args = p.parse_args()
    w = nepygui.Window(**vars(args))
    e = nepygui.EntryWidget(x=400, y=400, w=200, h=60, borderthickness=6)
    e2 = nepygui.EntryWidget(x=400, y=200, w=200, h=60)

    vlayout = nepygui.VLayout(w, orientation="C")

    vlayout.add_widget(e2)
    vlayout.add_widget(e)

    w.set_screen_color(*Color.Gray)
    w.init_window()
    game = Tic(w)
    com = Com(w, game, w)


    labels_layout = nepygui.HLayout(w, orientation="C", y_start=-35)
    label1 = nepygui.Label(text="Address:", w=100, h=20, anchor="W")
    label2 = nepygui.Label(text="Port:", w=100, h=20, anchor="W")
    labels_layout.add_widget(label1, 150)
    labels_layout.add_widget(label2)

    entries_layout = nepygui.HLayout(w, orientation="C", y_start=0)
    entry_address = nepygui.EntryWidget(w=200, h=50)
    entry_port = nepygui.EntryWidget(w=100, h=50)
    entries_layout.add_widget(entry_address, 50)
    entries_layout.add_widget(entry_port)

    entry_address.set_entry_value("localhost")
    entry_port.set_entry_value("8765")

    def exit_this(_):
        w.exit()

    buttons_layout = nepygui.HLayout(w, orientation="C", y_start=70)
    host_button = nepygui.Button(gradient=False, text="Host", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda: com.create_host(entry_address, entry_port))
    connect_button = nepygui.Button(gradient=False, text="Connect", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda: com.connect(entry_address, entry_port))
    buttons_layout.add_widget(host_button)
    buttons_layout.add_widget(connect_button)

    exit_layout = nepygui.HLayout(w, orientation="C", y_start=150)
    exit_button = nepygui.Button(gradient=False, text="Quit", w=100, h=50, fontsize=18, bold=True, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=exit_this)
    exit_layout.add_widget(exit_button)

    game.init_game_grid()

    single_button_layout = nepygui.HLayout(w, orientation="C", y_start=-100)
    single_button = nepygui.Button(bold=True, fontsize=18, text="Single computer", w=200, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, gradient=False, func=game.switch_to_game)
    single_button_layout.add_widget(single_button)

    w.add_to_menu(labels_layout)
    w.add_to_menu(entries_layout)
    w.add_to_menu(buttons_layout)
    w.add_to_menu(exit_layout)
    w.add_to_menu(single_button_layout)
    w.main_loop()


# class Main:
#     def __init__(self, **kwargs):
#         self.screen_size = kwargs.get("size", (800, 600))
#         caption = kwargs.get("caption", "pygame window")
#         fullscreen = kwargs.get("fullscreen", 0)
#         resizable = kwargs.get("resizable", 0)
#
#         # window configuration
#
#         options = pygame.HWSURFACE | pygame.DOUBLEBUF
#         if fullscreen:
#             options |= pygame.FULLSCREEN
#         if resizable:
#             options |= pygame.RESIZABLE
#
#         self.screen = pygame.display.set_mode(self.screen_size, options)
#         pygame.display.set_caption(caption)
#         self.screen_color = (0, 0, 0)
#
#         self.clock = pygame.time.Clock()
#
#         # variables
#
#         self.delta_time = 0
#         self.last_frame_time = pygame.time.get_ticks()
#         self.multiplayer_option = ""
#         self.x_size, self.y_size = self.screen_size
#
#         # objects
#
#         self.fps = Fps()
#         self.game = TicTacToe(self.screen)
#
#         # game
#
#         self.current_count = self.count_fields(self.game.g)
#         self.current_mng = self.game.mng_pressed
#
#     def main_loop(self):
#         self.set_screen_color(*Color.Gray)
#
#         # menu loop
#         # ------------------------------------------------------------- #
#         while self.game.running:
#             self.events()
#             self.screen.fill(self.screen_color)
#
#             # scene
#             # -------------------------------#
#
#             mouse_button = pygame.mouse.get_pressed()
#             mouse_pos = pygame.mouse.get_pos()
#             keys = pygame.key.get_pressed()
#
#             self.game.draw_multiplayer_menu(
#                 self.screen, mouse_pos, mouse_button, keys, self.delta_time)
#             # -------------------------------#
#
#             # fps management
#             self.fps.fps()
#             self.fps.show_fps(self.screen)
#
#             pygame.display.flip()
#
#             # delta time calcualtions
#             current_frame_time = pygame.time.get_ticks()
#             self.delta_time = (current_frame_time -
#                                self.last_frame_time) / 1000.0
#             self.last_frame_time = current_frame_time
#
#             self.clock.tick(60)
#
#         # multiplayer loop
#         # ------------------------------------------------------------ #
#
#         if self.game.multiplayer_choice == "host":
#             address = self.game.address_entry.get_entry_value()
#             port = self.game.port_entry.get_entry_value()
#             asyncio.get_event_loop().run_until_complete(
#                 websockets.serve(self.hosted_game, address, port))
#             asyncio.get_event_loop().run_forever()
#         elif self.game.multiplayer_choice == "connect":
#             address = self.game.address_entry.get_entry_value()
#             port = self.game.port_entry.get_entry_value()
#             uri = "ws://" + address + ":" + port
#             asyncio.get_event_loop().run_until_complete(self.hello_host(uri))
#         else:
#             print("There's no such option.")
#
#         self.kill()
#
#     async def hosted_game(self, websocket, path):
#         rt = asyncio.ensure_future(self.recive(websocket))
#         st = asyncio.ensure_future(self.send(websocket))
#         await self.game_loop(websocket, "player_1")
#
#         done, pending = await asyncio.wait(
#             [rt, st],
#             return_when=asyncio.FIRST_COMPLETED,
#         )
#         for task in pending:
#             task.cancel()
#
#     async def hello_host(self, uri):
#         async with websockets.connect(uri) as websocket:
#             rt = asyncio.ensure_future(self.recive(websocket))
#             st = asyncio.ensure_future(self.send(websocket))
#             await self.game_loop(websocket, "player_2")
#
#             done, pending = await asyncio.wait(
#                 [rt, st],
#                 return_when=asyncio.FIRST_COMPLETED,
#             )
#             for task in pending:
#                 task.cancel()
#
#     async def game_loop(self, websocket, player):
#         print('starting game loop...')
#         while True:
#             self.events()
#
#             mouse_button = pygame.mouse.get_pressed()
#             mouse_pos = pygame.mouse.get_pos()
#             keys = pygame.key.get_pressed()
#
#             self.screen.fill(self.screen_color)
#
#             self.game.draw_grid(player, self.screen, mouse_pos,
#                                 mouse_button, keys, self.delta_time)
#             self.game.window_resize_callback(
#                 self.screen.get_size(), self.game.calc_grid)
#
#             # fps management
#             self.fps.fps()
#             self.fps.show_fps(self.screen)
#
#             pygame.display.flip()
#
#             # delta time calcualtions
#             current_frame_time = pygame.time.get_ticks()
#             self.delta_time = (current_frame_time -
#                                self.last_frame_time) / 1000.0
#             self.last_frame_time = current_frame_time
#
#             # self.clock.tick(60)
#             await asyncio.sleep(0.01)
#
#     async def recive(self, websocket):
#         print('starting rcv loop...')
#         while True:
#             msg = await websocket.recv()
#             msg = pickle.loads(msg)
#             self.game.g, self.game.turn, mng_pressed = msg
#             if mng_pressed:
#                 self.game.make_new_game()
#             self.game.mng_pressed = False
#
#             print("receive")
#             await asyncio.sleep(0.01)
#
#     async def send(self, websocket):
#         print('starting send loop...')
#         while True:
#             if self.current_count != self.count_fields(self.game.g) or self.current_mng != self.game.mng_pressed:
#                 data = [self.game.g, self.game.turn,
#                         self.game.mng_pressed]
#                 await websocket.send(pickle.dumps(data))
#                 print("send")
#                 self.current_count = self.count_fields(self.game.g)
#                 self.current_mng = self.game.mng_pressed
#                 self.game.mng_pressed = False
#             await asyncio.sleep(0.01)
#
#     def count_fields(self, L):
#         count = 0
#         for i in range(3):
#             for j in range(3):
#                 if L[i][j] == "":
#                     count += 1
#         return count
#
#     def events(self):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 self.game.running = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     self.game.running = False
#
#     def set_screen_color(self, r, g, b):
#         self.screen_color = (r, g, b)
#
#     @ staticmethod
#     def kill():
#         pygame.quit()
#         sys.exit()
#
#
# def main():
#     pygame.init()
#     info = pygame.display.Info()
#     SCREENSIZE = (info.current_w, info.current_h)
#     SCREENSIZE = (600, 600)
#     CAPTION = "TIC TAC TOE"
#     Main(size=SCREENSIZE, caption=CAPTION, resizable=True,
#          fullscreen=False).main_loop()


if __name__ == "__main__":
    main()
