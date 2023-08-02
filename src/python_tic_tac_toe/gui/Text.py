import pygame


class Static_Text:
    def __init__(self, **kwargs):
        self.font_size = kwargs.get("fontsize", 12)
        self.color = kwargs.get("fontcolor", (0, 0, 0))
        self.static_text = kwargs.get("text", "")
        self.set_bold = kwargs.get("bold", False)

        self.text_font = pygame.font.SysFont(
            "dejavusansmono", self.font_size)
        self.width = 0
        self.height = 0
        self.static_text_objects(self.static_text, self.text_font, self.color)

    def static_text_objects(self, text, font, font_color):
        pygame.font.Font.set_bold(self.text_font, self.set_bold)
        text_surface = font.render(text, True, font_color)
        self.text_s, text_r = text_surface, text_surface.get_rect()
        self.width = text_r.w
        self.height = text_r.h

    def get_text_width(self):
        return self.width

    def get_text_height(self):
        return self.height

    def get_surface(self):
        return self.text_s

    def get_text(self):
        return self.static_text


class Dynamic_Text:
    def __init__(self, **kwargs):
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.font_size = kwargs.get("h", 20) // 3
        self.color = kwargs.get("font_color", (0, 0, 0))

        self.text_font = pygame.font.SysFont(
            "dejavusansmono", self.font_size)
        pygame.font.Font.set_bold(self.text_font, 0)
        test_surface = self.text_font.render("0", True, self.color)
        self.letter_size = test_surface.get_rect().w

    def dynamic_text_objects(self, text, font, font_color):
        text_surface = font.render(text, True, font_color)
        return text_surface, text_surface.get_rect()

    def recreate(self, **kwargs):
        self.x = kwargs.get("x", self.x)
        self.y = kwargs.get("y", self.y)

    def get_font_size(self):
        return self.font_size

    def get_letter_size(self):
        return self.letter_size

    def render_text(self, display, text, w, h):
        text_s, text_r = self.dynamic_text_objects(
            "".join(text), self.text_font, (0, 0, 0))
        text_r.center = (self.x + (w / 2), self.y + (h / 2))
        display.blit(text_s, text_r)
