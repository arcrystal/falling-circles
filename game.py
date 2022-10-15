import pygame

from player import Player
from ball import Ball
from floor import Floor
from laser import Laser

import math
import time


class Game:
    """
    Game object for falling circles.
    """
    WHITE  = (255, 255, 255)
    BLACK  = (  0,   0,   0)
    RED    = (255,   0,   0)
    GREEN  = (  0, 255,   0)
    BLUE   = (  0,   0, 255)
    ORANGE = (255, 255,   0)
    YELLOW = (  0, 255, 255)
    FPS = 52
    TIMESTEP = 0.1
    DISPLAY_WIDTH = 890
    DISPLAY_HEIGHT = DISPLAY_WIDTH / 1.8737
    LVL_TIME = [20000, 40000, 50000, 75000, 100000, 125000]

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        # Initialize gameplay window
        self.screen = pygame.display.set_mode((Game.DISPLAY_WIDTH, Game.DISPLAY_HEIGHT+27+10)) # + platform_h + timer_h
        pygame.display.set_caption("Ball Breaker")
        # Initialize gameplay vars
        self.score = 0
        self.level = 1
        self.font = pygame.font.SysFont('Calibri', 25, True, True)
        self.text = self.font.render(f"Score: {self.score}", True, Game.RED)
        self.screen.blit(self.text, (25, 25))
        self.backgrounds = [pygame.image.load("Backgrounds/bluepink.jpg").convert()] * len(Game.LVL_TIME)
        # Initialize sprite Groups
        
        self.objects = [pygame.sprite.Group() for _ in range(10)]
        for group in self.objects:
            group.add(Player())
            group.add(Floor())
        self.objects[0].add(Ball(Game.DISPLAY_WIDTH // 4, Game.DISPLAY_HEIGHT // 6, 0, 0, 0, 1, 'yellow'))
        self.objects[1].add(Ball(Game.DISPLAY_WIDTH // 4, Game.DISPLAY_HEIGHT // 6, 0, 0, 0, 2, 'green'))
        self.objects[2].add(Ball(Game.DISPLAY_WIDTH // 4, Game.DISPLAY_HEIGHT // 6, 0, 0, 0, 3, 'red'))
        self.objects[3].add(
            Ball(Game.DISPLAY_WIDTH // 4, Game.DISPLAY_HEIGHT // 6, 'left', 0, 0, 2, 'orange'),
            Ball(3 * Game.DISPLAY_WIDTH // 4, Game.DISPLAY_HEIGHT // 6, 'right', 0, 0, 2, 'orange'))
        self.objects[5].add(
            Ball(Game.DISPLAY_WIDTH // 2 - 45, Game.DISPLAY_HEIGHT // 6, 0, 0, 0, 2, 'yellow'),
            Ball(Game.DISPLAY_WIDTH // 2 - 10, Game.DISPLAY_HEIGHT // 6, 0, 0, 0, 3, 'green'))

    def play_music(self, filepath):
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play(-1)

    def load_background(self, background):
        """
        Loads a pygame image as the screen's background.

        Args:
            background (pygame.Surface): raw pygame surface to load.
        Returns:
            Transformed pygame.Surface with the dimensions of the screen.
        Raises:
            None.
        """
        return pygame.transform.scale(background, (Game.DISPLAY_WIDTH, Game.DISPLAY_HEIGHT))

    def draw_timer(self, timeleft):
        pygame.draw.line(
            self.screen, Game.BLACK,
            (0, Game.DISPLAY_HEIGHT+27),
            (timeleft, Game.DISPLAY_HEIGHT+27),
            10)
        # pygame.draw.line(
        #     self.screen, Game.WHITE,
        #     (0, Game.DISPLAY_HEIGHT-20),
        #     (timeleft, Game.DISPLAY_HEIGHT-20),
        #     10)

    def collide(self, laser, ball):
        if laser.rect.x < ball.x + ball.image.get_width() and laser.rect.x + laser.image.get_width() < ball.rect.x:
            if laser.rect.y < ball.rect.y + ball.image.get_height():
                return True

        return False

    def play(self):
        gameover = False
        nextLevel = False
        shooting = False
        laser = None
        clock = pygame.time.Clock()
        for lvl, (lvlsprites, background) in enumerate(zip(self.objects, self.backgrounds)):
            # Check gameover
            if gameover:
                break

            #if lvl!=3: continue # only play a certain level

            # Set up timers
            timer = 0
            timeleft = Game.DISPLAY_WIDTH
            pygame.time.wait(250)

            # Display new level screen
            curr_background = self.load_background(background)
            self.screen.blit(curr_background, (0, 0))
            lvl_font = self.font.render(f'Level {lvl+1}', True, Game.GREEN, Game.BLUE)
            lvl_font_rect = lvl_font.get_rect()
            lvl_font_rect.center = Game.DISPLAY_WIDTH / 2, Game.DISPLAY_HEIGHT / 10
            self.screen.blit(lvl_font, lvl_font_rect)
            pygame.display.update()
            pygame.time.wait(500)

            # Convert sprite pixels
            player = lvlsprites.sprites()[0]
            platform = lvlsprites.sprites()[1]
            balls = pygame.sprite.Group()
            for ball in lvlsprites.sprites()[2:]:
                balls.add(ball)

            for sprites in lvlsprites:
                for key, sprite in sprites.SPRITES.items():
                    sprites.SPRITES[key] = sprite.convert_alpha()
            
            # Play game
            while not (nextLevel or gameover):
                # Get pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameover = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            player.left()
                        if event.key == pygame.K_RIGHT:
                            player.right()
                        if event.key == pygame.K_UP:
                            if not shooting:
                                print("Shoot.")
                                shooting = True
                                laser = Laser(player.rect.centerx)
                        if event.key == pygame.K_SPACE:
                            player.jump()

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT and player.xspeed < 0:
                            player.stopx()
                        if event.key == pygame.K_RIGHT and player.xspeed > 0:
                            player.stopx()

                # Draw and update screen
                self.screen.blit(curr_background, (0, 0))

                # Get collision updates
                for ball in balls:
                    if pygame.sprite.collide_mask(player, ball):
                        gameover = True
                        print("You lose.")
                        break
                    if shooting:
                        laser.update(Game.TIMESTEP)
                        if pygame.sprite.collide_mask(laser, ball):
                        #if self.collide(laser, ball):
                            print("Laser pop.")
                            shooting = False
                            pop_result = ball.pop()
                            lvlsprites.remove(ball)
                            balls.remove(ball)
                            if pop_result is not None:
                                lvlsprites.add(pop_result)
                                balls.add(pop_result)
                                shooting = False
                        elif laser.hitCeiling(Game.TIMESTEP):
                            shooting = False
                        else:
                            self.screen.blit(laser.curr, laser.rect)

                    if pygame.sprite.collide_rect(ball, platform):
                        ball.bounceY()

                self.draw_timer(timeleft)
                lvlsprites.update(Game.TIMESTEP)
                lvlsprites.draw(self.screen)
                pygame.display.update()
                clock.tick(Game.FPS)
                timer += clock.get_time()
                timeleft = Game.DISPLAY_WIDTH - Game.DISPLAY_WIDTH / Game.LVL_TIME[lvl] * timer
                if timeleft <= 0:
                    gameover = False # True (Turn on game timer)
                    print("Time ran out.")
                    # break # uncomment (Turn on game timer)
                elif len(lvlsprites) == 2:
                    nextLevel = True

            nextLevel = False

        pygame.quit()