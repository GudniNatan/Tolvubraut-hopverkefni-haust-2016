import pygame
from Constants import *
from pygame.locals import *


class Brick(object):
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)


class Box(object):
    def __init__(self, rect):
        self.rect = rect


class Block(pygame.sprite.Sprite): # Simple block
    def __init__(self, rect, color, image=None):
        super(Block, self).__init__()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill(color)
        if image is not None:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft
        self.image = pygame.transform.scale(self.image, (self.rect.w, self.rect.h))

class TeleBlock(pygame.sprite.Sprite): # Simple block
    def __init__(self, rect, color, image=None):
        super(TeleBlock, self).__init__()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill(color)
        if image is not None:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft
        self.image = pygame.transform.scale(self.image, (self.rect.w, self.rect.h))



class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self, top_left_point, surface):
        super(SimpleSprite, self).__init__()
        self.image = surface
        self.rect = surface.get_rect()
        self.rect.topleft = top_left_point

class Animation(object):
    def __init__(self, name, params=dict()):
        self.name = name
        self.params = params
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __eq__(self, other):
        return self.name == other.name


class Grid(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = []

    def make_grid(self):
        grid_size = self.grid_size
        grid = [[0 for i in range((grid_size[1] * 2) + 1)] for j in range((grid_size[0] * 2) + 1)]
        self.grid = grid

    def update_grid(self, collidables, draw_size=drawSize, resolution=1):
        self.make_grid()
        grid = self.grid
        for obj in collidables:
            # Faster, but less reliable
            if resolution <= 1:
                for x in xrange(obj.rect.left / draw_size, obj.rect.right / draw_size):
                    for y in xrange(obj.rect.top / draw_size, obj.rect.bottom / draw_size):
                        if 0 < x <= self.grid_size[0] * 2 and 0 < y <= self.grid_size[1] * 2:
                            grid[x][y] = 1
            # Slower, but more reliable
            else:
                for x in xrange(resolution * obj.rect.left / draw_size, resolution * obj.rect.right / draw_size):
                    for y in xrange(resolution * obj.rect.top / draw_size, resolution * obj.rect.bottom / draw_size):
                        x2 = int(x / (resolution * 1.0))
                        y2 = int(y / (resolution * 1.0))
                        if 0 <= x2 <= self.grid_size[0] * 2 and 0 <= y2 <= self.grid_size[1] * 2:
                            grid[x2][y2] = 1
        self.grid = grid
