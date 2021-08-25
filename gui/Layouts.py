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


class GridLayout(Layout):
    def __init__(self, screen, orientation="NW"):
        super().__init__(screen)
        self.orientation = orientation
        self.x_size, self.y_size = screen.get_size()
        self.keep_pos_info = []

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

    def add_widget(self, widget, row, col, xpadd=0, ypadd=0):
        self.widgets.append(widget)
        self.keep_pos_info.append((row, col, xpadd, ypadd))
        self.put(widget, row, col, xpadd, ypadd)

    @window_resize_callback
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
