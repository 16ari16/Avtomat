import pygame
import random

# Настройки
WIDTH, HEIGHT = 800, 600
FPS = 60
BLUE = (0,0,255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Играт")
clock = pygame.time.Clock()

# Игрок
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 250))
        self.speed = 5

    def update(self, move_left, move_right):
        if move_left and self.rect.left > 100:
            self.rect.x -= self.speed
        if move_right and self.rect.right < 700:
            self.rect.x += self.speed

# Враги
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(100, 700), random.randint(-100, -40)))
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom >= 400:
            global lives
            lives -= 1
            self.kill()

# Монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, value=10):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        pygame.draw.circle(self.image, YELLOW, (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value
        self.animation = False
        self.returning = False
        self.target = (700, 500)
        self.start_pos = (x, y)

    def start_animation(self, target):
        self.animation = True
        self.target = target

    def return_animation(self):
        self.returning = True
        self.target = self.start_pos

    def update(self):
        if self.animation:
            speed = 5
            if self.rect.x < self.target[0]:
                self.rect.x += speed
            if self.rect.y < self.target[1]:
                self.rect.y += speed
            if self.rect.x >= self.target[0] and self.rect.y >= self.target[1]:
                self.animation = False
                self.kill()

        elif self.returning:
            speed = 5
            if self.rect.x > self.target[0]:
                self.rect.x -= speed
            if self.rect.y > self.target[1]:
                self.rect.y -= speed
            if self.rect.x <= self.target[0] and self.rect.y <= self.target[1]:
                self.returning = False

# Логика автомата
class ArcadeMachine:
    def __init__(self):
        self.balance = 100
        self.cost = 50

    def add_coin(self, value):
        self.balance += value

    def can_play(self):
        return self.balance >= self.cost

    def give_change(self):
        change = self.balance
        self.balance = 0
        return change

# Кнопки
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

# Инициализация игровых объектов
player = Player()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group([player])
arcade_machine = ArcadeMachine()

# Монеты для оплаты
coins = pygame.sprite.Group([Coin(50 + i * 50 + 15, HEIGHT - 80 - 15) for i in range(5)])

# Кнопки управления
move_left = False
move_right = False

def left_button_action():
    global move_left
    move_left = True

def right_button_action():
    global move_right
    move_right = True

def stop_left():
    global move_left
    move_left = False

def stop_right():
    global move_right
    move_right = False

# Логика выдачи сдачи
def give_change_action():
    change = arcade_machine.give_change()
    for i in range(change // 10):
        coin = Coin(700, 500)
        coin.return_animation()
        coins.add(coin)

# Кнопки интерфейса
left_button = Button(100, HEIGHT - 60, 100, 50, "Left", left_button_action)
right_button = Button(250, HEIGHT - 60, 100, 50, "Right", right_button_action)
change_button = Button(600, HEIGHT - 60, 185, 50, "Выдать сдачу", give_change_action)

# Логика конца игры
lives = 3
score = 0
game_over = False
animation_complete = True

def check_game_over():
    global lives, game_over
    if lives <= 0:
        arcade_machine.balance -= arcade_machine.cost  # Вычитаем 50 из баланса
        if arcade_machine.balance < arcade_machine.cost:  # Если баланс меньше 50
            game_over = True  # Заканчиваем игру
        else:
            restart_game()

def draw_game_over_message():
    pygame.draw.rect(screen, WHITE, (100, 100, 600, 300))
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, BLACK)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(game_over_text, text_rect)

def restart_game():
    global lives, score, enemies, all_sprites, player, game_over
    lives = 3
    score = 0
    enemies.empty()  # Очищаем врагов
    all_sprites.empty()  # Очищаем все спрайты
    all_sprites.add(player)  # Добавляем игрока обратно
    game_over = False

# Главный игровой цикл
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            stop_left()
            stop_right()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for coin in coins:
                if coin.rect.collidepoint(event.pos) and not coin.animation and not coin.returning:
                    coin.start_animation((700, 500))
                    arcade_machine.add_coin(coin.value)
                    animation_complete = False
                    break

            left_button.is_clicked(event)
            right_button.is_clicked(event)
            change_button.is_clicked(event)

    if all(not coin.animation and not coin.returning for coin in coins):
        animation_complete = True

    # Если игра не началась
    if not game_over and arcade_machine.can_play() and animation_complete:
        if len(enemies) < 5:
            if random.randint(1, 100) <= 10:
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)

    # Проверяем столкновение игрока с врагами
    hits = pygame.sprite.spritecollide(player, enemies, True)
    if hits:
        score += 1

    if arcade_machine.can_play() and game_over:
        restart_game()

    # Обновляем объекты
    if not game_over:
        player.update(move_left, move_right)
        enemies.update()
        check_game_over()

    # Рендеринг
    screen.fill(BLACK)

    pygame.draw.rect(screen, BLUE, (50, 50, 700, 500), 5)
    pygame.draw.rect(screen, WHITE, (100, 100, 600, 300))
    pygame.draw.rect(screen, GRAY, (680, 500, 50, 30))

    coins.update()
    coins.draw(screen)

    if not game_over:
        all_sprites.draw(screen)

    font = pygame.font.Font(None, 36)
    balance_text = font.render(f'Balance: {arcade_machine.balance} руб', True, WHITE)
    lives_text = font.render(f'Lives: {lives}', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)

    screen.blit(balance_text, (120, 420))
    screen.blit(lives_text, (120, 450))
    screen.blit(score_text, (120,480))

    # Отрисовка кнопок
    left_button.draw(screen)
    right_button.draw(screen)
    change_button.draw(screen)

    # Если игра окончена, выводим сообщение
    if game_over:
        draw_game_over_message()

    # Обновляем экран
    pygame.display.flip()

# Закрытие Pygame
pygame.quit()
