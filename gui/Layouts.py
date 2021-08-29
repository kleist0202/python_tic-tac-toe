# --------------------------------------------------------------------- #
# -----------------------------LAYOUTS--------------------------------- #
# --------------------------------------------------------------------- #

from abc import ABC, abstractmethod


class Layout(ABC):
    """A"""
    @abstractmethod
    def __init__(self, screen):
        self.widgets = []
        self.screen = screen

    @abstractmethod
    def add_widget(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def window_resize_callback(func):
        def inner(self, screen_size, mouse_pos, mouse_button, keys, delta_time):
            x_size, y_size = screen_size
            if self.x_size != x_size:
                self.x_size = x_size
                self.resize()
            elif self.y_size != y_size:
                self.y_size = y_size
                self.resize()
            func(self, screen_size, mouse_pos, mouse_button, keys, delta_time)
        return inner


class VLayout(Layout):
    """ Layout that allows you to arrange the widgets one after another vertically"""

    def __init__(self, screen, orientation="NW", x_start=0, y_start=0):
        super().__init__(screen)
        self.orientation = orientation
        self.x_start = x_start
        self.y_start = y_start
        self.x_size, self.y_size = screen.get_size()
        self.keep_padd_info = []
        self.curr_x = 0
        self.curr_y = 0

    def add_widget(self, widget, ypadd=0):
        self.widgets.append(widget)
        self.keep_padd_info.append(ypadd)
        self.put(widget, ypadd)

    @Layout.window_resize_callback
    def draw(self, screen_size, mouse_pos, mouse_button, keys, delta_time):

        for widget in self.widgets:
            widget.draw(self.screen, mouse_pos, mouse_button, keys, delta_time)

    def put(self, widget, ypadd):
        # jesus... this code is too complicated and probably bloated
        # at least it works
        for i, widget in enumerate(self.widgets):
            curr_w, curr_h = widget.get_size()

            # bloated
            if self.orientation == "C":
                if i == 0:
                    self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_y -= self.keep_padd_info[j]/2

                self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no need to bloat
            elif self.orientation == "N":
                if i == 0:
                    self.curr_y = self.y_start
                self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "S":
                if i == 0:
                    self.curr_y = self.y_size - curr_h + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2 + self.keep_padd_info[j]
                        else:
                            self.curr_y -= self.keep_padd_info[j]
                self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "W":
                if i == 0:
                    self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_y -= self.keep_padd_info[j]/2
                self.curr_x = self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "E":
                if i == 0:
                    self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_y -= self.keep_padd_info[j]/2
                self.curr_x = self.x_size - curr_w + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no need to bloat
            elif self.orientation in ["EN", "NE"]:
                if i == 0:
                    self.curr_y = self.y_start
                self.curr_x = self.x_size - curr_w + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no need to bloat
            elif self.orientation in ["NW", "WN"]:
                if i == 0:
                    self.curr_y = self.y_start
                self.curr_x = self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation in ["SW", "WS"]:
                if i == 0:
                    self.curr_y = self.y_size - curr_h + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2 + self.keep_padd_info[j]
                        else:
                            self.curr_y -= self.keep_padd_info[j]
                self.curr_x = self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation in ["SE", "ES"]:
                if i == 0:
                    self.curr_y = self.y_size - curr_h + self.y_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_y -= curr_h2 + self.keep_padd_info[j]
                        else:
                            self.curr_y -= self.keep_padd_info[j]

                self.curr_x = self.x_size - curr_w + self.x_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            self.curr_y += curr_h + self.keep_padd_info[i]

    def resize(self):
        for keep_index, widget in enumerate(self.widgets):
            self.put(widget, self.keep_padd_info[keep_index])


class HLayout(Layout):
    """ Layout that allows you to arrange the widgets one after another horizontally"""

    def __init__(self, screen, orientation="NW", x_start=0, y_start=0):
        super().__init__(screen)
        self.orientation = orientation
        self.x_start = x_start
        self.y_start = y_start
        self.x_size, self.y_size = screen.get_size()
        self.keep_padd_info = []
        self.curr_x = 0
        self.curr_y = 0

    def add_widget(self, widget, xpadd=0):
        self.widgets.append(widget)
        self.keep_padd_info.append(xpadd)
        self.put(widget, xpadd)

    @Layout.window_resize_callback
    def draw(self, screen_size, mouse_pos, mouse_button, keys, delta_time):

        for widget in self.widgets:
            widget.draw(self.screen, mouse_pos, mouse_button, keys, delta_time)

    def put(self, widget, xpadd):
        for i, widget in enumerate(self.widgets):
            curr_w, curr_h = widget.get_size()

            # bloated
            if self.orientation == "C":
                if i == 0:
                    self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_x -= self.keep_padd_info[j]/2
                self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no need to bloat
            elif self.orientation == "W":
                if i == 0:
                    self.curr_x = self.x_start
                self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "E":
                if i == 0:
                    self.curr_x = self.x_size - curr_w + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2 + self.keep_padd_info[j]
                        else:
                            self.curr_x -= self.keep_padd_info[j]
                self.curr_y = self.y_size/2 - curr_h/2 + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "N":
                if i == 0:
                    self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_x -= self.keep_padd_info[j]/2
                self.curr_y = self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation == "S":
                if i == 0:
                    self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2/2 + self.keep_padd_info[j]/2
                        else:
                            self.curr_x -= self.keep_padd_info[j]/2
                self.curr_y = self.y_size - curr_h + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no need to bloat
            elif self.orientation in ["SW", "WS"]:
                if i == 0:
                    self.curr_x = self.x_start
                self.curr_y = self.y_size - curr_h + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # no nedd to bloat
            elif self.orientation in ["NW", "WN"]:
                if i == 0:
                    self.curr_x = self.x_start
                self.curr_y = self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            # bloated
            elif self.orientation in ["EN", "NE"]:
                if i == 0:
                    self.curr_x = self.x_size - curr_w + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2 + self.keep_padd_info[j]
                        else:
                            self.curr_x -= self.keep_padd_info[j]
                self.curr_y = self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            elif self.orientation in ["SE", "ES"]:
                if i == 0:
                    self.curr_x = self.x_size - curr_w + self.x_start
                    for j, curr_widget in enumerate(self.widgets):
                        curr_w2, curr_h2 = curr_widget.get_size()
                        if j != 0:
                            self.curr_x -= curr_w2 + self.keep_padd_info[j]
                        else:
                            self.curr_x -= self.keep_padd_info[j]
                self.curr_y = self.y_size - curr_h + self.y_start
                widget.set_pos(self.curr_x,
                               self.curr_y)

            self.curr_x += curr_w + self.keep_padd_info[i]

    def resize(self):
        for keep_index, widget in enumerate(self.widgets):
            self.put(widget, self.keep_padd_info[keep_index])


class GridLayout(Layout):
    def __init__(self, screen, orientation="NW", x_start=0, y_start=0):
        super().__init__(screen)
        self.orientation = orientation
        self.x_start = x_start
        self.y_start = y_start
        self.widgets = []
        self.x_size, self.y_size = screen.get_size()
        self.keep_padd_info = []
        self.curr_x = 0
        self.curr_y = 0
        self.curr_r = 0
        self.curr_c = 0

    def add_widget(self, widget, row, col, xpadd=0, ypadd=0):
        if row == 0 and col == 0:
            self.widgets.append(["0", widget])
        else:
            self.widgets.append([self.v_or_h(row, col), widget])
        self.keep_padd_info.append((xpadd, ypadd))
        self.put(widget, row, col, xpadd, ypadd)

    @ Layout.window_resize_callback
    def draw(self, screen_size, mouse_pos, mouse_button, keys, delta_time):

        for widget in self.widgets:
            widget[1].draw(self.screen, mouse_pos,
                           mouse_button, keys, delta_time)

    def put(self, widget, row, col, xpadd, ypadd):
        for widget_l in self.widgets:
            curr_w, curr_h = widget_l[1].get_size()

            # bloated
            if self.orientation == "C":
                if widget_l[0] == "0":
                    self.curr_x = self.x_size/2 - curr_w/2 + self.x_start
                    self.curr_y = self.y_size/2 - curr_h/2 + self.y_start

                if widget_l[0] == "v":
                    self.curr_y += curr_h  # + self.keep_padd_info[i]
                elif widget_l[0] == "h":
                    self.curr_x += curr_w  # + self.keep_padd_info[i]
                widget.set_pos(self.curr_x, self.curr_y)

    def v_or_h(self, r, c):
        rr = r - self.curr_r
        cc = c - self.curr_c
        print(rr, cc)

        self.curr_r = r
        self.curr_c = c
        if rr >= 1 and cc <= 0:
            return "h"
        elif cc >= 1 and rr <= 0:
            return "v"
        else:
            raise ValueError("YOU CAN'T PLACE IT LIKE THAT.")

    def resize(self):
        pass

# --------------------------------------------------------------------- #
