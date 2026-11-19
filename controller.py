"""CONTROLLER: reads input, tells the model what to do, tells the view to redraw."""
import pygame
from model import GameModel
from view import View


class Controller:
    def __init__(self):
        self.model = GameModel()
        self.view = View()
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
        k = pygame.key.get_pressed()
        if k[pygame.K_UP]:
            self.model.move_player(-1)
        if k[pygame.K_DOWN]:
            self.model.move_player(1)
        if k[pygame.K_SPACE]:
            self.model.player_shoot(pygame.time.get_ticks())

    def run(self):
        while self.running:
            self.handle_input()          # user  -> controller
            self.model.update()          # controller -> model
            self.view.render(self.model) # model -> view
            self.clock.tick(60)
        pygame.quit()
