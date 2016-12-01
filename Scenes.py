import pygame
import os
import random
import codecs
import copy
import MySQLdb
from pygame.locals import *
from eztext import *
from generateMaze import Generator
from Constants import *
from Characters_sprites import *
from Objects import *


class SceneManager(object):
    def __init__(self):
        self.go_to(TitleScene())

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


class MazeScene(Scene):

    def __init__(self, level, difficulty=0):
        super(MazeScene, self).__init__()
        # Generate maze
        print("new level")
        self.level = level
        print(self.level)
        mazeGenerator = Generator()
        self.grid = Grid(GRID_SIZE)
        if level > 14:
            level = 14
        self.maze = mazeGenerator.generate(0, 0, 2 + level, 2 + level)
        levelDrawSize = drawSize
        self.levelDrawSize = levelDrawSize
        mazeBox = pygame.Rect(0, 0, 0, 0)
        mazeBox.x = 28 * levelDrawSize - ((level + level % 2 - 1) * levelDrawSize)  # Change the first number to move maze
        mazeBox.y = 15 * levelDrawSize - ((level + level % 2 - 1) * levelDrawSize)
        mazeBox.w = (level + 2) * levelDrawSize * 2 + levelDrawSize
        mazeBox.h = mazeBox.w
        self.mazeBox = mazeBox
        self.block_group = pygame.sprite.Group()
        self.last_safe_pos = pygame.mouse.get_pos()
        if difficulty == 0:
            self.godMode = True
        if difficulty == 1:
            self.godMode = True
        elif difficulty == 2:
            self.godMode = False
        self.difficulty = difficulty
        self.floor_tile = pygame.image.load(os.path.join('images', 'floor.png')).convert_alpha()
        self.floor_tile = pygame.transform.smoothscale(self.floor_tile, (self.levelDrawSize, self.levelDrawSize))
        self.wall_tile = pygame.image.load(os.path.join('images', 'steinn.png')).convert_alpha()
        self.wall_tile = pygame.transform.smoothscale(self.wall_tile, (self.levelDrawSize, self.levelDrawSize))


        if self.level % 2:
            self.exit = Block(pygame.Rect(mazeBox.left + levelDrawSize, mazeBox.top, levelDrawSize, levelDrawSize), GREEN)
            self.entrance = Block(pygame.Rect(mazeBox.right - levelDrawSize*2, mazeBox.bottom - levelDrawSize, levelDrawSize, levelDrawSize), BLUE)
            topcap = copy.deepcopy(self.exit)
            bottomcap = copy.deepcopy(self.entrance)
        else:
            self.exit = Block(pygame.Rect(mazeBox.right - levelDrawSize*2, mazeBox.bottom - levelDrawSize, levelDrawSize, levelDrawSize), GREEN)
            self.entrance = Block(pygame.Rect(mazeBox.left + levelDrawSize, mazeBox.top, levelDrawSize, levelDrawSize), BLUE)
            topcap = copy.deepcopy(self.entrance)
            bottomcap = copy.deepcopy(self.exit)

        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == 0:
                    if not (i == len(self.maze) - 2 and j == len(self.maze[i]) - 1):
                        if not (i == 1 and j == 0):
                            self.block_group.add(Block(pygame.Rect(i * levelDrawSize + mazeBox.left, j * levelDrawSize + mazeBox.top, levelDrawSize, levelDrawSize), BLACK, self.wall_tile))
        self.stalker = None
        if level >= 5 and difficulty > 0:
            pygame.time.set_timer(stalkerEvent, 5000)  # Spawn stalker after 5 seconds
        topcap.rect.y -= levelDrawSize
        bottomcap.rect.y += levelDrawSize
        self.grid.update_grid(pygame.sprite.Group(self.block_group, topcap, bottomcap), self.levelDrawSize)
        self.last_pos = self.entrance.rect.center

    def render(self, screen):
        screen.fill(WHITE)
        for i in xrange(self.mazeBox.w / self.levelDrawSize):
            for j in xrange(self.mazeBox.h / self.levelDrawSize):
                screen.blit(self.floor_tile, (i * self.levelDrawSize + self.mazeBox.left, j * self.levelDrawSize + self.mazeBox.top))

        self.block_group.draw(screen)
        screen.blit(self.exit.image, self.exit.rect)
        screen.blit(self.entrance.image, self.entrance.rect)
        if self.stalker:
            screen.blit(self.stalker.image, self.stalker.rect)
        pygame.draw.rect(screen, BLACK, self.mazeBox, 3)


    def update(self, time):
        check_col = False
        for block in self.block_group:
            if block.rect.collidepoint(pygame.mouse.get_pos()):
                if not self.godMode:
                    self.manager.go_to(GameOverScene())
                else:
                    check_col = True
        if not self.mazeBox.collidepoint(pygame.mouse.get_pos()):
            if not self.godMode:
                self.manager.go_to(GameOverScene())
            else:
                check_col = True
            print("outside game area")
        if ((self.last_pos[0] - pygame.mouse.get_pos()[0]) ** 2 + (self.last_pos[1] - pygame.mouse.get_pos()[1]) ** 2 > self.levelDrawSize ** 2):
            coords1 = ((self.last_pos[0] + pygame.mouse.get_pos()[0] * 2) / 3, (self.last_pos[1] + pygame.mouse.get_pos()[1] * 2) / 3)
            coords2 = ((self.last_pos[0] + pygame.mouse.get_pos()[0]) / 2, (self.last_pos[1] + pygame.mouse.get_pos()[1]) / 2)
            coords3 = ((self.last_pos[0]*2 + pygame.mouse.get_pos()[0]) / 3, (self.last_pos[1]*2 + pygame.mouse.get_pos()[1]) / 3)
            print(self.last_pos)
            print(coords1)
            print(pygame.mouse.get_pos())
            for block in self.block_group:
                if block.rect.collidepoint(coords1) or block.rect.collidepoint(coords2) or block.rect.collidepoint(coords3):
                    if not self.godMode:
                        self.manager.go_to(GameOverScene())
                    else:
                        check_col = True
        if not check_col:
            self.last_pos = pygame.mouse.get_pos()
        else:
            pygame.mouse.set_pos(self.last_pos)
        if self.exit.rect.collidepoint(pygame.mouse.get_pos()):
            self.manager.go_to(MazeScene(self.level+1, self.difficulty))
        if self.stalker is not None:
            self.stalker.update_speed()
            self.stalker.update_position(time.get_time(), self.block_group)
            if self.stalker.rect.collidepoint(pygame.mouse.get_pos()):
                self.manager.go_to(GameOverScene())

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            if event.type == stalkerEvent and not self.stalker:
                pygame.time.set_timer(stalkerEvent, 0)  # Stops timer after running once
                stalkerRect = pygame.Rect(self.entrance.rect)
                stalkerRect.center = self.entrance.rect.center
                self.stalker = Stalker(stalkerRect, 0, 0)
                self.stalker.baseSpeed += (-0.05) + self.level * 0.01
                pygame.event.post(pygame.event.Event(pathfindingEvent))
                pygame.time.set_timer(pathfindingEvent, 500)
            if event.type == pathfindingEvent and self.stalker:
                mouse_grid_pos = [pygame.mouse.get_pos()[0] / self.levelDrawSize, pygame.mouse.get_pos()[1] / self.levelDrawSize]
                stalker_grid_pos = [self.stalker.collision_rect.x / self.levelDrawSize, self.stalker.collision_rect.y / self.levelDrawSize]
                self.stalker.update_path(self.grid.grid, stalker_grid_pos, mouse_grid_pos)
    def returnLevel():
        if self.level:
            return self.level
        else:
            return 0

