import os
import pygame
import sys
import random
import json
from pygame.math import Vector2

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

pygame.mixer.set_num_channels(16)
pygame.mixer.set_reserved(1)  # channel 0 is kept for the music only
bgm = pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound", "snake bg song.ogg"))
bgm.set_volume(0.4)
bgm_channel = pygame.mixer.Channel(0)
bgm_channel.play(bgm, loops=-1)
print("music length in seconds:", bgm.get_length())
cell_size = 30
cell_number = 20
screen_width = cell_number * cell_size
screen_height = cell_number * cell_size

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()


game_font = pygame.font.Font(None, 48)
ui_font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)
score_font = pygame.font.Font(None, 30)  # FIX 3: smaller font so the score fits in its box

apple = apple = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics", "apple-Photoroom.png")).convert_alpha()
apple = pygame.transform.scale(apple, (cell_size, cell_size))


HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_high_score.json")


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            data = json.load(f)
            return data.get("high_score", 0)
    except:
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)


class Button:
    def __init__(self, x, y, width, height, text, text_color=(255, 255, 255), color=(70, 130, 180), hover_color=(90, 160, 210), border_color=(255,255,255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.color = color
        self.hover_color = hover_color
        self.border_color = border_color

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=18)
        pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=18)

        text_surface = ui_font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class SNAKE:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)
        self.last_move = Vector2(1, 0)  # FIX 5: the direction the snake actually moved last tick
        self.new_block = False

        self.head_right = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics", "head_right.png")).convert_alpha()
        self.head_right = pygame.transform.smoothscale(self.head_right, (cell_size, cell_size))
        self.head_up = pygame.transform.rotate(self.head_right, 90)
        self.head_left = pygame.transform.rotate(self.head_right, 180)
        self.head_down = pygame.transform.rotate(self.head_right, 270)

        self.tail_right = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics", "tail_right.png")).convert_alpha()
        self.tail_right = pygame.transform.smoothscale(self.tail_right, (cell_size, cell_size))
        self.tail_right = pygame.transform.rotate(self.tail_right, 180)
        self.tail_up = pygame.transform.rotate(self.tail_right, 90)
        self.tail_left = pygame.transform.rotate(self.tail_right, 180)
        self.tail_down = pygame.transform.rotate(self.tail_right, 270)

        self.body_horizontal = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics", "body_hori.png")).convert_alpha()
        self.body_horizontal = pygame.transform.smoothscale(self.body_horizontal, (cell_size, cell_size))
        self.body_vertical = pygame.transform.rotate(self.body_horizontal, 90)

        self.body_bl = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics", "corner.png")).convert_alpha()
        self.body_bl = pygame.transform.smoothscale(self.body_bl, (cell_size, cell_size))
        self.body_br = pygame.transform.rotate(self.body_bl, 90)
        self.body_tr = pygame.transform.rotate(self.body_bl, 180)
        self.body_tl = pygame.transform.rotate(self.body_bl, 270)

        try:
            self.crunch_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound", "trimmed.wav"))
        except:
            self.crunch_sound = None

    def draw_snake(self):
        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                direction = self.body[0] - self.body[1]
                if direction == Vector2(1, 0):
                    screen.blit(self.head_right, block_rect)
                elif direction == Vector2(-1, 0):
                    screen.blit(self.head_left, block_rect)
                elif direction == Vector2(0, -1):
                    screen.blit(self.head_up, block_rect)
                else:
                    screen.blit(self.head_down, block_rect)

            elif index == len(self.body) - 1:
                direction = self.body[-2] - self.body[-1]
                if direction == Vector2(-1, 0):
                    screen.blit(self.tail_right, block_rect)
                elif direction == Vector2(1, 0):
                    screen.blit(self.tail_left, block_rect)
                elif direction == Vector2(0, 1):
                    screen.blit(self.tail_up, block_rect)
                else:
                    screen.blit(self.tail_down, block_rect)

            else:
                previous_block = self.body[index - 1] - block
                next_block = self.body[index + 1] - block

                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if (previous_block.x == -1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == -1):
                        screen.blit(self.body_tl, block_rect)
                    elif (previous_block.x == -1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == -1):
                        screen.blit(self.body_bl, block_rect)
                    elif (previous_block.x == 1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == 1):
                        screen.blit(self.body_tr, block_rect)
                    elif (previous_block.x == 1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == 1):
                        screen.blit(self.body_br, block_rect)

    def move_snake(self):
        self.last_move = Vector2(self.direction)  # FIX 5: remember the direction used for this move
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def play_crunch_sound(self):
        if self.crunch_sound:
            self.crunch_sound.play()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)
        self.last_move = Vector2(1, 0)
        self.new_block = False


