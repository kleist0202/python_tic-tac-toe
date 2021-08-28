import pygame
from operator import attrgetter
from gui import Static_Text, Dynamic_Text
from gui import Color
from abc import ABC, abstractmethod


class Widget(ABC):
    """ Base class of all GUI objects """

    def __init__(self, **kwargs):
        # positions and dimensions
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.w = kwargs.get("w", 16)
        self.h = kwargs.get("h", 16)

    def recreate(self, **kwargs):
        self.x = kwargs.get("x", self.x)
        self.y = kwargs.get("y", self.y)
        self.w = kwargs.get("w", self.w)
        self.h = kwargs.get("h", self.h)

    def set_pos(self, x, y):
        self.recreate(x=x, y=y)

    def set_size(self, w, h):
        self.recreate(w=w, h=h)

    def get_pos(self):
        return (self.x, self.y)

    def get_size(self):
        return (self.w, self.h)

    @abstractmethod
    def draw(self):
        pass


class Frame(Widget):
    """ Basic object which can be drawn on screen"""

    def __init__(self, **kwargs):
        """
        Kwargs:
            **x (int): x position
            **y (int): y position
            **w (int): width
            **h (int): height
            **fill (tuple): background color of frame
            **border (bool): draw border or not
            **bordercolor (tuple): color of border, border argument must be True
            **hover (bool): draw when hovering over or not
            **hovercolor (tuple): color which appear when mouse is hovering over frame
            **gradient (bool): draw gradient or not
            **border_thickness (int): size of border
        """
        super().__init__(**kwargs)
        self.fill_color = kwargs.get("fill", Color.White)
        self.is_border = kwargs.get("border", False)
        self.border_color = kwargs.get("bordercolor", Color.Gray)
        self.is_hover = kwargs.get("hover", False)
        self.hover_color = kwargs.get("hovercolor", self.fill_color)
        self.is_gradient = kwargs.get("gradient", False)
        self.border_thickness = kwargs.get("borderthickness", 2)
        self.surf_init()

    def recreate(self, **kwargs):
        super().recreate(**kwargs)
        self.fill_color = kwargs.get("fill", self.fill_color)
        self.is_border = kwargs.get("border", self.is_border)
        self.border_color = kwargs.get("bordercolor", self.border_color)
        self.is_hover = kwargs.get("hover", self.is_hover)
        self.hover_color = kwargs.get("hovercolor", self.hover_color)
        self.is_gradient = kwargs.get("gradient", self.is_gradient)
        self.border_thickness = kwargs.get(
            "borderthickness", self.border_thickness)
        self.surf_init()

    def surf_init(self):
        self.fill_surface = ColorSurface(self.fill_color, self.w, self.h)
        self.hover_surface = ColorSurface(self.hover_color, self.w, self.h)
        self.temp_fill_surface = self.fill_surface
        begin_color = self.fill_color
        end_color = (self.fill_color[0]-60,
                     self.fill_color[1]-60, self.fill_color[1]-60)
        self.grad_surface = Gradient(begin_color, end_color, self.w, self.h)
        self.temp_grad_surface = self.grad_surface

    def draw(self, display, mouse_pos, mouse_button=0, keys=0, delta_time=0):
        if self.is_gradient:
            Special_Functions.border_rect(display, self.grad_surface.get_surface(),
                                          self.border_color, self.x, self.y, self.w, self.h, self.is_border, self.border_thickness)
        else:
            Special_Functions.border_rect(display, self.fill_surface.get_surface(),
                                          self.border_color, self.x, self.y, self.w, self.h, self.is_border, self.border_thickness)
        self.is_hovering(mouse_pos)

    def is_hovering(self, mouse_pos):
        if mouse_pos[0] > self.x and mouse_pos[1] > self.y and mouse_pos[0] < self.x + self.w and mouse_pos[1] < self.y + self.h:
            if self.is_hover:
                self.fill_surface = self.hover_surface
                self.grad_surface = self.hover_surface
            else:
                self.fill_surface = self.temp_fill_surface
                self.grad_surface = self.temp_grad_surface
        else:
            self.fill_surface = self.temp_fill_surface
            self.grad_surface = self.temp_grad_surface


