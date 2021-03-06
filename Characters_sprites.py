import pygame
from pygame.locals import *
from pathfinderAStar import AStar
from Constants import *
from Objects import *
from Methods import *


class Character(pygame.sprite.Sprite):
    def __init__(self, rect, charset=0, sprite_size_rect=0):
        super(Character, self).__init__()
        self.collision_rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.collision_rect.x
        self.realY = self.collision_rect.y
        self.original_x = self.realX
        self.original_y = self.realY
        self.startPoint = [self.collision_rect.x, self.collision_rect.y]
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.baseSpeed = 0.08
        self.health = 3
        self.charset = charset
        self.sprite_size_rect = sprite_size_rect
        self.image = pygame.Surface((0, 0))
        self.direction = 180
        self.last_direction = None
        self.set_sprite_direction()
        self.rect = self.image.get_rect()
        self.rect.midbottom = rect.midbottom
        self.collision_rect.w = 20
        self.walking_phase = 1
        self.moving = False

    def set_sprite_direction(self):
        vx = self.vx
        vy = self.vy
        if vx == 0 and vy == 0 and self.last_direction is not None:
            self.moving = False
            self.walking_phase = 1
            return
        direction = 180
        if vx and vy:
            if vy < 0 and vx < 0:
                direction = 315
            if vy < 0 and vx > 0:
                direction = 45
            if vy > 0 and vx < 0:
                direction = 225
            if vy > 0 and vx > 0:
                direction = 135
        else:
            if vx > 0:
                direction = 90
            if vx < 0:
                direction = 270
            if vy > 0:
                direction = 180
            if vy < 0:
                direction = 0
        if vx == 0 and vy == 0:
            self.moving = False
            self.walking_phase = 1
        else:
            self.moving = True
        if direction == self.last_direction:
            return
        self.direction = direction
        self.last_direction = direction
        self.update_sprite()

    def update_sprite(self):
        sprite = 0
        if self.charset == 0:
            self.image = Block(self.collision_rect, ORANGE).image
            return
        direction = self.direction
        (width, height, desired_width) = self.sprite_size_rect
        phase = int(self.walking_phase)

        if 45 > (direction % 360) or (direction % 360) >= 315:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 0, width-1, height))
        elif 45 <= (direction % 360) < 135:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 1, width-1, height))
        elif 135 <= (direction % 360) < 225:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 2, width-1, height))
        elif 225 <= (direction % 360) < 315:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 3, width-1, height))
        #sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * 24 / height, sprite.get_rect().h * 24 / height)
        sprite = aspect_scale(sprite, (desired_width, 100))
        self.image = sprite

    def update_speed(self):
        pass

    def update_position(self, time, collidables):
        if time == 0:
            pygame.time.wait(1)
            time = 1
        original_x = self.realX
        original_y = self.realY
        self.original_x = original_x
        self.original_y = original_y
        pixellimit = 6 # should not ever be higher than drawsize / 2
        if -pixellimit < self.vx * time < pixellimit:
            self.realX += self.vx * time
        elif self.vx < 0:
            self.realX -= pixellimit
        else:
            self.realX += pixellimit
        if -pixellimit < self.vy * time < pixellimit:
            self.realY += self.vy * time
        elif self.vy < 0:
            self.realY -= pixellimit
        else:
            self.realY += pixellimit
        rect = self.collision_rect
        next_location = pygame.Rect(int(self.realX), int(self.realY), rect.w, rect.h)
        collision = False

        for object in collidables:
            if object == self.collision_rect:
                continue
            if (max(rect.center[0], object.rect.center[0]) - min(rect.center[0], object.rect.center[0]) > max(rect.w, object.rect.w) * 2 or
                    max(rect.center[1], object.rect.center[1]) - min(rect.center[1], object.rect.center[1]) > max(rect.h, object.rect.h) * 2):
                continue
            if object.rect.colliderect(next_location):
                collision = True
                # Flats
                if self.vx > 0 and object.rect.colliderect(pygame.Rect(next_location.left + next_location.w, rect.top, 0, next_location.h)):    # Left
                    self.realX = object.rect.left - next_location.w
                if self.vx < 0 and object.rect.colliderect(pygame.Rect(next_location.right - next_location.w, rect.top, 0, next_location.h)):    # right
                    self.realX = object.rect.right
                if self.vy > 0 and object.rect.colliderect(pygame.Rect(rect.left, next_location.top + next_location.h, next_location.w, 0)):    # top
                    self.realY = object.rect.top - next_location.h
                if self.vy < 0 and object.rect.colliderect(pygame.Rect(rect.left, next_location.bottom - next_location.h, next_location.w, 0)):    # bottom
                    self.realY = object.rect.bottom
                # Corners
                """if object.rect.collidepoint(rect.topleft[0] + 0.1, rect.topleft[1] + 0.1):
                    [self.realX, self.realY] = [original_x + 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomleft[0] + 0.1, rect.bottomleft[1] - 0.1):
                    [self.realX, self.realY] = [original_x + 1.1, original_y - 0.1]
                if object.rect.collidepoint(rect.topright[0] - 0.1, rect.topright[1] + 0.1):
                    [self.realX, self.realY] = [original_x - 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomright[0] - 0.1, rect.bottomright[1] - 0.1):
                    [self.realX, self.realY] = [original_x - 1.1, original_y - 0.1]"""

            if object.rect.collidepoint(rect.center):   # Moves character out if fully inside a block
                [self.realX, self.realY] = self.startPoint
        self.collision_rect.x = self.realX
        self.collision_rect.y = self.realY
        if collision == False:
            self.startPoint = self.collision_rect
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.rect.midbottom = self.collision_rect.midbottom

    def get_collision_box(self):
        return Box(self.collision_rect)


