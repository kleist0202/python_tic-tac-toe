from python_tic_tac_toe.Colors import Color
from python_tic_tac_toe.TicTacToe import Tic

import asyncio
import socket
import pickle
import nepygui
import argparse
import threading


class Player():
    def __init__(self, points, user_tag):
        self.points = points
        self.user_tag = user_tag

    def serialize(self):
        return {
            'points': self.points,
            'user_tag': self.user_tag,
        }

    def __repr__(self) -> str:
        return f"Player({self.points}, {self.user_tag})"

    @classmethod
    def deserialize(cls, data):
        points = data['points']
        user_tag = data['user_tag']
        player = cls(points, user_tag)
        return player


class Network:
    def __init__(self, user_tag, server, port, w):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server = socket.gethostbyname(socket.gethostname())
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.plr = None
        self.window = w
        self.connect(user_tag)

    def getP(self):
        return self.plr

    def connect(self, user_tag):
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps(user_tag))

            player_data = self.client.recv(2048)
            # print("Player data: ", player_data)
            self.plr = pickle.loads(player_data)
            # print("Player: ", self.plr)

            if user_tag == "player1":
                self.window.switch_menus("host")
            else:
                self.window.switch_menus("client")

            return self.plr
        except Exception as e:
            self.window.switch_menus("default")
            print("Error connecting to server", e)
            return

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data.serialize()))
            received_data = self.client.recv(2048)
            print("RECEIVED")
            print(pickle.loads(received_data))
            if not received_data:
                print("No data received from the server")
                return []
            return [
                Player.deserialize(p_data) for p_data in pickle.loads(received_data)
            ]
        except Exception as e:
            print(e)
            self.client.close()
            return []
        except socket.error as e:
            print(e)
            self.client.close()
            return []
        except EOFError:
            print("EOFError: Ran out of input")
            return []

    def close(self):
        self.client.close()
        self.window.switch_menus("default")


class ConnectionManager:
    def __init__(self):
        self.players = {}
        self._next_connection_id = 0

    def get_new_connection_id(self):
        conn_id = self._next_connection_id
        self._next_connection_id += 1
        return conn_id
    
    def get_all_players(self):
        return self.players
    
    def add_player(self, conn_id, player):
        self.players[conn_id] = player

    def remove_player(self, player: Player):
        current_player_name = player.user_tag
        for key, val in self.players.items():
            if current_player_name == val.user_tag:
                self.players.pop(key)
                break

    def get_player(self, player_name):
        player_gotten = None
        player_key = ""
        for key, val in self.players.items():
            if player_name == val.user_tag:
                player_gotten = val
                player_key = key
                break
        return player_key, player_gotten

    def get_all_players_except(self, curr_player):
        return [player for id, player in self.players.items() if player.user_tag != curr_player.user_tag]


class Server:
    def __init__(self):
        self.ip = ""
        self.port = 0
        self.plr_mgr = ConnectionManager()
        self.is_running = False
        self.client_do_close = False
        self.stop_request = asyncio.Event()
        self.start_request = asyncio.Event()
        self.server_thread = None

    def set_address_and_port(self, address, port):
        self.ip = address
        self.port = port

    def new_player(self, user_tag):
        player = Player(0, user_tag)
        return player

    async def wait_for_startup(self):
        await self.start_request.wait()

    async def handle_client(self, reader, writer):
        if len(self.plr_mgr.players.keys()) > 1:
            print("Only two players allowed!")
            writer.close()
            await writer.wait_closed()
            return
        user_tag = await reader.read(2048)
        user_tag = pickle.loads(user_tag)

        player = self.new_player(user_tag)
        print("NEW PLAYER:", player)
        # print("Player: ", player)
        id = self.plr_mgr.get_new_connection_id()
        self.plr_mgr.add_player(id, player)

        # player_data = player.serialize()
        # print("PLAYERDATA", player_data)
        writer.write(pickle.dumps(player))
        await writer.drain()

        # Get the client's address
        client_address = writer.get_extra_info('peername')
        print(f"Connected to: {client_address}")

        self.is_running = True
        try:
            while self.is_running:
                data = await reader.read(2048)
                # print("Data: ", data)
                if not data:
                    break

                data = pickle.loads(data)
                _, player = self.plr_mgr.get_player(data['user_tag'])
                player.points = data['points']
                # print("Player: ", player)
                other_players = self.plr_mgr.get_all_players_except(player)
                # print("Other players: ", other_players)
                other_players = [p.serialize() for p in other_players]
                # print("Sending other players data:", other_players)
                writer.write(pickle.dumps(other_players))
                # print("Received: ", data) 
                await writer.drain()

        except Exception as e:
            print(f"Exception occurred: {e}")

        writer.close()
        await writer.wait_closed()

        if player is not None and player.user_tag == "player1":
            self.plr_mgr.players.clear()
        else:
            self.plr_mgr.remove_player(player)
        # if not self.is_running:
        if not self.plr_mgr.players:
            self.stop_request.set()
            self.start_request.clear()
        # self.is_running = False

    async def start_server(self):
        self.start_request.clear()
        try:
            server = await asyncio.start_server(self.handle_client, self.ip, self.port)
        except Exception as e:
            print(e)
            self.start_request.set()
            await asyncio.sleep(1)
            return

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # async with server:
        #     await server.serve_forever()
        self.start_request.set()
        await self.stop_request.wait()
        self.stop_request.clear()
        server.close()
        print("waiting for server to close...")
        await server.wait_closed()
        print("server stopped yay!")

    def clean_up(self):
        self.plr_mgr.players.clear()


