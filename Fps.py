import time
import pygame


class Fps:
    def __init__(self):
        self.cSec, self.cFrame, self.FPS, self.delta = 0, 0, 0, 0
        self.fps_font = pygame.font.Font("/usr/share/fonts/noto/NotoSansMono-Black.ttf", 20)

    def fps(self):
        if self.cSec == time.strftime("%S"):
            self.cFrame += 1
        else:
            self.FPS = self.cFrame
            self.cFrame = 0
            self.cSec = time.strftime("%S")
            if self.FPS > 0:
                self.delta = 1 / self.FPS

    def show_fps(self, window):
        fps_overlay = self.fps_font.render(str(self.FPS), True, (255, 255, 0))
        window.blit(fps_overlay, (0, 0))
