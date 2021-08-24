import pygame

from gui import Color, rgb
from gui import Frame, TextFrame, EntryWidget, Button
from gui import GridLayout

import asyncio
import websockets


class TicTacToe:
    def __init__(self, screen):
        self.grid_thickness = 5
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

        # init
        self.x_size, self.y_size = screen.get_size()
        self.calc_grid()
        self.init(screen)
        # self.window_size_changed()

    def create_game(self, screen, mouse_pos, mouse_button, keys, is_running, delta_time):
        self.window_resize_callback(
            screen.get_size(), self.window_size_changed)
        self.is_running = is_running

        if self.choice == "menu":
            self.draw_menu(
                screen, mouse_pos, mouse_button)

        elif self.choice == "multiplayer":
            self.draw_multiplayer_menu(
                screen, mouse_pos, mouse_button, keys, delta_time)
        else:
            self.draw_grid(
                screen)

    def calc_grid(self):
        self.y_offset = self.offset

        if self.x_size < self.y_size:
            smaller_dim = self.x_size
            greater_dim = self.y_size

            self.grid_size = smaller_dim - 2*self.y_offset
            self.x_offset = self.y_offset
            self.y_offset = (greater_dim - self.grid_size) / 2.0
        else:
            smaller_dim = self.y_size
            greater_dim = self.x_size

            self.grid_size = smaller_dim - 2*self.y_offset
            self.x_offset = (greater_dim - self.grid_size) / 2.0

        self.square_size = self.grid_size / self.squares_num

    def init(self, screen):
        # place clickables
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                self.clickables.append(ClickableSqaure(self.x_offset+i*self.square_size, self.y_offset +
                                                       j*self.square_size, self.square_size, self.square_size))

        # info frames
        self.win_screen = TextFrame(
            y=self.y_size/2-50/2, w=self.x_size, anchor="C", fontsize=20, h=50, gradient=True)

        self.info__player1 = TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=True,
                                       text="Player 1", x=0, y=0, w=100, h=20)
        self.info__player2 = TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=True,
                                       text="Player 2", x=self.x_size-100, y=0, w=100, h=20)

        self.info__player1_points = TextFrame(fill=Color.Gray, fontcolor=Color.Blue, fontsize=14, bold=False,
                                              text="0", x=0, y=20, w=100, h=20)
        self.info__player2_points = TextFrame(fill=Color.Gray, fontcolor=Color.Red, fontsize=14, bold=False,
                                              text="0", x=self.x_size-100, y=20, w=100, h=20)
        # new game button
        self.new_game_button = Button(
            x=10, y=self.y_size-60, w=60, h=20, text="New game", bordercolor=Color.Black, gradient=False, fill=Color.DarkGray, func=self.make_new_game)

        # return to menu button
        self.return_to_menu_button = Button(
            x=self.x_size-110, y=self.y_size, w=100, h=20, text="Return to menu", bordercolor=Color.Black, gradient=False, fill=Color.DarkGray)

        # ----------- MENU ------------#

        # play button
        self.play_button = Button(
            x=self.x_size/2-200/2, y=self.y_size/2-120, w=200, h=60, text="Play", bordercolor=Color.Black, fontsize=20, gradient=False, fill=Color.DarkGray)

        # multiplayer button
        self.multiplayer_button = Button(
            x=self.x_size/2-200/2, y=self.y_size, w=200, h=60, text="Multiplayer", bordercolor=Color.Black, fontsize=20, gradient=False, fill=Color.DarkGray)

        # quit
        self.quit_button = Button(
            x=self.x_size/2-200/2, y=self.y_size/2+60/2, w=200, h=60, text="Quit", bordercolor=Color.Black, fontsize=20, gradient=False, fill=Color.DarkGray)

        # multiplayer : host game, join to game, return

        self.multiplayer_menu_layout = GridLayout(screen, "C")

        self.address_label = TextFrame(w=100, h=20,
                                       fill=Color.Red, fontsize=14, bold=False, text="Address:")

        self.port_label = TextFrame(w=100, h=20,
                                    fill=Color.Red, fontsize=14, bold=False, text="Port:")

        self.misja = TextFrame(w=200, h=20,
                               fill=Color.Blue, fontsize=14, bold=False, text="misja:")
        self.address_entry = EntryWidget(w=200, h=50)
        self.port_entry = EntryWidget(w=150, h=50)

        # default entry values
        self.address_entry.set_entry_value("localhost")
        self.port_entry.set_entry_value("8765")

        self.host_button = Button(
            x=self.x_size/2-160, y=self.y_size/2-50, w=150, h=50, text="Host", bordercolor=Color.Black, fontsize=20, gradient=False, fill=Color.DarkGray, func=self.host)
        self.connect_button = Button(
            x=self.x_size/2 + 10, y=self.y_size/2-50, w=150, h=50, text="Connect", bordercolor=Color.Black, fontsize=19, gradient=False, fill=Color.DarkGray, func=self.connect)

        self.multiplayer_menu_layout.add_widget(self.address_label, 0, 0)
        self.multiplayer_menu_layout.add_widget(self.port_label, 0, 1)
        self.multiplayer_menu_layout.add_widget(self.misja, 1, 0)
        self.multiplayer_menu_layout.add_widget(self.address_entry, 0, 2)

        self.multiplayer_menu_layout.add_widget(self.port_entry, 0, 3)

        self.whose_turn = TextFrame(fill=Color.Gray, fontcolor=Color.Black, fontsize=14, bold=True,
                                    text="---", x=self.x_size/2 - 50, y=20, w=100, h=20)

    def draw_grid(self, player, screen, mouse_pos, mouse_button):
        # FIXME: GRID DRAWING IS FINE ONLY FOR TIC-TAC-TOE 3x3

        # horizontal lines
        pygame.draw.line(screen, (Color.Black), (self.x_offset, self.y_offset),
                         (self.x_offset+self.grid_size, self.y_offset), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset, self.y_offset+self.square_size),
                         (self.x_offset+self.grid_size, self.y_offset+self.square_size), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset, self.y_offset+2*self.square_size),
                         (self.x_offset+self.grid_size, self.y_offset+2*self.square_size), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset, self.y_offset+3*self.square_size),
                         (self.x_offset+self.grid_size, self.y_offset+3*self.square_size), self.grid_thickness)

        # vertical lines
        pygame.draw.line(screen, (Color.Black), (self.x_offset, self.y_offset),
                         (self.x_offset, self.y_offset+self.grid_size), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset+self.square_size, self.y_offset),
                         (self.x_offset+self.square_size, self.y_offset+self.grid_size), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset+2*self.square_size, self.y_offset),
                         (self.x_offset+2*self.square_size, self.y_offset+self.grid_size), self.grid_thickness)
        pygame.draw.line(screen, (Color.Black), (self.x_offset+3*self.square_size, self.y_offset),
                         (self.x_offset+3*self.square_size, self.y_offset+self.grid_size), self.grid_thickness)

        # clickables
        if player == self.player:
            for i in range(self.squares_num):
                for j in range(self.squares_num):
                    current_index = i*3+j
                    current_clickable = self.clickables[current_index]

                    if current_clickable.is_clicked(screen, mouse_pos, mouse_button) and self.game_running:
                        if self.player == "player_1":
                            self.mark = "X"
                        elif self.player == "player_2":
                            self.mark = "O"
                        else:
                            raise Exception

                        self.g[i][j] = self.mark

                        self.turn += 1

        for i in range(self.squares_num):
            for j in range(self.squares_num):
                current_index = i*3+j
                current_clickable = self.clickables[current_index]
                current_clickable.set_mark(self.g[i][j])
                current_clickable.draw_mark(screen)
                current_clickable.resize(self.x_offset+i*self.square_size, self.y_offset +
                                         j*self.square_size, self.square_size, self.square_size)

        if self.turn % 2 == 0:
            self.player = "player_2"
        else:
            self.player = "player_1"

        # return to menu button
        # self.return_to_menu_button.draw(
        #    screen, mouse_pos, mouse_button, self.return_to_menu)

        # draw players info
        self.info__player1.draw(screen, mouse_pos)
        self.info__player2.draw(screen, mouse_pos)
        self.info__player1_points.draw(screen, mouse_pos)
        self.info__player2_points.draw(screen, mouse_pos)
        self.info__player1_points.set_text(str(self.player1_points))
        self.info__player2_points.set_text(str(self.player2_points))

        self.whose_turn.draw(screen, mouse_pos)
        if self.player == "player_1":
            self.whose_turn.set_text("<---")
            self.whose_turn.set_color(Color.Blue)
        elif self.player == "player_2":
            self.whose_turn.set_text("--->")
            self.whose_turn.set_color(Color.Red)
        else:
            raise Exception

        # check if game ends
        self.check_result(screen, mouse_pos, mouse_button)

    def check_result(self, screen, mouse_pos, mouse_button):
        if self.check_vertical(self.g, "X") or self.check_horizontal(self.g, "X") or self.check_diagonally(self.g, "X"):
            if self.game_running:
                self.player1_points += 1
                self.win_screen.set_text("Player 1 has won!")
                self.win_screen.set_color(Color.Blue)
            self.game_running = False
            self.win_screen.draw(screen, mouse_pos)
            self.new_game_button.draw(
                screen, mouse_pos, mouse_button)
        elif self.check_vertical(self.g, "O") or self.check_horizontal(self.g, "O") or self.check_diagonally(self.g, "O"):
            if self.game_running:
                self.player2_points += 1
                self.win_screen.set_text("Player 2 has won!")
                self.win_screen.set_color(Color.Red)
            self.game_running = False
            self.win_screen.draw(screen, mouse_pos)
            self.new_game_button.draw(
                screen, mouse_pos, mouse_button)
        elif self.draw_check():
            if self.game_running:
                self.win_screen.set_text("Draw")
                self.win_screen.set_color(Color.Black)
            self.game_running = False
            self.win_screen.draw(screen, mouse_pos)
            self.new_game_button.draw(
                screen, mouse_pos, mouse_button)
        else:
            pass

    def check_vertical(self, whole, mark):
        # FIXME: IT ONLY WORKS FOR TIC-TAC-TOE 3x3
        for row in whole:
            if all(x == mark for x in row):
                return True
        return False

    def check_horizontal(self, whole, mark):
        # FIXME: IT ONLY WORKS FOR TIC-TAC-TOE 3x3
        return all(elem[0] == mark for elem in whole) or \
            all(elem[1] == mark for elem in whole) or \
            all(elem[2] == mark for elem in whole)

    def check_diagonally(self, whole, mark):
        # FIXME: IT ONLY WORKS FOR TIC-TAC-TOE 3x3
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

    def draw_menu(self, screen, mouse_pos, mouse_button):
        self.play_button.draw(screen, mouse_pos, mouse_button)
        self.multiplayer_button.draw(
            screen, mouse_pos, mouse_button, self.multiplayer)
        self.quit_button.draw(screen, mouse_pos, mouse_button)

    def draw_multiplayer_menu(self, screen, mouse_pos, mouse_button, keys, delta_time):
        self.multiplayer_menu_layout.draw(
            screen.get_size(), mouse_pos, mouse_button, keys, delta_time)
        pass
        #self.address_label.draw(screen, mouse_pos)
        #self.port_label.draw(screen, mouse_pos)
        # self.address_entry.draw(
        #    screen, mouse_pos, mouse_button, keys, delta_time)
        # self.port_entry.draw(
        #    screen, mouse_pos, mouse_button, keys, delta_time)

        # self.host_button.draw(screen, mouse_pos,
        #                      mouse_button)
        # self.connect_button.draw(
        #    screen, mouse_pos, mouse_button)

    # ---------------- slots ---------------- #

    def make_new_game(self):
        self.mng_pressed = True
        self.game_running = True
        for i in range(self.squares_num):
            for j in range(self.squares_num):
                self.g[i][j] = ""
                self.clickables[i*3+j].set_mark("")

    def play(self):
        self.choice = "game"

    def multiplayer(self):
        self.choice = "multiplayer"

    def return_to_menu(self):
        self.choice = "menu"
        self.make_new_game()
        self.player1_points = 0
        self.player2_points = 0

    def host(self):
        self.running = False
        self.multiplayer_choice = "host"

    def connect(self):
        self.running = False
        self.multiplayer_choice = "connect"

    def back(self):
        self.multiplayer_choice = "menu"
        self.address_entry.clear_entry_value()
        self.port_entry.clear_entry_value()

    def quit(self):
        self.is_running.clear()