class Label(Widget):
    """Creates label where you can display some text"""

    def __init__(self, **kwargs):
        """
        Kwargs:
            **x (int): x position
            **y (int): y position
            **w (int): width
            **h (int): height
            **text (str): text to display
            **anchor (str): set relative text position
            **fontcolor (tuple): changes font color
            **fontsize (int): set size of font
            **bold (bool): set text bold or not
        """
        super().__init__(**kwargs)

        # new settings
        self.text = kwargs.get("text", "")
        self.anchor = kwargs.get("anchor", "C")
        self.font_color = kwargs.get("fontcolor", (0, 0, 0))
        self.font_size = kwargs.get("fontsize", 12)
        self.set_bold = kwargs.get("bold", False)

        self.text_object = Static_Text(
            fontsize=self.font_size, bold=self.set_bold, text=self.text, fontcolor=self.font_color)

        self.text_padding = 4
        # FIXME: There is no vertical padding

    def draw(self, display, mouse_pos=0, mouse_key=0, keys=0, delta_time=0):
        vertical_center = self.y + self.h / 2 - self.text_object.get_text_height() / 2
        horizontal_center = self.x + self.w / 2 - self.text_object.get_text_width() / 2

        if self.anchor == "C":
            # center
            x_pos = horizontal_center
            y_pos = vertical_center
        elif self.anchor == "W":
            # left
            x_pos = self.x + self.text_padding
            y_pos = vertical_center
        elif self.anchor == "E":
            # right
            x_pos = self.x + self.w - self.text_object.get_text_width() - self.text_padding
            y_pos = vertical_center
        elif self.anchor == "N":
            # up
            x_pos = horizontal_center
            y_pos = self.y
        elif self.anchor == "S":
            # bottom
            x_pos = horizontal_center
            y_pos = self.y + self.h - self.text.get_text_height()
        elif self.anchor in ["NW", "WN"]:
            # up left
            x_pos = self.x + self.text_padding
            y_pos = self.y
        elif self.anchor in ["SW", "WS"]:
            # down left
            x_pos = self.x + self.text_padding
            y_pos = self.y + self.h - self.text_object.get_text_height()
        elif self.anchor in ["NE", "EN"]:
            # up right
            x_pos = self.x + self.w - self.text_object.get_text_width() - self.text_padding
            y_pos = self.y
        elif self.anchor in ["SE", "ES"]:
            # down right
            x_pos = self.x + self.w - self.text_object.get_text_width() - self.text_padding
            y_pos = self.y + self.h - self.text_object.get_text_height()
        else:
            x_pos = horizontal_center
            y_pos = vertical_center

        display.blit(self.text_object.get_surface(), (x_pos, y_pos))

    def set_padding(self, padd):
        self.text_padding = padd

    def get_padding(self):
        return self.text_padding

    def set_text(self, text):
        self.text = text
        self.text_object = Static_Text(
            h=self.h, text=text, fontsize=self.font_size, bold=self.set_bold, fontcolor=self.font_color)

    def set_color(self, color):
        self.font_color = color
        self.text_object = Static_Text(
            h=self.h, text=self.text, fontsize=self.font_size, bold=self.set_bold, fontcolor=color)

    def get_text(self):
        return self.text


class TextFrame(Frame, Label):
    """Creates frame with text to display"""

    def __init__(self, **kwargs):
        """
        Kwargs:
            **x (int): x position
            **y (int): y position
            **w (int): width
            **h (int): height
            **fill (tuple): background color of frame
            **border (bool): draw border or not
            **bordercolor (tuple): color of border, border argument must be True
            **hover (bool): draw when hovering over or not
            **hovercolor (tuple): color which appear when mouse is hovering over frame
            **gradient (bool): draw gradient or not
            **text (str): text to display
            **align (str): align text ("left", "center", "right")
            **fontcolor (tuple): changes font color
        """
        super().__init__(**kwargs)
        if self.w < self.text_object.get_text_width():
            self.w = self.text_object.get_text_width()
            Frame.recreate(self, w=self.w, h=self.h)
        Label.set_padding(self, Label.get_padding(self)
                          + self.border_thickness/2)

    def draw(self, display, mouse_pos, mouse_key=0, keys=0, delta_time=0):
        Frame.draw(self, display, mouse_pos)
        Label.draw(self, display)


