import pygame
from pygame.locals import *
import os
from Constants import *
from Characters_sprites import *
from Objects import *
import random
import codecs
from generateMaze import Generator


class SceneMananger(object):
    def __init__(self):
        # self.go_to(TitleScene())

        self.go_to(MoveMouseScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self, time):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class GameScene(Scene):
    def __init__(self, level):
        super(GameScene, self).__init__()
        charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
        self.entities = pygame.sprite.LayeredUpdates()
        self.npcs = list()
        self.animations = list()
        self.collidables = list()
        character_sprite_size = (16, 18, 24)
        self.player = Player(pygame.Rect(30, 30, 15, drawSize / 2), charset.subsurface(pygame.Rect(0, 72, 47, 72)), character_sprite_size)

        self.block_group = pygame.sprite.Group()
        self.grid = Grid(GRID_SIZE)

        f = open(os.path.join('rooms', 'room' + str(level)) + ".txt", 'r')
        lines = f.readlines()
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                if lines[i][j] == "W":
                    rect = pygame.Rect(j * drawSize, i * drawSize, drawSize, drawSize)
                    self.block_group.add(Block(rect, BLACK))
                if lines[i][j] == "S":
                    stalker = Stalker(pygame.Rect(j * drawSize, i * drawSize, 15, drawSize / 2), charset.subsurface(pygame.Rect(48, 72, 47, 72)), character_sprite_size)
                    self.npcs.append(stalker)

        '''for i in range(GRID_SIZE[0] * 2):
                block1 = (Block(pygame.Rect(i * drawSize, 0, drawSize, drawSize), BLACK))
                block2 = (Block(pygame.Rect(i * drawSize, (GRID_SIZE[1] * 2 - 1) * drawSize, drawSize, drawSize), BLACK))
                self.block_group.add(block1, block2)
        for i in range(GRID_SIZE[1] * 2):
                block1 = (Block(pygame.Rect(0, i * drawSize, drawSize, drawSize), BLACK))
                block2 = (Block(pygame.Rect((GRID_SIZE[0] * 2 - 1) * drawSize, i * drawSize, drawSize, drawSize), BLACK))
                self.block_group.add(block1, block2)'''
        self.collidables.extend(self.block_group)

        self.entities.add(self.player, self.npcs)
        self.character_collision_boxes = [char.get_collision_box() for char in self.entities]
        self.grid.update_grid(self.collidables + self.character_collision_boxes)

    def render(self, screen):
        screen.fill(WHITE)
        self.block_group.draw(screen)
        self.entities.draw(screen)

    def update(self, time):
        for sprite in self.entities.sprites():
            self.entities.change_layer(sprite, sprite.rect.centery)
        self.character_collision_boxes = [entity.get_collision_box() for entity in self.entities]
        for entity in self.entities:
            if type(entity) is not Player:
                entity.update_speed()
            entity.update_position(time, self.collidables + self.character_collision_boxes)

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                pygame.event.post(pygame.event.Event(swordSwingEvent))
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.player.update_speed()
            if event.type == pathfindingEvent:
                for char in self.npcs:
                    if type(char) is Stalker:
                        char.update_path(self.grid.grid, char.gridPos, self.player.gridPos)
            if event.type == updateGridEvent:
                self.grid.update_grid(self.collidables + self.character_collision_boxes)
            if event.type == animationEvent:
                # Update all active animations
                for s in self.animations:
                    '''if s.name == "sword":
                        if sword.rotation < s.end and s.direction == self.player.direction:
                            sword.display = True
                            sword.rot_center(50)
                        else:
                            sword.display = False
                            sword.rotation = 0
                            animations.remove(s)'''
                for char in self.entities:
                    if char.moving:
                        char.walking_phase = (char.walking_phase + 0.5) % 3
                        char.update_sprite()
            if event.type == swordSwingEvent:
                '''if Animation("sword") not in animations:
                    sword.rotation = thePlayer.direction - 25
                    params = {'direction': thePlayer.direction, 'end': thePlayer.direction + 100}
                    animations.append(Animation("sword", params))'''