class ClickableSqaure:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.mark = ""

    def resize(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def is_clicked(self, screen, mouse_pos, mouse_button):
        if mouse_pos[0] > self.x and mouse_pos[0] < self.x+self.w \
                and mouse_pos[1] > self.y and mouse_pos[1] < self.y+self.h:
            if mouse_button[0] and self.mark == "":
                return True

        return False

    def set_mark(self, mark):
        self.mark = mark

    def get_rect(self):
        return self.x, self.y, self.w, self.h

    def draw_mark(self, screen):
        if self.mark == "X":
            X.draw(screen, self.x, self.y, self.w, self.h, int(self.w/7))
        elif self.mark == "O":
            O.draw(screen, self.x, self.y, self.w, self.h, self.w/2.5)
        else:
            pass


class O:
    """Simple static class which draws 'O' symbol """
    @ staticmethod
    def draw(screen, x, y, w, h, r):
        pygame.draw.circle(screen, Color.Red, (x+w/2, y+h/2), r)
        pygame.draw.circle(screen, Color.Gray, (x+w/2, y+h/2), r/1.5)


class X:
    """Simple static class which draws 'X' symbol """
    @ staticmethod
    def draw(screen, x, y, w, h, t):
        space = w/7
        pygame.draw.line(screen, Color.Blue, (x+space, y +
                         space), (x+w-space, y+h-space), t)
        pygame.draw.line(screen, Color.Blue, (x+space, y +
                         h-space), (x+w-space, y+space), t)
