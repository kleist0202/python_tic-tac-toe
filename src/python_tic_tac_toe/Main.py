from python_tic_tac_toe.Colors import Color
from python_tic_tac_toe.TicTacToe import Tic

import asyncio
import websockets
import pickle
import nepygui
import argparse
import threading


class SERVER:
    def __init__(self):
        self.stop_request = asyncio.Event()
        self.should_stop = False  # Flag to indicate whether the server should stop

    async def main_server(self):
        while not self.should_stop:
            print('starting the server')
            server = await asyncio.get_event_loop().create_server(EchoServerProtocol, '127.0.0.1', 8888)

            await self.stop_request.wait()
            self.stop_request.clear()
            print('stopping the server')
            server.close()
            await server.wait_closed()
            print("Closed")

    def stop_server(self):
        self.should_stop = True
        self.stop_request.set()


class CLIENT:
    def __init__(self, client_protocol):
        self.client_protocol = client_protocol

    def close_client(self):
        self.client_protocol.close_connection()


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.running = True

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print('\nData received from client: {!r}\n'.format(message))

    def close(self):
        print('Close the client socket')
        self.transport.close()

    def connection_lost(self, exc):
        print('The client closed the connection')

    def send_message(self, message):
        self.transport.write(message.encode())


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('\nData received from server: {!r}\n'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

    def close_connection(self):
        if self.transport:
            self.transport.close()


async def client_runner():
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = 'Client says hello!'

    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(message, on_con_lost),
        '127.0.0.1', 8888)

    return protocol  # Return the protocol, not the transport


async def async_input(prompt):
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(None, input, prompt)
    return user_input


async def user_input(client_instance):
    client_protocol = None
    client_protocol = await client_runner()
    client_instance.client_protocol = client_protocol
    while True:
        print("DEATh")


async def send_message(message, client_protocol):
    if client_protocol and client_protocol.transport:
        client_protocol.transport.write(message.encode())


def server_runner(loop, sss):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sss.main_server())


def start_server(btn, w, loop, server_instance: SERVER):
    w.switch_menus("host")
    server_instance.should_stop = False
    server_instance.stop_request.clear()
    # Start the server in a separate thread
    server_thread = threading.Thread(target=server_runner, args=(loop, server_instance,))
    server_thread.start()
    # stop_server(loop, server_instance)
    # Wait for the server thread to finish
    # server_thread.join()


def stop_server(w, sss):
    w.switch_menus("default")
    sss.should_stop = True  # Set the flag to indicate the server should stop
    sss.stop_request.set()


def start_client(btn, w, client_instance):
    w.switch_menus("client")
    asyncio.run(user_input(client_instance))


def stop_client(client_instance: CLIENT):
    client_instance.client_protocol.close_connection()
    client_instance.client_protocol = None

    
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

    server_instance = SERVER()
    client_instance = CLIENT(None)
    loop = asyncio.get_event_loop()

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

    entry_address.set_entry_value("localhost")
    entry_port.set_entry_value("8765")

    def exit_this(_):
        w.exit()

    buttons_layout = nepygui.HLayout(w, orientation="C", y_start=70)
    host_button = nepygui.Button(gradient=False, text="Host", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: start_server(btn, w, loop, server_instance))
    connect_button = nepygui.Button(gradient=False, text="Connect", fontsize=18, bold=True, w=175, h=50, fill=Color.DarkGray, borderthickness=2, bordercolor=Color.Black, func=lambda btn: start_client(btn, w, client_instance))
    
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

    disconnect_server_button = nepygui.Button(w=300, h=50, text="Disconnect server", func=lambda btn: loop.call_soon_threadsafe(stop_server, w, server_instance))
    disconnect_client_button = nepygui.Button(w=300, h=50, text="Disconnect client", func=lambda btn: stop_client(client_instance))
    disconnect_server_layout = nepygui.VLayout(w, orientation="C")
    disconnect_client_layout = nepygui.VLayout(w, orientation="C")
    disconnect_server_layout.add_widget(disconnect_server_button)
    disconnect_client_layout.add_widget(disconnect_client_button)
    server_send_message = nepygui.Button(w=200, h=50, text="Send message")
    client_send_message = nepygui.Button(w=200, h=50, text="Send message")
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
