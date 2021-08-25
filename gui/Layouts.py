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
    def __init__(self, screen, orientation="NW"):
        super().__init__(screen)
        self.orientation = orientation
        self.x_size, self.y_size = screen.get_size()
        self.keep_pos_info = []

    def add_widget(self, widget, row, col, xpadd=0, ypadd=0):
        self.widgets.append(widget)
        self.keep_pos_info.append((row, col, xpadd, ypadd))
        self.put(widget, row, col, xpadd, ypadd)

    @Layout.window_resize_callback
    def draw(self, screen_size, mouse_pos, mouse_button, keys, delta_time):

        for widget in self.widgets:
            widget.draw(self.screen, mouse_pos, mouse_button, keys, delta_time)

    def put(self, widget, row, col, xpadd, ypadd):
        if len(self.widgets) == 1:
            current_index = 0
        else:
            current_index = len(self.widgets)-2
        w, h = self.widgets[current_index].get_size()

        if self.orientation == "C":
            widget.set_pos(self.x_size/2 - (w/2) + row*w+xpadd,
                           self.y_size/2 - (h/2) + col*h+ypadd)
        elif self.orientation == "E":
            widget.set_pos(self.x_size - w + row*w+xpadd,
                           self.y_size/2 - (h/2) + col*h+ypadd)
        elif self.orientation == "W":
            widget.set_pos(0 + row*w+xpadd,
                           self.y_size/2 - (h/2) + col*h+ypadd)
        elif self.orientation == "N":
            widget.set_pos(self.x_size/2 - (w/2) + row*w+xpadd,
                           0 + col*h+ypadd)
        elif self.orientation == "S":
            widget.set_pos(self.x_size/2 - (w/2) + row*w+xpadd,
                           self.y_size - h + col*h+ypadd)
        elif self.orientation in ["NE", "EN"]:
            widget.set_pos(self.x_size - w + row*w+xpadd,
                           0 + col*h+ypadd)
        elif self.orientation in ["SE", "ES"]:
            widget.set_pos(self.x_size - w + row*w+xpadd,
                           self.y_size - h + col*h+ypadd)
        elif self.orientation in ["WS", "SW"]:
            widget.set_pos(0 + row*w+xpadd,
                           self.y_size - h + col*h+ypadd)
        else:
            widget.set_pos(row*w+xpadd, col*h+ypadd)

    def resize(self):
        for keep_index, widget in enumerate(self.widgets):
            self.put(widget, *self.keep_pos_info[keep_index])

# --------------------------------------------------------------------- #
