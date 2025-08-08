# Complete your game here
import pygame
from random import randint
from datetime import datetime

class CollectTheCoins:
    # initiate pygame, set up the default game values, and enter the game loop
    def __init__(self):
        pygame.init()

        self.__highscore = 0

        self.__ref_time = datetime.now()

        self.__clock = pygame.time.Clock()

        self.__window_width = 640
        self.__window_height = 480
        self.__window = pygame.display.set_mode((self.__window_width, self.__window_height))

        self.__game_font = pygame.font.SysFont("Arial", 24)

        self.__num_coins = 20
        self.__num_monsters = 5
        
        self.__render_ctrls_text()
        self.__load_images()
        self.__new_game()

        pygame.display.set_caption("Collect the Coins")

        self.__main_loop()
    
    # create basic controls information text, which we will use to obtain the height for the ground
    def __render_ctrls_text(self):
        self.__new_game_text = self.__game_font.render("F2 = restart", True, (0, 0, 0))
        self.__exit_game_text = self.__game_font.render("Esc = close", True, (0, 0, 0))
        self.__ground_height = self.__new_game_text.get_height()

    # load all of the images, rendered into a dictionary for easy access and code clarity
    def __load_images(self):
        images = ["coin", "monster", "robot"]
        self.__images = {}
        for image in images:
            self.__images[image] = pygame.image.load(image + ".png")

    # starts a new game and resets all of the default values other than highscore
    def __new_game(self):
        self.__game_over = False
        midpoint = (self.__window_width / 2, self.__window_height / 2)
        self.__robot_pos = [midpoint[0] - self.__images["robot"].get_width() / 2, self.__window_height - (self.__ground_height + self.__images["robot"].get_height())]
        self.__coins_collected = 0
        self.__monster_speed = 1
        self.__coin_speed = 1
        self.__robot_speed = 5
        self.__coins = []
        self.__monsters = []
        for i in range(self.__num_coins):
            if i < self.__num_monsters: self.__monsters.append([randint(0, self.__window_width - self.__images["monster"].get_width()), -randint(100, 1000)])
            self.__coins.append([randint(0, self.__window_width - self.__images["coin"].get_width()), -randint(100, 1000)])

    # main loop for the game
    def __main_loop(self):
        movement_right = movement_left = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
                    if event.key == pygame.K_F2:
                        self.__new_game()
                    if event.key == pygame.K_LEFT:
                        movement_left = True
                    if event.key == pygame.K_RIGHT:
                        movement_right = True
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        movement_left = False
                    if event.key == pygame.K_RIGHT:
                        movement_right = False
                
                if event.type == pygame.QUIT:
                    exit()
            
            if movement_left: self.__move(-1)
            if movement_right: self.__move(1)

            self.__update_speeds()
            
            self.__draw_window()

            self.__clock.tick(60)
    
    # draw all the objects in the window
    def __draw_window(self):
        # make the window a nice sky blue
        self.__window.fill((135, 206, 235))

        # create a rectangular ground, which looks like grass 
        pygame.draw.rect(self.__window, (60, 179, 113), (0, self.__window_height - self.__ground_height, self.__window_width, self.__window_height - self.__ground_height))

        # add the necessary game text
        cur_text_width = 0

        score_text = self.__game_font.render(f"Score: {self.__coins_collected}", True, (0, 0, 0))
        self.__window.blit(score_text, (cur_text_width, self.__window_height - self.__ground_height))

        cur_text_width += score_text.get_width() + 25

        highscore_text = self.__game_font.render(f"High Score: {self.__highscore}", True, (0, 0, 0))
        self.__window.blit(highscore_text, (cur_text_width, self.__window_height - self.__ground_height))

        cur_text_width += highscore_text.get_width() + 25

        self.__window.blit(self.__new_game_text, (cur_text_width, self.__window_height - self.__ground_height))

        cur_text_width += self.__new_game_text.get_width() + 25

        self.__window.blit(self.__exit_game_text, (cur_text_width, self.__window_height - self.__ground_height))

        # update all moving objects in the game
        self.__update_falling_objects()
        self.__window.blit(self.__images["robot"], tuple(self.__robot_pos))
        for coin in self.__coins:
            self.__window.blit(self.__images["coin"], tuple(coin))
        for monster in self.__monsters:
            self.__window.blit(self.__images["monster"], tuple(monster))
        
        # check for game over flag and stop the game upon the flag being set
        if self.__game_over:
            game_over_text = self.__game_font.render("Game Over", True, (255, 0, 0))
            game_over_x = self.__window_width / 2 - game_over_text.get_width() / 2
            game_over_y = self.__window_height / 2 - game_over_text.get_height() / 2
            pygame.draw.rect(self.__window, (0, 0, 0), (game_over_x, game_over_y, game_over_text.get_width(), game_over_text.get_height()))
            self.__window.blit(game_over_text, (game_over_x, game_over_y))

        pygame.display.flip()
    
    # move robot in direction, -1 for left and 1 for right
    def __move(self, direction: int):
        if self.__game_over: return

        new_x = self.__robot_pos[0] + direction * self.__robot_speed

        if new_x < 0 or new_x > self.__window_width - self.__images["robot"].get_width():
            return
        
        self.__robot_pos[0] = new_x
    
    # update positions of falling objects, reset objects at random place upon collision with robot or ground
    def __update_falling_objects(self):
        if self.__game_over: return

        for i in range(self.__num_coins):
            if self.__game_over: break

            if i < self.__num_monsters:
                self.__monsters[i][1] += self.__monster_speed
                if self.__collision_occured(self.__monsters[i][0], self.__monsters[i][1], self.__images["monster"].get_width(), self.__images["monster"].get_height(), self.__monster_collision_task) or self.__monsters[i][1] + self.__images["monster"].get_height() >= self.__window_height - self.__ground_height:
                    self.__monsters[i][0] = randint(0, self.__window_width - self.__images["monster"].get_width())
                    self.__monsters[i][1] = -randint(100, 1000)

            self.__coins[i][1] += self.__coin_speed
            if self.__collision_occured(self.__coins[i][0], self.__coins[i][1], self.__images["coin"].get_width(), self.__images["coin"].get_height(), self.__coin_collision_task) or self.__coins[i][1] + self.__images["coin"].get_height() >= self.__window_height - self.__ground_height:
                self.__coins[i][0] = randint(0, self.__window_width - self.__images["coin"].get_width())
                self.__coins[i][1] = -randint(100, 1000)
            
    # check for collision between robot and a falling object, perform task and return True upon collision otherwise just return False
    def __collision_occured(self, x: int, y: int, object_width: int, object_height: int, task: callable):
        if y + object_height >= self.__robot_pos[1]:
            robot_midpoint = self.__robot_pos[0] + self.__images["robot"].get_width() / 2
            object_midpoint = x + object_width / 2
            if abs(robot_midpoint - object_midpoint) <= (self.__images["robot"].get_width() + object_width) / 2:
                task()
                return True
        return False

    # increase coin count upon collision
    def __coin_collision_task(self):
        self.__coins_collected += 1
        self.__highscore = max(self.__highscore, self.__coins_collected)
    
    # set game over flag upon monster collision
    def __monster_collision_task(self):
        self.__game_over = True
    
    # update monster falling speed by 25% after every 10 seconds
    def __update_speeds(self):
        now = datetime.now()
        if (now - self.__ref_time).total_seconds() >= 10:
            self.__monster_speed *= 1.25
            self.__ref_time = now

CollectTheCoins()