class MoveMouseScene(Scene):
    def __init__(self, difficulty):
        super(MoveMouseScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 20)
        self.block = Block(pygame.Rect(30 * drawSize, 16 * drawSize, drawSize, drawSize), GREEN)
        self.text = self.font.render('Move your mouse into the green box.', True, WHITE)
        self.difficulty = difficulty

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.block.image, self.block.rect)
        screen.blit(self.text, (200, 150))

    def update(self, time):
        if self.block.rect.collidepoint(pygame.mouse.get_pos()):
            print("true")
            self.manager.go_to(MazeScene(0, self.difficulty))

    def handle_events(self, events):
        pass


class TitleScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.3)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
        self.mixer.play(self.music)
        print("music")
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]
        self.titletext = self.font.render('Lokaverkefni', True, tuple(self.color))
        self.text1 = self.sfont.render('Hall of fame ', True, WHITE)
        self.text2 = self.sfont.render('Choose your difficulty: ', True, WHITE)

        #self.txtbx = eztext.Input(maxlength=45, color=(255,0,0), prompt='type here: ')
        self.difficultyText = list()
        self.topten = list()
        self.difficultyText.append(SimpleSprite((700, 300), self.sfont.render('Easy Mode', True, WHITE)))
        self.difficultyText.append(SimpleSprite((700, 400), self.sfont.render('Hard Mode', True, WHITE)))
        self.difficultyText.append(SimpleSprite((700, 500), self.sfont.render('Extreme Mode', True, WHITE)))
        self.menutext = pygame.sprite.Group(self.difficultyText)
        self.selected = 0

        #connect to db and get the top 10
        self.db = MySQLdb.connect("tsuts.tskoli.is", "0403983099","mypassword" , "0403983099_highscores")
        if self.db:
            print "connected"
        cursor = self.db.cursor()

        sql = "SELECT name, score FROM data ORDER BY score ASC"

        try:
            
           # Execute the SQL command
           cursor.execute(sql)
           # Fetch all the rows in a list of lists.
           results = cursor.fetchall()
           for row in results:
              name = row[0]
              score = row[1]
              # Now print fetched result
              print name,"  -  " ,score
              self.topten.append(SimpleSprite((200, 300), self.sfont.render('name and score', True, WHITE)))

        except Exception as e:
            raise

    def render(self, screen):
        self.titletext = self.font.render('Lokaverkefni', True, tuple(self.color))
        #screen.blit(self.txtbx, (450, 200))

        screen.fill(BLACK)
        screen.blit(self.titletext, (450, 50))
        screen.blit(self.text1, (250, 200))
        screen.blit(self.text2, (620, 200))
        self.menutext.draw(screen)
        #pygame.draw.rect(screen, WHITE, self.topten.rect, 1)
        pygame.draw.rect(screen, WHITE, self.difficultyText[self.selected].rect, 3)


    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_RETURN):
                self.mixer.fadeout(500)
                self.manager.go_to(MoveMouseScene(self.selected))
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
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
            if event.type == KEYDOWN and event.key == K_UP:
                self.selected -= 1
                self.selected %= 3
            if event.type == KEYDOWN and event.key == K_DOWN:
                self.selected += 1
                self.selected %= 3


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
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.8)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'triggered.ogg'))
        self.mixer.play(self.music)
        self.txtbx = Input(maxlength=45, color=(255,0,0), prompt='type here: ')

        font = pygame.font.SysFont('Consolas', 56)
        small_font = pygame.font.SysFont('Consolas', 32)
        self.text = font.render('Game Over', True, WHITE)
        self.text2 = small_font.render('Press space to try again.', True, WHITE)
        self.text3 = small_font.render('want to submit to leaderboards?', True, WHITE)
        #text_width, text_height = small_font.size("self.text3")
        #screen = pygame.display.set_mode((100, 100))
        #self.inp = ask("what is your name?") #inp will equal whatever the input is


    def render(self, screen):
        screen.fill(BLACK)

        screen.blit(self.text, (500, 50))
        screen.blit(self.text2, (440, 120))
        screen.blit(self.text3, (440, 200))
        #screen.blit(self.inp, (440, 300))
        self.txtbx.draw(screen)

        pygame.display.flip()

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.manager.go_to(TitleScene())
<<<<<<< HEAD
            self.txtbx.update(events)

class ScoreScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.3)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
        self.mixer.play(self.music)
        print("music")
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]
        self.titletext = self.font.render('Lokaverkefni', True, tuple(self.color))
        self.text2 = self.sfont.render('Choose your difficulty: ', True, WHITE)
        #self.txtbx = eztext.Input(maxlength=45, color=(255,0,0), prompt='type here: ')
        self.difficultyText = list()
        self.difficultyText.append(SimpleSprite((420, 450), self.sfont.render('babby Mode', True, WHITE)))
        self.difficultyText.append(SimpleSprite((420, 450), self.sfont.render('babby Mode', True, WHITE)))
        self.difficultyText.append(SimpleSprite((420, 500), self.sfont.render('normal Mode', True, WHITE)))
        self.difficultyText.append(SimpleSprite((420, 550), self.sfont.render('spergstreme', True, WHITE)))
        self.menutext = pygame.sprite.Group(self.difficultyText)
        self.selected = 0


    def render(self, screen):
        self.titletext = self.font.render('Lokaverkefni', True, tuple(self.color))
        #screen.blit(self.txtbx, (450, 200))

        screen.fill(BLACK)
        screen.blit(self.titletext, (450, 50))
        screen.blit(self.text2, (420, 350))
        self.menutext.draw(screen)
        pygame.draw.rect(screen, WHITE, self.difficultyText[self.selected].rect, 3)


    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_RETURN):
                self.mixer.fadeout(500)
                self.manager.go_to(MoveMouseScene(self.selected))
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
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
            if event.type == KEYDOWN and event.key == K_UP:
                self.selected -= 1
                self.selected %= 3
            if event.type == KEYDOWN and event.key == K_DOWN:
                self.selected += 1
                self.selected %= 3


=======
>>>>>>> origin/njalsson
