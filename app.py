import pygame
import random
from flask import Flask, render_template, send_file, Response
import io
import threading
import time
import os

app = Flask(__name__)

# Инициализация Pygame
pygame.init()

# Настройка экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Цвета
WHITE = (255, 255, 255)

# Создание экрана Pygame
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

# Функция для сохранения текущего экрана в поток
def get_screen_image():
    image_io = io.BytesIO()
    pygame.image.save(screen, image_io, "JPEG")
    image_io.seek(0)
    return image_io

# Основной игровой цикл в отдельном потоке
def main_game_loop():
    global current_apple, apple_rect
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        screen.blit(current_apple["image"], apple_rect)
        display.blit(screen, (0, 0))
        pygame.display.flip()

        # Задержка для управления скоростью обновления экрана
        time.sleep(0.1)

# Запускаем игровой цикл в отдельном потоке
threading.Thread(target=main_game_loop, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screen')
def screen_image():
    return send_file(get_screen_image(), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)