class AbstractButton(Widget):
    """ Class which provides functionality common to buttons """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pressed = False
        self.function = kwargs.get("func", None)

    def is_clicked(self, mouse_pos, mouse_key):

        # we are checking if mouse position covers button dimensions
        if mouse_pos[0] > self.x and mouse_pos[1] > self.y and mouse_pos[0] < self.x + self.w and mouse_pos[1] < self.y + self.h:
            if not mouse_key[0]:
                if self.pressed:
                    if self.function == None:
                        pass
                    else:
                        self.function()

            # when mouse hover on the button, we can check if mouse button is pressed and trigger an event
            if mouse_key[0]:
                if not self.pressed:
                    self.pressed = True
                return True

        self.pressed = False
        return False


class Button(AbstractButton, TextFrame):
    """Class which allows you to draw fully functional button"""

    def __init__(self, **kwargs):
        """
        Kwargs:
            **x (int): x position
            **y (int): y position
            **w (int): width
            **h (int): height
            **fill (tuple): background color of button
            **border (bool): draw border or not
            **bordercolor (tuple): color of border, border argument must be True
            **hover (bool): change color when hovering over or not
            **hovercolor (tuple): color which appear when mouse is hovering over button
            **pressedcolor (tuple): color which appear when button is pressed
            **gradient (bool): draw gradient or not
            **func (function): function which will be executed when the button is pressed
        """
        super().__init__(**kwargs)

        # new settings
        self.color_pressed = kwargs.get("pressedcolor", Color.LightGray)
        self.color_surface_pressed = ColorSurface(
            self.color_pressed, self.w, self.h)

        # default settings
        self.is_gradient = kwargs.get("gradient", True)
        self.is_border = kwargs.get("border", True)

    def draw(self, display, mouse_pos, mouse_key, keys=0, delta_time=0):
        TextFrame.draw(self, display, mouse_pos)
        if(super().is_clicked(mouse_pos, mouse_key)):
            self.fill_surface = self.color_surface_pressed
            self.grad_surface = self.color_surface_pressed


class AbstractEntry(Widget):
    """Class which provides functionality of writing text"""
    signs = [None, None, None, None, "a", "b", "c", "d", "e", "f",
             "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
             "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2",
             "3", "4", "5", "6", "7", "8", "9", "0", None, None, None,
             None, " ", None, None, None, None, None, None, None, None,
             None, None, "."]
    delay = 0
    blit_delay = 0.5
    backspace_value = 42

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_value = ""
        self.dyn_text = Dynamic_Text(x=self.x, y=self.y, h=self.h)
        self.name = []
        self.marker_x = 0
        # set marker step for entry
        self.marker_step = self.dyn_text.get_letter_size()/2
        self.current_step = 0

    def writing(self, display, keys, delta_time):
        i = 0
        self.marker_x = self.x + self.w / 2 + self.current_step
        self.blitting_line(display, delta_time)
        if AbstractEntry.delay > 7 * delta_time:
            AbstractEntry.delay = 0
            for key in keys:
                if key and i == AbstractEntry.backspace_value and self.name:
                    self.name.pop()
                    self.current_step -= self.marker_step
                elif key and ((i >= 4 and i < 40) or i == 44 or i == 55):
                    # when there are too many letters don't allow to write
                    if self.marker_x + self.marker_step >= self.x + self.w:
                        return

                    self.name.append(AbstractEntry.signs[i])
                    self.current_step += self.marker_step
                    break
                i += 1
        AbstractEntry.delay += 1 * delta_time

    def blitting_line(self, display, delta_time):
        if AbstractEntry.blit_delay > 0.5:
            pygame.draw.line(display, Color.Black, (self.marker_x,
                             self.y + 4), (self.marker_x, self.y + self.h - 4))
            if AbstractEntry.blit_delay > 1:
                AbstractEntry.blit_delay = 0
        AbstractEntry.blit_delay += 1 * delta_time

    def clear_entry_value(self):
        self.entry_value = ""
        self.name.clear()
        self.marker_x = self.x + self.w / 2

    def set_entry_value(self, value):
        self.entry_value = ""
        self.name.clear()
        self.name = list(value)
        self.entry_value = value
        self.current_step = self.marker_step * len(self.name)

    def get_entry_value(self):
        return self.entry_value


