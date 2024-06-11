import pygame
import sys
import json
import random

# Инициализация Pygame
pygame.init()

# Настройка экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Apples")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)

# Шрифт
font = pygame.font.SysFont(None, 30)

# Счетчик и ранги
score = 0
ranks = {
    "Newbie": 0,
    "Apple Finder": 25000,
    "Apple Lover": 75000
}
current_rank = "Newbie"

# Файл для сохранения и загрузки счета
SCORE_FILE = "score.json"

# Класс для управления инвентарем
class Inventory:
    def __init__(self):
        self.apples_count = 0

    def add_apples(self, amount):
        self.apples_count += amount

    def get_apples_count(self):
        return self.apples_count

# Создаем объект инвентаря
inventory = Inventory()

# Загрузка счета из файла (если он существует)
try:
    with open(SCORE_FILE, "r") as file:
        score_data = json.load(file)
        score = score_data.get("score", 0)
        inventory.apples_count = score_data.get("apples_inventory", 0)
except FileNotFoundError:
    score_data = {}

# Количество яблок в инвентаре
apples_inventory = 0

# Загрузка и уменьшение изображения яблок
apple_image = pygame.image.load('apple.png')
golden_apple_image = pygame.image.load('golden_apple.png')
APPLE_WIDTH, APPLE_HEIGHT = 100, 100  # Новый размер яблока
apple_image = pygame.transform.scale(apple_image, (APPLE_WIDTH, APPLE_HEIGHT))
golden_apple_image = pygame.transform.scale(golden_apple_image, (APPLE_WIDTH, APPLE_HEIGHT))

# Список яблок с шансами появления
apples = [
    {"image": apple_image, "points": 1, "chance": 0.9},
    {"image": golden_apple_image, "points": 5, "chance": 0.1}
]

def choose_apple():
    return random.choices(apples, weights=[apple["chance"] for apple in apples])[0]

current_apple = choose_apple()
apple_rect = current_apple["image"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Звуковой эффект для клика
click_sound = pygame.mixer.Sound('click.wav')

# Класс для объекта "1"
class NumberOne(pygame.sprite.Sprite):
    def __init__(self, pos, points):
        super().__init__()
        self.image = font.render(f"+{points}", True, GRAY)  # Серый цвет
        self.rect = self.image.get_rect(center=pos)
        self.timer = 3000  # Время, в течение которого цифра будет отображаться (в миллисекундах)
        self.alpha = 255  # Начальная прозрачность

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()  # Удаляем объект из группы спрайтов
        else:
            # Обновляем прозрачность каждую миллисекунду, чтобы достичь исчезновения за 3 секунды
            self.alpha = max(0, int(self.timer / 3000 * 255))  # Рассчитываем прозрачность
            self.image.set_alpha(self.alpha)  # Устанавливаем прозрачность для изображения

# Группа спрайтов для объектов "1"
number_one_group = pygame.sprite.Group()

# Список уже использованных никнеймов
used_nicknames = []

# Функция для отображения окна ввода ника
def input_nickname():
    nickname = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if nickname not in used_nicknames:
                        input_active = False
                    else:
                        # Вывод сообщения об ошибке, если никнейм уже занят
                        nickname = ""
                        input_surface = font.render("This Nickname is already taken", True, RED)
                        screen.blit(input_surface, (SCREEN_WIDTH // 2 - input_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    nickname += event.unicode
        screen.fill(WHITE)
        text_surface = font.render("Enter your Nickname:", True, BLACK)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        input_surface = font.render(nickname, True, BLACK)
        screen.blit(input_surface, (SCREEN_WIDTH // 2 - input_surface.get_width() //
        2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
    return nickname

# Проверяем, был ли введен никнейм, и если нет, запрашиваем его
if not score_data.get("nickname"):
    nickname = input_nickname()
    score_data["nickname"] = nickname
    used_nicknames.append(nickname)
else:
    nickname = score_data["nickname"]

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Сохранение счета перед выходом из игры
            score_data["score"] = score
            score_data["apples_inventory"] = inventory.get_apples_count()
            with open(SCORE_FILE, "w") as file:
                json.dump(score_data, file)
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if apple_rect.collidepoint(event.pos):
                score += current_apple["points"]
                click_sound.play()  # Воспроизведение звука при клике
                # Добавляем объект "1" в группу спрайтов
                number_one_group.add(NumberOne(event.pos, current_apple["points"]))
                # Перемещение яблока на случайную позицию
                apple_rect.center = (random.randint(APPLE_WIDTH // 2, SCREEN_WIDTH - APPLE_WIDTH // 2), 
                                     random.randint(APPLE_HEIGHT // 2, SCREEN_HEIGHT - APPLE_HEIGHT // 2))
                # Смена типа яблока
                current_apple = choose_apple()

    # Проверка, достигнуто ли количество яблок для добавления в инвентарь
    if score >= 2000:
        # Рассчитываем количество яблок для добавления в инвентарь
        apples_to_add = score // 2000
        # Добавляем яблоки в инвентарь
        inventory.add_apples(apples_to_add)
        # Обновляем счетчик яблок, вычитая добавленные в инвентарь
        score -= apples_to_add * 2000
    
    # Определение текущего ранга и оставшегося до следующего ранга
    next_rank = None
    next_rank_threshold = None
    for rank, threshold in ranks.items():
        if score >= threshold:
            current_rank = rank
        else:
            next_rank = rank
            next_rank_threshold = threshold
            break

    # Рассчитываем прогресс к следующему рангу
    progress = 0
    if next_rank:
        progress = (score - ranks[current_rank]) / (ranks[next_rank] - ranks[current_rank])

    # Рассчитываем, сколько очков осталось до следующего яблока в инвентарь
    points_to_next_apple = 2000 - (score % 2000)

    # Отрисовка экрана
    screen.fill(WHITE)
    screen.blit(current_apple["image"], apple_rect)
    score_text = font.render(f"Apples: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    rank_text = font.render(f"Rank: {current_rank}", True, BLACK)
    screen.blit(rank_text, (10, 40))
    if next_rank:
        # Отображение текущего ранга
        current_rank_text = font.render(f"{current_rank}", True, BLACK)
        screen.blit(current_rank_text, (10, 70))  # Перенесли выше на экране

        # Отображение полосы прогресса
        pygame.draw.rect(screen, BLACK, (130, 70, 150, 20))  # Фон полосы, перенесли выше на экране
        pygame.draw.rect(screen, GREEN, (130, 70, 150 * progress, 20))  # Заполнение полосы, перенесли выше на экране

        # Отображение числа яблок для достижения следующего ранга
        next_rank_text = font.render(f"Level 1/3", True, BLACK)
        screen.blit(next_rank_text, (290, 70))  # Перенесли выше на экране

    # Отображение никнейма
    nickname_text = font.render(f"Nickname: {nickname}", True, BLACK)
    screen.blit(nickname_text, (10, 100))

    # Отображение количества очков до следующего яблока в инвентарь
    next_apple_text = font.render(f"Points to next apple: {points_to_next_apple}", True, BLACK)
    screen.blit(next_apple_text, (10, 130))

        # Обновление и отображение объектов "1"
    number_one_group.update()
    number_one_group.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()