class GameClient:
    counter = 0

    def __init__(self, w):
        self.names = ["player1", "player2"]
        self.player_username = self.get_player_id()
        self.net: Network = None
        self.plr: Player = None
        self.window = w

    def connect_to_network(self, server, port):
        self.net = Network(self.player_username, server, port, self.window)
        self.plr = self.net.getP()

    def get_player_id(self):
        player_id = self.names[GameClient.counter % 2]
        GameClient.counter += 1
        return player_id

    def update_players(self):
        self.plr.points += 1
        other_players = self.net.send(self.plr)
        if other_players is None:
            other_players = []
        # self.plr.update(dt, other_players)
        return [self.plr] + other_players

    def change_results(self):
        players = self.update_players()
        print(players)


def run_server(loop, server):
    # asyncio.run(server.start_server)
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start_server())


def gui_action_connect(player2, entry_address, entry_port):
    server_name = entry_address.get_entry_value()
    port_val = entry_port.get_entry_value()
    if port_val.isdigit():
        port = int(port_val)
    else:
        return
    player2.connect_to_network(server_name, port)
    # w.switch_menus("client")


def gui_action_disconnect(w, player2):
    player2.net.close()


def gui_action_start_server(loop, server, player1, entry_address, entry_port):
    server_name = entry_address.get_entry_value()
    port_val = entry_port.get_entry_value()
    if port_val.isdigit():
        port = int(port_val)
    else:
        return
    server.set_address_and_port(server_name, port)
    server.server_thread = threading.Thread(target=run_server, args=(loop, server,))
    server.server_thread.start()

    asyncio.run_coroutine_threadsafe(server.wait_for_startup(), loop).result()

    player1.connect_to_network(server_name, port)


def gui_action_stop_server(w, loop, server, player1: Player):
    player1.net.close()
    # loop.call_soon_threadsafe(stop_server, server)
    server.server_thread.join()
    server.server_thread = None
    server.clean_up()
    w.switch_menus("default")


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

    # server_ip = socket.gethostbyname(socket.gethostname())
    server = Server()
    # client_instance = CLIENT(None)
    loop = asyncio.get_event_loop()

    player1 = GameClient(w)
    player2 = GameClient(w)

    # menu screen

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

    entry_address.set_entry_value("127.0.0.1")
    entry_port.set_entry_value(str(5555))

    def exit_this(_):
        w.exit()

    buttons_layout = nepygui.HLayout(w, orientation="C", y_start=70)
    host_button = nepygui.Button(gradient=False, text="Host", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: gui_action_start_server(loop, server, player1, entry_address, entry_port))
    connect_button = nepygui.Button(gradient=False, text="Connect", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: gui_action_connect(player2, entry_address, entry_port))
    
    buttons_layout.add_widget(host_button)
    buttons_layout.add_widget(connect_button)

    exit_layout = nepygui.HLayout(w, orientation="C", y_start=150)
    exit_button = nepygui.Button(gradient=False, text="Quit", w=100, h=50, fontsize=18, bold=True, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=exit_this)
    exit_layout.add_widget(exit_button)

    single_button_layout = nepygui.HLayout(w, orientation="C", y_start=-100)
    single_button = nepygui.Button(bold=True, fontsize=18, text="Single computer", w=200, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, gradient=False, func=game.switch_to_game)
    single_button_layout.add_widget(single_button)

    game.init_game_grid()

    w.add_to_menu(labels_layout)
    w.add_to_menu(entries_layout)
    w.add_to_menu(buttons_layout)
    w.add_to_menu(exit_layout)
    w.add_to_menu(single_button_layout)

    # server screen

    disconnect_server_button = nepygui.Button(w=300, h=50, text="Disconnect server", func=lambda btn: gui_action_stop_server(w, loop, server, player1))
    disconnect_client_button = nepygui.Button(w=300, h=50, text="Disconnect client", func=lambda btn: gui_action_disconnect(w, player2))
    disconnect_server_layout = nepygui.VLayout(w, orientation="C")
    disconnect_client_layout = nepygui.VLayout(w, orientation="C")
    disconnect_server_layout.add_widget(disconnect_server_button)
    disconnect_client_layout.add_widget(disconnect_client_button)
    server_send_message = nepygui.Button(w=200, h=50, text="Send message", func=lambda btn: player1.change_results())
    client_send_message = nepygui.Button(w=200, h=50, text="Send message", func=lambda btn: player2.change_results())
    disconnect_server_layout.add_widget(server_send_message)
    disconnect_client_layout.add_widget(client_send_message)

    w.add_to_menu(disconnect_server_layout, "host")
    w.add_to_menu(disconnect_client_layout, "client")

    # add them

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