class EntryWidget(AbstractEntry, AbstractButton, Frame):
    """Creates entry which allows you to write some text"""

    def __init__(self, **kwargs):
        """
        Kwargs:
            **x (int): x position
            **y (int): y position
            **w (int): width
            **h (int): height
            **fill (tuple): background color of entry
            **border (bool): draw border or not
            **bordercolor (tuple): color of border, border argument must be True
            **hover (bool): change color when hovering over or not
            **hovercolor (tuple): color which appear when mouse is hovering over entry
            **gradient (bool): draw gradient or not
            **activebordercolor (tuple): border color which appear when entry is active 
        """
        super().__init__(**kwargs)
        self.is_active = False
        self.prev_active_border_color = self.border_color

        # default settings
        self.is_border = kwargs.get("border", True)
        self.active_border_color = kwargs.get(
            "activebordercolor", Color.SkyBlue)

        # entrywidget as 'abstractbutton', needs function: here, activate entry
        self.function = self.activate

    def draw(self, display, mouse_pos, mouse_key, keys, delta_time):
        AbstractButton.is_clicked(self, mouse_pos, mouse_key)
        Frame.draw(self, display, mouse_pos)
        if self.is_active:
            self.border_color = self.active_border_color
            AbstractEntry.writing(self, display, keys, delta_time)
        else:
            self.border_color = self.prev_active_border_color
        self.entry_value = "".join(self.name)
        self.dyn_text.render_text(display, self.entry_value, self.w, self.h)

        # when we press mouse button outside entry, it deactivates itself
        if mouse_pos[0] < self.x or mouse_pos[0] > self.x + self.w or mouse_pos[1] < self.y or mouse_pos[1] > self.y + self.h:
            if mouse_key[0]:
                self.deactivate()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def recreate(self, **kwargs):
        Frame.recreate(self, **kwargs)
        self.dyn_text.recreate(**kwargs)


# --------------------------------------------------------------------- #


class Special_Functions:
    """Helpful functions which can help make code cleaner"""

    def __init__(self): pass

    @staticmethod
    def border_rect(display, color_surface, frame_color, x, y, w, h, draw_borders, border_thickness):
        """Function which allows you draw rectangle with borders"""
        display.blit(color_surface, (x, y))
        if draw_borders:
            pygame.draw.line(display, frame_color, (x, y),
                             (x + w, y), border_thickness)
            pygame.draw.line(display, frame_color,
                             (x, y + h), (x + w, y + h), border_thickness)
            pygame.draw.line(display, frame_color, (x, y),
                             (x, y + h), border_thickness)
            pygame.draw.line(display, frame_color,
                             (x + w, y), (x + w, y + h), border_thickness)


class ColorSurface:
    """Class which gives you rectangular surfaces of the selected color"""

    def __init__(self, color, w, h):
        self.clr_surface = pygame.Surface(
            (w, h), pygame.HWSURFACE)
        self.color_surface(color, w, h)

    def color_surface(self, color, w, h):
        pygame.draw.rect(self.clr_surface, color, (0, 0, w, h))

    def get_surface(self):
        return self.clr_surface


class Gradient:
    """Class which calculates surface with gradient"""

    def __init__(self, begin, end, w, h):
        self.gradient_surface = pygame.Surface((w, h), pygame.HWSURFACE)
        self.gradient(self.gradient_surface, begin, end, w, h)

    def gradient(self, surface, begin, end, w, h):
        r, g, b = begin[0], begin[1], begin[2]
        for layer in range(h):
            pygame.draw.line(surface,
                             (self.to_zero(r),
                              self.to_zero(g),
                              self.to_zero(b)),
                             (0, 0 + layer), (0 + w, 0 + layer), 1)
            if begin[0] < end[0]:
                if r > end[0]:
                    continue
                color_step = abs(end[0] - begin[0]) // h
                r += color_step
                g += color_step
                b += color_step
            elif begin[0] > end[0]:
                if r < end[0]:
                    continue
                color_step = abs(end[0] - begin[0]) // h
                r -= color_step
                g -= color_step
                b -= color_step
            else:
                pass

    def get_surface(self):
        return self.gradient_surface

    def to_zero(self, v):
        if v < 0:
            return 0
        else:
            return v
