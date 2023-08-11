from python_tic_tac_toe.Colors import Color
from python_tic_tac_toe.TicTacToe import TicTacToe

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
        self.turn = "player_1"
        self.changed = False

    def serialize(self):
        return {
            'points': self.points,
            'user_tag': self.user_tag,
            'turn': self.turn,
            'changed': self.changed,
        }

    def __repr__(self) -> str:
        return f"Player({self.points=}, {self.user_tag=}, {self.turn=}, {self.changed=})"

    def update(self):
        pass

    @classmethod
    def deserialize(cls, data):
        points = data['points']
        user_tag = data['user_tag']
        turn = data['turn']
        changed = data['changed']
        player = cls(points, user_tag)
        player.turn = turn
        player.changed = changed
        return player


class Network:
    def __init__(self, user_tag, server, port, w):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(2)
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
            self.plr = pickle.loads(player_data)

            self.window.switch_menus("game")

            return self.plr
        except Exception as e:
            self.window.switch_menus("default")
            print("Error connecting to server", e)
            return

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data.serialize()))
            try:
                received_data = self.client.recv(2048)
            except Exception as e:
                print(e)
            if not received_data:
                print("No data received from the server")
                return []
            return [
                Player.deserialize(p_data) for p_data in pickle.loads(received_data)
            ]
        except socket.error as e:
            print("WAT SOCKET ERROR")
            print(e)
            self.close()
            return []
        except EOFError:
            print("EOFError: Ran out of input")
            return []
        except Exception as e:
            print("WAT SOME OTHER EXCEPTION")
            print(e)
            self.client.close()
            return []

    def close(self):
        self.client.close()
        self.window.background_function = lambda: None
        self.window.switch_menus("default")


class ConnectionManager:
    def __init__(self):
        self.players = {}
        self._next_connection_id = 0

    def get_new_connection_id(self):
        conn_id = self._next_connection_id
        self._next_connection_id += 1
        return conn_id
    
    def add_player(self, conn_id, player):
        self.players[conn_id] = player

    def remove_player(self, player: Player):
        current_player_name = player.user_tag
        for key, val in self.players.items():
            if current_player_name == val.user_tag:
                self.players.pop(key)
                break

    def get_player(self, player_name):
        for key, player in self.players.items():
            if player_name == player.user_tag:
                return key, player
        return "", None

    def get_all_players_except(self, curr_player):
        return [player for id, player in self.players.items() if player.user_tag != curr_player.user_tag]

    def get_all_players(self):
        return [player for id, player in self.players.items()]


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
        id = self.plr_mgr.get_new_connection_id()
        self.plr_mgr.add_player(id, player)

        writer.write(pickle.dumps(player))
        await writer.drain()

        # Get the client's address
        client_address = writer.get_extra_info('peername')
        print(f"Connected to: {client_address}")

        self.is_running = True
        try:
            while self.is_running:
                data = await reader.read(2048)
                if not data:
                    break

                data = pickle.loads(data)
                # _, player = self.plr_mgr.get_player(data['user_tag'])
                # player.points = data['points']
                # player.turn = data['turn']
                players = self.plr_mgr.get_all_players()
                if data["changed"]:
                    if players:
                        for other in players:
                            other.changed = False
                            if other.turn == "player_1":
                                other.turn = "player_2"
                            elif other.turn == "player_2":
                                other.turn = "player_1"
                players = [p.serialize() for p in players]
                writer.write(pickle.dumps(players))
                await writer.drain()

        except Exception as e:
            print(f"Exception occurred: {e}")

        writer.close()
        await writer.wait_closed()

        if player is not None and player.user_tag == "player_1":
            self.plr_mgr.players.clear()
        else:
            self.plr_mgr.remove_player(player)
        if not self.plr_mgr.players:
            self.stop_request.set()
            self.start_request.clear()

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
        await server.wait_closed()
        print("server stopped yay!")

    def clean_up(self):
        self.plr_mgr.players.clear()


class GameClient:
    def __init__(self, w, game):
        self.player_username = ""
        self.net: Network = None
        self.plr: Player = None
        self.window = w
        self.game = game

    def connect_to_network(self, player_name, server_address, port, server):
        self.player_username = player_name
        self.net = Network(player_name, server_address, port, self.window)
        self.plr = self.net.getP()
        self.window.background_function = self.runner

        for clickable in self.game.clickables:
            clickable.function = lambda btn: self.action()

        if self.player_username == "player_1":
            self.game.return_to_menu_button.function = lambda btn: self.gui_action_stop_server(server)
        elif self.player_username == "player_2":
            self.game.return_to_menu_button.function = lambda btn: self.gui_action_disconnect()

    def update_players(self):
        if self.net is None or self.plr is None:
            return
        other_players = self.net.send(self.plr)
        if other_players is None:
            other_players = []
        return other_players

    def runner(self):
        players = self.update_players()
        if players:
            self.game.player = players[0].turn
        if self.plr is not None:
            self.plr.changed = False
        self.game.set_turn()
    
    def action(self):
        self.game.square_clicked_multiplayer()
        self.plr.changed = True

    def gui_action_stop_server(self, server):
        self.net.close()
        # loop.call_soon_threadsafe(stop_server, server)
        server.server_thread.join()
        server.server_thread = None
        server.clean_up()
        self.window.switch_menus("default")

    def gui_action_disconnect(self):
        self.net.close()


def run_server(loop, server):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start_server())


def gui_action_connect(game_client, entry_address, entry_port, server):
    server_name = entry_address.get_entry_value()
    port_val = entry_port.get_entry_value()
    if port_val.isdigit():
        port = int(port_val)
    else:
        return
    game_client.connect_to_network("player_2", server_name, port, server)


def gui_action_start_server(loop, server, game_client, entry_address, entry_port):
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

    game_client.connect_to_network("player_1",server_name, port, server)


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
    game = TicTacToe(w)

    game.init_game_grid()

    # server_ip = socket.gethostbyname(socket.gethostname())
    server = Server()
    loop = asyncio.get_event_loop()
    game_client = GameClient(w, game)

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

    buttons_layout = nepygui.HLayout(w, orientation="C", y_start=70)
    host_button = nepygui.Button(gradient=False, text="Host", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: gui_action_start_server(loop, server, game_client, entry_address, entry_port))
    connect_button = nepygui.Button(gradient=False, text="Connect", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: gui_action_connect(game_client, entry_address, entry_port, server))
    
    buttons_layout.add_widget(host_button)
    buttons_layout.add_widget(connect_button)

    exit_layout = nepygui.HLayout(w, orientation="C", y_start=150)
    exit_button = nepygui.Button(gradient=False, text="Quit", w=100, h=50, fontsize=18, bold=True, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: w.exit())
    exit_layout.add_widget(exit_button)

    single_button_layout = nepygui.HLayout(w, orientation="C", y_start=-100)
    single_button = nepygui.Button(bold=True, fontsize=18, text="Single computer", w=200, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, gradient=False, func=game.switch_to_game)
    single_button_layout.add_widget(single_button)

    w.add_to_menu(labels_layout)
    w.add_to_menu(entries_layout)
    w.add_to_menu(buttons_layout)
    w.add_to_menu(exit_layout)
    w.add_to_menu(single_button_layout)

    w.main_loop()


if __name__ == "__main__":
    main()
