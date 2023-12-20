import pygame
from game import TIMESTEP, DISPLAY_WIDTH, DISPLAY_HEIGHT, GAMESTATE, RATIOS


YACC = [
    # DISPLAY HEIGHT --> ballY == 229
    DISPLAY_HEIGHT, # DONE
    DISPLAY_HEIGHT * 1.03, # DONE
    DISPLAY_HEIGHT * 0.82, # DONE
    DISPLAY_HEIGHT * 0.95, # DONE
    DISPLAY_HEIGHT * 1, # NOT
    DISPLAY_HEIGHT * 1 # NOT
]

resize = DISPLAY_WIDTH / 890

class Ball(pygame.sprite.Sprite):
    """
    A pygame object for the game.
    """
    # 9.5 Seconds from one side to the other
    XSPEED = DISPLAY_WIDTH / 9.5
    # Ball size
    sizes = [
        int(DISPLAY_WIDTH / 50.7273), # 55=b1
        int(DISPLAY_WIDTH / 29.3684), # 95=b2
        int(DISPLAY_WIDTH / 15.7627), # 177=b3
        int(DISPLAY_WIDTH / 10.856), # 257=b4
        int(DISPLAY_WIDTH / 8.2301), # 339=b5
        int(DISPLAY_WIDTH / 6.7718)] # 412=b6

    SPRITES = {
        'yellow':pygame.image.load("Sprites/ball_yellow.png"),
        'red':pygame.image.load("Sprites/ball_red.png"),
        'blue':pygame.image.load("Sprites/ball_blue.png"),
        'purple':pygame.image.load("Sprites/ball_purple.png"),
        'green':pygame.image.load("Sprites/ball_green.png"),
        'orange':pygame.image.load("Sprites/ball_orange.png"),
        'pink':pygame.image.load("Sprites/ball_pink.png")}

    # Ball bounce height (floor to bottom of ball)
    BOUNCE_HEIGHT = [
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.1695,
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.3498,
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.4292,
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.515,
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.5966,
        DISPLAY_HEIGHT - DISPLAY_HEIGHT * 0.6803
    ]
    bounce_time = [
        # seconds / bounce_height / 2
        27.17 / 25 / 2,
        35.29 / 23 / 2,
        32.08 / 18 / 2,
        17.48 / 10 / 2,
        -1,
        -1
    ]
    YSPEED = [YACC[i] * t for i, t in enumerate(bounce_time)]

    def __init__(self, x, y, xspeed, yspeed, xacceleration, ballsize, color):
        assert ballsize < 5
        super().__init__() # equivalent to pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        if type(xspeed) in [float, int]:
            self.xspeed = xspeed
        elif xspeed == 'left':
            self.xspeed = -Ball.XSPEED
        elif xspeed == 'right':
            self.xspeed = Ball.XSPEED
        else:
            self.xspeed = 0

        self.yspeed = yspeed
        self.xacceleration = xacceleration
        self.ballsize = ballsize
        self.size = Ball.sizes[ballsize]
        self.color = color
        self.image = pygame.transform.scale(Ball.SPRITES[color], (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.width = self.rect.width
        self.height = self.rect.height

        self.gsY = round(self.y / RATIOS['y'])
        self.gsX = round(self.x / RATIOS['x'])
        self.gsH = round(self.height / RATIOS['y'])
        self.gsW = round(self.width / RATIOS['x'])

        GAMESTATE[self.gsY:self.gsY+self.gsH, self.gsX:self.gsX+self.gsH, 1] = 1

    def get_features(self):
        return [self.x / DISPLAY_WIDTH,
                (self.x + self.width) / DISPLAY_WIDTH,
                self.y / DISPLAY_HEIGHT,
                (self.y + self.height) / DISPLAY_HEIGHT]
        
    def getSize(self):
        return self.ballsize

    def bounceX(self):
        if self.x > DISPLAY_WIDTH / 2:
            self.xspeed = -Ball.XSPEED
        else:
            self.xspeed = Ball.XSPEED

    def bounceY(self):
        self.yspeed = -Ball.YSPEED[self.ballsize]

    def update(self):
        """
        Overides pygame.sprite.Sprite.update()
        Applied when Group.update() is called.

        Args:
            t (float): the timestep of the update.
        Returns:
            None.
        Raises:
            None.
        """
        # Update position
        self.x += self.xspeed * TIMESTEP
        # y = y0 + v0yt + ½at2
        self.y += self.yspeed * TIMESTEP + 0.5 * YACC[self.ballsize] * TIMESTEP ** 2
        
        if self.y < 0:
            GAMESTATE[self.gsY:self.gsY+self.gsH, self.gsX:self.gsX+self.gsH, 1] = 0
            print("Ceiling pop!")
            self.kill()
            return
        
        # Update speed
        self.xspeed += self.xacceleration * TIMESTEP
        # vy2	 = v0y2 − 2g(y − y0)
        self.yspeed += YACC[self.ballsize] * TIMESTEP

        # Update rect dimensions
        self.rect.x = self.x
        self.rect.y = self.y

        # Update Gamestate
        GAMESTATE[self.gsY:self.gsY+self.gsH, self.gsX:self.gsX+self.gsH, 1] = 0
        self.gsY = round(self.y / RATIOS['y'])
        self.gsX = round(self.x / RATIOS['x'])
        GAMESTATE[self.gsY:self.gsY+self.gsH, self.gsX:self.gsX+self.gsH, 1] = 1

    def pop(self):
        """
        Occurs when the player hits the ball with their laser.

        Args:
            None.
        Returns:
            2 balls of size n-1.
        Raises:
            None.
        """
        GAMESTATE[self.gsY:self.gsY+self.gsH, self.gsX:self.gsX+self.gsH, 1] = 0
        if self.ballsize == 0:
            return
        else:
            # (0 - self.yspeed) / -YACC[self.ballsize]
            time_from_top = abs(self.yspeed / YACC[self.ballsize])
            # the closer the ball is to the vertex, the higher it pops
            newYspeed = max(-300 * resize, -30 / (time_from_top) * resize)
            return (Ball(self.x-10, self.y, 'left', newYspeed,
                    0, self.ballsize-1, self.color),
                    Ball(self.x+10, self.y, 'right', newYspeed,
                    0, self.ballsize-1, self.color))