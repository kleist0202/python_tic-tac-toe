# --------------------------------------------------------------------- #
# -----------------------------LAYOUTS--------------------------------- #
# --------------------------------------------------------------------- #

from abc import ABC, abstractmethod


class Layout(ABC):
    """A"""
    @abstractmethod
    def __init__(self, screen):
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
        self.widgets = [[]]
        self.keep_pos_info = []
        self.prev_row = 0
        self.prev_col = 0
        self.curr_x = 0
        self.curr_y = 0

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

    def add_2_2d(self, a, num, row, col):
        for r in range(0, row+1):
            if r >= len(a):
                a.append([])

        for i, r in enumerate(a):
            for c in range(0, col+1):
                if c >= len(a[i]):
                    a[i].append(0)

        a[row][col] = num

    def add_widget(self, widget, row, col, xpadd=0, ypadd=0):
        self.add_2_2d(self.widgets, widget, row, col)
        self.keep_pos_info.append((row, col, xpadd, ypadd))
        self.put(widget, row, col, xpadd, ypadd)

    @window_resize_callback
    def draw(self, screen_size, mouse_pos, mouse_button, keys, delta_time):

        for r in range(len(self.widgets)):
            for c in range(len(self.widgets[r])):
                curr_widget = self.widgets[r][c]
                if curr_widget == 0:
                    return
                curr_widget.draw(
                    self.screen, mouse_pos, mouse_button, keys, delta_time)

    def put(self, widget, row, col, xpadd, ypadd):
        #curr_row = len(self.widgets)-2
        #curr_col = len(self.widgets)-2
        calc_row = row - self.prev_row
        calc_col = col - self.prev_col

        curr_row = 0
        curr_col = 0

        if calc_row == 1:
            curr_row = row - 1
        elif calc_col == 1:
            curr_col = col - 1

        self.prev_row = row
        self.prev_col = col

        current_widget = self.widgets[row][col]
        chosen_widget = self.widgets[curr_row][curr_col]
        w, h = chosen_widget.get_size()
        curr_w, curr_h = current_widget.get_size()

        if self.orientation == "C":
            self.curr_x = self.x_size/2 - curr_w/2
            self.curr_y = self.y_size/2 - curr_h/2
            self.orientation = ""
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

        self.curr_x += w*calc_row+xpadd
        self.curr_y += h*calc_col+ypadd

        widget.set_pos(self.curr_x,
                       self.curr_y)

    def resize(self):
        for r in range(len(self.widgets)):
            for c in range(len(self.widgets[r])):
                curr_widget = self.widgets[r][c]
                if curr_widget == 0:
                    return
                self.orientation = "C"
                self.put(curr_widget,
                         *self.keep_pos_info[r*len(self.widgets)+c])

# --------------------------------------------------------------------- #
