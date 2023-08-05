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

        # init
        self.calc_grid()

    def calc_grid(self):
        self.x_size, self.y_size = self.window.get_screen().get_size()
        self.y_offset = self.offset

        if self.x_size < self.y_size:
            smaller_dim = self.x_size
            greater_dim = self.y_size

            self.grid_size = smaller_dim - 2*self.y_offset - self.grid_thickness
            self.x_offset = self.y_offset
            self.y_offset = (greater_dim - self.grid_size) / 2.0
        else:
            smaller_dim = self.y_size
            greater_dim = self.x_size

            self.grid_size = smaller_dim - 2*self.y_offset - self.grid_thickness
            self.x_offset = (greater_dim - self.grid_size) / 2.0

        self.square_size = self.grid_size / self.squares_num

    def window_resize_callback(self, screen_size, func):
        if self.x_size != screen_size[0]:
            self.x_size = screen_size[0]
            func()
        elif self.y_size != screen_size[1]:
            self.y_size = screen_size[1]
            func()

    def draw_grid(self, button):
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
            self.window.add_to_menu(f, "game")
        # vertical lines
        for i in range(4):
            f = nepygui.Frame(
                    fill=Color.Black,
                    x=int(self.x_offset+i*self.square_size-self.grid_thickness/2),
                    y=int(self.y_offset),
                    w=self.grid_thickness,
                    h=int(self.grid_size+self.grid_thickness),
                    gradient=False
            )
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
        self.info_left_layout = nepygui.VLayout(self.window, "NW")
        self.info_right_layout = nepygui.VLayout(self.window, "NE")

        self.win_screen = nepygui.TextFrame(
            y=self.y_size//2-50//2, w=self.x_size, anchor="C", fontsize=20, h=50, gradient=True)

        self.win_screen_layout = nepygui.HLayout(self.window, "C")
        self.win_screen_layout.add_widget(self.win_screen)

        self.info_player1 = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=True,
                                      text="Player 1", w=100, h=20)
        self.info_player2 = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=True,
                                      text="Player 2", w=100, h=20)

        self.info_player1_points = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=False,
                                             text="0", w=100, h=20)
        self.info_player2_points = nepygui.TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=False,
                                             text="0", w=100, h=20)

        # layouts
        self.info_left_layout.add_widget(self.info_player1)
        self.info_left_layout.add_widget(self.info_player1_points)
        self.info_right_layout.add_widget(self.info_player2)
        self.info_right_layout.add_widget(self.info_player2_points)

        self.window.add_to_menu(self.info_left_layout, "game")
        self.window.add_to_menu(self.info_right_layout, "game")
        self.window.add_to_menu(self.win_screen_layout, "game")

        self.window.switch_menus("game")
    
    def square_clicked(self, button):
        if self.player == "player_1":
            button.set_mark("X")
        elif self.player == "player_2":
            button.set_mark("O")
        else:
            raise Exception


class Clickable(nepygui.Button):
    def __init__(self, *, x, y, w, h, func) -> None:
        super().__init__(x=x, y=y, w=w, h=h, func=func)
        self.mark = ""

    def set_mark(self, mark):
        self.mark = mark

    def get_rect(self):
        return self.x, self.y, self.w, self.h

    def draw(self, display, mouse_pos, mouse_key, keys=0, delta_time=0, event_list=[]):
        nepygui.Button.draw(self, display, mouse_pos, mouse_key)
        self.draw_mark(display)

    def draw_mark(self, screen):
        if self.mark == "X":
            self.draw_X(screen, self.x, self.y, self.w, self.h, int(self.w/7))
        elif self.mark == "O":
            self.draw_O(screen, self.x, self.y, self.w, self.h, self.w/2.5)
        else:
            pass

    @staticmethod
    def draw_O(screen, x, y, w, h, r):
        pygame.draw.circle(screen, Color.Red, (x+w/2, y+h/2), r)
        pygame.draw.circle(screen, Color.Gray, (x+w/2, y+h/2), r/1.5)

    @ staticmethod
    def draw_X(screen, x, y, w, h, t):
        space = w/7
        pygame.draw.line(screen, Color.Blue, (x+space, y +
                         space), (x+w-space, y+h-space), t)
        pygame.draw.line(screen, Color.Blue, (x+space, y +
                         h-space), (x+w-space, y+space), t)

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


    labels_layout = nepygui.HLayout(w, orientation="C", y_start=-25)
    label1 = nepygui.Label(text="Address:", w=100, h=20, anchor="W")
    label2 = nepygui.Label(text="Port:", w=100, h=20, anchor="W")
    labels_layout.add_widget(label1, 150)
    labels_layout.add_widget(label2)

    entries_layout = nepygui.HLayout(w, orientation="C", y_start=10)
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

    single = nepygui.Button(text="Play single", w=200, h=200, func=game.draw_grid)

    w.add_to_menu(labels_layout)
    w.add_to_menu(entries_layout)
    w.add_to_menu(buttons_layout)
    w.add_to_menu(exit_layout)
    w.add_to_menu(single)
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
