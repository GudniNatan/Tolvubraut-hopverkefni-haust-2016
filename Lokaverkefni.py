import pygame
from pygame.locals import *
import threading
import sys
import os
from Scenes import *

def main():
    # Pygame stuff
    pygame.init()
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pygame.display.set_caption('FOR3G3U')

    #Setup
    charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
    pygame.time.set_timer(pathfindingEvent, 500)
    pygame.time.set_timer(animationEvent, 1000 / 24)
    gridImage = pygame.image.load(os.path.join('images', 'grid 16x16 transculent.png')).convert_alpha()
    gridImage = pygame.transform.scale(gridImage, (gridImage.get_rect().w * 24 / 16, gridImage.get_rect().h * 24 / 16))
    manager = SceneMananger()
    pygame.mixer.init()

    running = True
    while running:  # Game loop
        if pygame.event.get(QUIT):
            running = False
            return
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update(clock.get_time())
        manager.scene.render(screen)
        pygame.display.update()
        clock.tick()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()