class Player(Character):
    def __init__(self, rect, charset, sprite_size_rect):
        super(Player, self).__init__(rect, charset, sprite_size_rect)
        self.score = 5
        self.kitCount = 0
        self.direction = 180

    def update_speed(self):
        keys = pygame.key.get_pressed()
        speed = self.baseSpeed
        if not (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT]):
            self.vy = 0
            self.vx = 0
        else:
            if keys[K_UP]:
                self.vy = -speed
                self.direction = 0
            if keys[K_DOWN]:
                self.vy = speed
            if keys[K_LEFT]:
                self.vx = -speed
            if keys[K_RIGHT]:
                self.vx = speed
            if keys[K_UP] == keys[K_DOWN]:
                self.vy = 0
            if keys[K_RIGHT] == keys[K_LEFT]:
                self.vx = 0
        if self.charset:
            self.set_sprite_direction()


class NPC(Character):
    def __init__(self, rect, charset, sprite_size_rect):
        super(NPC, self).__init__(rect, charset, sprite_size_rect)
        self.path = list()
        self.pathBricks = list()
        self.pathfinder = AStar()

    def update_path(self, grid, position, destination, search_range=-1, absolute_max=250):
        # NPC Pathfinding
        p = self.pathfinder.find_path(grid, position, destination, search_range, absolute_max)
        path = list()
        if p is not None:
            self.path = list(p.nodes)
            for n in p.nodes:
                path.append(Brick(n.value[0] * drawSize, n.value[1] * drawSize, drawSize))
            self.pathBricks = path


class Stalker(NPC):
    def __init__(self, rect, charset, sprite_size_rect):
        super(Stalker, self).__init__(rect, charset, sprite_size_rect)
        self.baseSpeed = 0.09
        self.followPlayer = True
        self.next_square = 0

    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            return
        speed = round(self.baseSpeed, 2)
        rect = self.collision_rect
        next_loc = path[0].value
        next_square = pygame.Rect(next_loc[0] * drawSize, next_loc[1] * drawSize, drawSize, drawSize)
        self.next_square = pygame.Rect(next_square)
        if next_square.contains(self.collision_rect):
            self.path.pop(0)
            return
        if rect.right < next_square.right and rect.left < next_square.left:
            self.vx = speed
        elif rect.left > next_square.left and rect.right > next_square.right:
            self.vx = -speed
        else:
            self.vx = 0
        if rect.bottom < next_square.bottom and rect.top < next_square.top:
            self.vy = speed
        elif rect.top > next_square.top and rect.bottom > next_square.bottom:
            self.vy = -speed
        else:
            self.vy = 0
        if self.charset:
            self.set_sprite_direction()

    def update_position(self, time, collidables):
        super(Stalker, self).update_position(time, collidables)
        if self.path is None or not self.path:
            return
        testrect = pygame.Rect(self.collision_rect)
        if self.original_x - self.realX > 0:
            testrect.w -= (self.original_x - self.realX)
        if self.original_x - self.realX < 0:
            testrect.w += (self.original_x - self.realX)
            testrect.x -= (self.original_x - self.realX)
        if self.original_y - self.realY > 0:
            testrect.h -= (self.original_y - self.realY)
        if self.original_y - self.realY < 0:
            testrect.h += (self.original_y - self.realY)
            testrect.y -= (self.original_y - self.realY)
        if testrect != 0 and self.next_square and self.next_square.contains(testrect):
            self.path.pop(0)