class MazeScene(Scene):

    def __init__(self, level):
        super(MazeScene, self).__init__()
        # Generate maze
        print("new level")
        self.level = level
        mazeGenerator = Generator()
        self.maze = mazeGenerator.generate(0, 0, 2 + level, 2 + level)
        levelDrawSize = drawSize
        self.levelDrawSize = levelDrawSize
        mazeBox = pygame.Rect(0, 0, 0, 0)
        mazeBox.x = 28 * levelDrawSize - ((level + level % 2 - 1) * levelDrawSize)  # Change the first number to move maze placement
        mazeBox.y = 15 * levelDrawSize - ((level + level % 2 - 1) * levelDrawSize)
        mazeBox.w = (level + 2) * levelDrawSize * 2 + levelDrawSize
        mazeBox.h = mazeBox.w
        self.mazeBox = mazeBox
        self.block_group = pygame.sprite.Group()
        if level % 2:
            self.exit = Block(pygame.Rect(mazeBox.left + levelDrawSize, mazeBox.top, levelDrawSize, levelDrawSize), GREEN)
            self.entrance = Block(pygame.Rect(mazeBox.right - levelDrawSize*2, mazeBox.bottom - levelDrawSize, levelDrawSize, levelDrawSize), BLUE)
        else:
            self.exit = Block(pygame.Rect(mazeBox.right - levelDrawSize*2, mazeBox.bottom - levelDrawSize, levelDrawSize, levelDrawSize), GREEN)
            self.entrance = Block(pygame.Rect(mazeBox.left + levelDrawSize, mazeBox.top, levelDrawSize, levelDrawSize), BLUE)
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == 0:
                    if not (i == len(self.maze) - 2 and j == len(self.maze[i]) - 1):
                        if not (i == 1 and j == 0):
                            self.block_group.add(Block(pygame.Rect(i * levelDrawSize + mazeBox.left, j * levelDrawSize + mazeBox.top, levelDrawSize, levelDrawSize), BLACK))
        self.stalker = 0
        if level > 5:
            pygame.time.set_timer(stalkerEvent, 5000)  # Spawn stalker after 5 seconds


    def render(self, screen):
        screen.fill(WHITE)
        self.block_group.draw(screen)
        screen.blit(self.exit.image, self.exit.rect)
        screen.blit(self.entrance.image, self.entrance.rect)
        pygame.draw.rect(screen, BLACK, self.mazeBox, 3)
        if self.stalker:
            screen.blit(self.stalker.image, self.stalker.rect)
            for node in self.stalker.pathBricks:  # Use this to see stalker pathfinding
                screen.fill(RED, node)


    def update(self, time):
        for block in self.block_group:
            if block.rect.collidepoint(pygame.mouse.get_pos()):
                #self.manager.go_to(GameOverScene())
                print("lose")
        if not self.mazeBox.collidepoint(pygame.mouse.get_pos()):
            print("outside game area")
        if self.exit.rect.collidepoint(pygame.mouse.get_pos()):
            self.manager.go_to(MazeScene(self.level+1))
        if self.stalker:
            mouse_grid_pos = ((pygame.mouse.get_pos()[0] - self.mazeBox.x) / self.levelDrawSize,(pygame.mouse.get_pos()[1] - self.mazeBox.y) / self.levelDrawSize)
            stalker_grid_pos = ((self.stalker.collision_rect.centerx - self.mazeBox.x) / self.levelDrawSize,(self.stalker.collision_rect.centery - self.mazeBox.y) / self.levelDrawSize)
            print(mouse_grid_pos)
            print(stalker_grid_pos)
            print(len(self.maze), len(self.maze[0]))
            self.stalker.update_path(self.maze, stalker_grid_pos, mouse_grid_pos)
            offset = (self.mazeBox.x, self.mazeBox.y)
            self.stalker.update_speed(offset)
            self.stalker.update_position(time, self.block_group)

    def handle_events(self, events):
        for event in events:
            if event.type == stalkerEvent:
                pygame.time.set_timer(stalkerEvent, 0)  # Stops timer after running once
                stalkerRect = pygame.Rect(self.entrance.rect)
                stalkerRect.h -= 2
                stalkerRect.w -= 2
                self.stalker = Stalker(stalkerRect, 0, 0)

        pass


class MoveMouseScene(Scene):
    def __init__(self):
        super(MoveMouseScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 20)
        self.block = Block(pygame.Rect(8 * drawSize, 7 * drawSize, drawSize, drawSize), GREEN)
        self.text = self.font.render('Move mouse inside the box.', True, WHITE)

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.block.image, self.block.rect)
        screen.blit(self.text, (200, 150))

    def update(self, time):
        if self.block.rect.collidepoint(pygame.mouse.get_pos()):
            print("true")
            self.manager.go_to(MazeScene(0))

    def handle_events(self, events):
        pass


class TitleScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.8)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
        self.mixer.play(self.music)
        print("music")
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]

    def render(self, screen):
        screen.fill(BLACK)
        text1 = self.font.render('Lokaverkefni', True, tuple(self.color))
        text2 = self.sfont.render('> press space to start <', True, WHITE)
        screen.blit(text1, (130, 50))
        screen.blit(text2, (100, 350))

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.mixer.fadeout(500)
                self.manager.go_to(GameScene(0))
            if event.type == animationEvent:
                for i in range(3):
                    if self.colorLevel[i]:
                        self.color[i] += i+random.randint(-i, 2)
                        if self.color[i] >= 256:
                            self.color[i] = 255
                            self.colorLevel[i] = False
                    else:
                        self.color[i] -= i+random.randint(-i, 2)
                        if self.color[i] <= 0:
                            self.color[i] = 0
                            self.colorLevel[i] = True


class TextScrollScene(Scene):

    def __init__(self, text):
        f = codecs.open(os.path.join('text', 'text' + str(text)) + ".txt", encoding='utf-8-sig')
        lines = f.readlines()
        self.text = ""
        for i in range(len(lines)):
            lines[i] = lines[i][:-1]
            self.text += lines[i] + "\n"
        self.livetext = ""
        self.font = pygame.font.SysFont('Consolas', 20)
        self.blanks = 0
        self.text_number = text

    def render(self, screen):
        screen.fill(BLACK)
        lines = self.livetext.splitlines()
        for i in range(len(lines)):
            text1 = self.font.render(lines[i], True, WHITE)
            screen.blit(text1, (20, 50 + i*self.font.get_linesize()))

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if self.text_number == 1:
                    self.manager.go_to(TitleScene())
                else:
                    self.manager.go_to(TextScrollScene(self.text_number + 1))
            if event.type == animationEvent:
                if len(self.livetext) + self.blanks != len(self.text):
                    if self.text[len(self.livetext)+self.blanks] == "|":
                        self.blanks += 1
                    else:
                        self.livetext += self.text[len(self.livetext)+self.blanks]


class GameOverScene(Scene):
    def __init__(self):
        self.font = pygame.font.SysFont('Consolas', 56)
        self.text = self.font.render('Game Over', True, WHITE)

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.text, (130, 50))

    def update(self, time):
        pass

    def handle_events(self, events):
        pass