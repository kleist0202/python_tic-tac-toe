import pygame
import sys
from python_tic_tac_toe.gui import Color
from python_tic_tac_toe.Fps import Fps
from python_tic_tac_toe.TicTacToe import TicTacToe

import asyncio
import websockets
import pickle


class Main:
    def __init__(self, **kwargs):
        self.screen_size = kwargs.get("size", (800, 600))
        caption = kwargs.get("caption", "pygame window")
        fullscreen = kwargs.get("fullscreen", 0)
        resizable = kwargs.get("resizable", 0)

        # window configuration

        options = pygame.HWSURFACE | pygame.DOUBLEBUF
        if fullscreen:
            options |= pygame.FULLSCREEN
        if resizable:
            options |= pygame.RESIZABLE

        self.screen = pygame.display.set_mode(self.screen_size, options)
        pygame.display.set_caption(caption)
        self.screen_color = (0, 0, 0)

        self.clock = pygame.time.Clock()

        # variables

        self.delta_time = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.multiplayer_option = ""
        self.x_size, self.y_size = self.screen_size

        # objects

        self.fps = Fps()
        self.game = TicTacToe(self.screen)

        # game

        self.current_count = self.count_fields(self.game.g)
        self.current_mng = self.game.mng_pressed

    def main_loop(self):
        self.set_screen_color(*Color.Gray)

        # menu loop
        # ------------------------------------------------------------- #
        while self.game.running:
            self.events()
            self.screen.fill(self.screen_color)

            # scene
            # -------------------------------#

            mouse_button = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            self.game.draw_multiplayer_menu(
                self.screen, mouse_pos, mouse_button, keys, self.delta_time)
            # -------------------------------#

            # fps management
            self.fps.fps()
            self.fps.show_fps(self.screen)

            pygame.display.flip()

            # delta time calcualtions
            current_frame_time = pygame.time.get_ticks()
            self.delta_time = (current_frame_time -
                               self.last_frame_time) / 1000.0
            self.last_frame_time = current_frame_time

            self.clock.tick(60)

        # multiplayer loop
        # ------------------------------------------------------------ #

        if self.game.multiplayer_choice == "host":
            address = self.game.address_entry.get_entry_value()
            port = self.game.port_entry.get_entry_value()
            asyncio.get_event_loop().run_until_complete(
                websockets.serve(self.hosted_game, address, port))
            asyncio.get_event_loop().run_forever()
        elif self.game.multiplayer_choice == "connect":
            address = self.game.address_entry.get_entry_value()
            port = self.game.port_entry.get_entry_value()
            uri = "ws://" + address + ":" + port
            asyncio.get_event_loop().run_until_complete(self.hello_host(uri))
        else:
            print("There's no such option.")

        self.kill()

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
        while True:
            self.events()

            mouse_button = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            self.screen.fill(self.screen_color)

            self.game.draw_grid(player, self.screen, mouse_pos,
                                mouse_button, keys, self.delta_time)
            self.game.window_resize_callback(
                self.screen.get_size(), self.game.calc_grid)

            # fps management
            self.fps.fps()
            self.fps.show_fps(self.screen)

            pygame.display.flip()

            # delta time calcualtions
            current_frame_time = pygame.time.get_ticks()
            self.delta_time = (current_frame_time -
                               self.last_frame_time) / 1000.0
            self.last_frame_time = current_frame_time

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

    def count_fields(self, L):
        count = 0
        for i in range(3):
            for j in range(3):
                if L[i][j] == "":
                    count += 1
        return count

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def set_screen_color(self, r, g, b):
        self.screen_color = (r, g, b)

    @ staticmethod
    def kill():
        pygame.quit()
        sys.exit()


def main():
    pygame.init()
    info = pygame.display.Info()
    SCREENSIZE = (info.current_w, info.current_h)
    SCREENSIZE = (600, 600)
    CAPTION = "TIC TAC TOE"
    Main(size=SCREENSIZE, caption=CAPTION, resizable=True,
         fullscreen=False).main_loop()


if __name__ == "__main__":
    main()