class FRUIT:
    def __init__(self):
        self.randomize()

    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(apple, fruit_rect)


    def randomize(self, snake_body=()):
        while True:
            self.x = random.randint(0, cell_number - 1)
            self.y = random.randint(0, cell_number - 1)
            self.pos = Vector2(self.x, self.y)
            if self.pos not in snake_body:
                break


class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()
        self.state = "menu"
        self.score = 0
        self.high_score = load_high_score()

        self.start_button = Button(
            screen_width // 2 - 110, 420, 220, 60, "START",
            color=(60, 180, 80), hover_color=(90, 210, 110)
        )

        self.restart_button = Button(
            screen_width // 2 - 120, 430, 240, 60, "RESTART",
            color=(60, 180, 80), hover_color=(90, 210, 110)
        )

        self.menu_button = Button(
            screen_width // 2 - 120, 510, 240, 60, "MAIN MENU",
            color=(90, 120, 180), hover_color=(120, 150, 220)
        )

    def start_game(self):
        self.snake.reset()
        self.fruit.randomize(self.snake.body)  # FIX 1
        self.score = 0
        self.state = "playing"

    def update(self):
        if self.state != "playing":
            return

        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize(self.snake.body)  # FIX 1
            self.snake.add_block()
            self.snake.play_crunch_sound()
            self.score += 1

            if self.score > self.high_score:
                self.high_score = self.score
                save_high_score(self.high_score)

    def check_fail(self):
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            self.game_over()

        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def game_over(self):
        self.state = "game_over"
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def draw_grass(self):
        grass_color = pygame.Color("light green")
        for row in range(cell_number):
            if row % 2 == 0:
                for col in range(cell_number):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)
            else:
                for col in range(cell_number):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)

    def draw_score(self):
        score_text = str(self.score)
        score_surface = score_font.render(score_text, True, (56, 74, 12))  # FIX 3
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = apple.get_rect(midright=(score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, apple_rect.width + score_rect.width + 6, apple_rect.height)

        pygame.draw.rect(screen, (167, 209, 61), bg_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(apple, apple_rect)
        pygame.draw.rect(screen, (56, 74, 12), bg_rect, 2)

    def draw_menu(self):
        screen.fill((200, 220, 255))

        title = title_font.render("SNAKE", True, (30, 60, 120))
        title_rect = title.get_rect(center=(screen_width // 2, 160))
        screen.blit(title, title_rect)

        high_score_label = game_font.render(f"High Score: {self.high_score}", True, (20, 40, 70))
        high_score_rect = high_score_label.get_rect(center=(screen_width // 2, 280))
        screen.blit(high_score_label, high_score_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.start_button.draw(screen, mouse_pos)

    def draw_game_over(self):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        game_over_text = title_font.render("GAME OVER", True, (255, 70, 70))
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, 140))
        screen.blit(game_over_text, game_over_rect)

        score_text = game_font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(screen_width // 2, 230))
        screen.blit(score_text, score_rect)

        high_score_text = game_font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(center=(screen_width // 2, 290))
        screen.blit(high_score_text, high_score_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.draw(screen, mouse_pos)
        self.menu_button.draw(screen, mouse_pos)

    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                # FIX 5: compare against last_move (what the snake really did),
                # not direction (which can change several times within one tick)
                if event.key == pygame.K_UP:
                    if self.snake.last_move.y != 1:
                        self.snake.direction = Vector2(0, -1)
                if event.key == pygame.K_RIGHT:
                    if self.snake.last_move.x != -1:
                        self.snake.direction = Vector2(1, 0)
                if event.key == pygame.K_DOWN:
                    if self.snake.last_move.y != -1:
                        self.snake.direction = Vector2(0, 1)
                if event.key == pygame.K_LEFT:
                    if self.snake.last_move.x != 1:
                        self.snake.direction = Vector2(-1, 0)

        if self.state == "menu" and self.start_button.clicked(event):
            self.start_game()

        if self.state == "game_over":
            if self.restart_button.clicked(event):
                self.start_game()
            if self.menu_button.clicked(event):
                self.state = "menu"


SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150)

main_game = MAIN()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SCREEN_UPDATE and main_game.state == "playing":
            main_game.update()

        main_game.handle_events(event)




    screen.fill(pygame.Color("light cyan"))

    if main_game.state == "menu":
        main_game.draw_menu()

    elif main_game.state == "playing":
        main_game.draw_elements()

    elif main_game.state == "game_over":
        main_game.draw_elements()
        main_game.draw_game_over()

    pygame.display.update()
    clock.tick(60)
