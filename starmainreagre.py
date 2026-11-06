import os
import sys
import math
import pygame

def generate_3d_star():
    """Математическая генерация вершин и граней объемной 5-конечной звезды"""
    vertices = []
    faces = []
    
    r_out = 1.8  # Радиус внешних лучей
    r_in = 0.7   # Радиус внутренних впадин
    height = 0.5 # Толщина звезды

    vertices.append([0.0, 0.0, height])  
    vertices.append([0.0, 0.0, -height]) 

    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        vertices.append([x, y, 0.0]) 

    for i in range(10):
        next_i = (i + 1) % 10 + 2
        curr_i = i + 2
        faces.append([0, curr_i, next_i])
        faces.append([1, next_i, curr_i])

    return vertices, faces

# 1. Геометрия
vertices, faces = generate_3d_star()

# 2. Инициализация Pygame с изменяемым размером окна
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ASCII 3D Star — Mouse Controlled")
clock = pygame.time.Clock()

FONT_SIZE = 12
font = pygame.font.SysFont('Courier New', FONT_SIZE, bold=True)

SCALE = 80          
DISTANCE = 5.0      

# Углы вращения
A = 0.0  # Авто-вращение по оси X
B = 0.0  # Управление мышкой по оси Y

ASCII_CHARS = ".,-~:;=!*#$@"

running = True
while running:
    clock.tick(60)
    screen.fill((10, 10, 18)) # Темно-космический фон
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                running = False

    # === УПРАВЛЕНИЕ МЫШКОЙ ВМЕСТО АРДУИНО ===
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Переводим позицию курсора на экране в угол поворота от 0 до 2*PI
    B = (mouse_x / WIDTH) * (2.0 * math.pi)
    # Опционально: можно привязать и ось X ко второй координате мыши,
    # но пока оставим авто-вращение + ручной сдвиг:
    A_offset = (mouse_y / HEIGHT) * (2.0 * math.pi)

    A += 0.01 # Постоянное базовое вращение
    current_A = A + A_offset
    
    sinA, cosA = math.sin(current_A), math.cos(current_A)
    sinB, cosB = math.sin(B), math.cos(B)
    
    # Расчет адаптивной сетки под размер окна
    cols = max(1, WIDTH // (FONT_SIZE - 4))
    rows = max(1, HEIGHT // FONT_SIZE)
    
    char_buffer = [[" " for _ in range(rows)] for _ in range(cols)]
    z_buffer = [[0.0 for _ in range(rows)] for _ in range(cols)]
    color_buffer = [[(0,0,0) for _ in range(rows)] for _ in range(cols)]

    # Рендеринг граней звезды
    for face in faces:
        if len(face) < 3:
            continue
            
        v1 = vertices[face[0]]
        v2 = vertices[face[1]]
        v3 = vertices[face[2]]
        
        v1_vec = pygame.math.Vector3(v1[0], v1[1], v1[2])
        v2_vec = pygame.math.Vector3(v2[0], v2[1], v2[2])
        v3_vec = pygame.math.Vector3(v3[0], v3[1], v3[2])
        
        steps = 12
        for k in range(steps + 1):
            t1 = k / steps
            for j in range(steps - k + 1):
                t2 = j / steps
                t3 = 1.0 - t1 - t2
                
                p = v1_vec * t1 + v2_vec * t2 + v3_vec * t3
                x, y, z = p.x, p.y, p.z
                
                # Вращение
                y1 = y * cosA - z * sinA
                z1 = y * sinA + z * cosA
                x2 = x * cosB + z1 * sinB
                z2 = -x * sinB + z1 * cosB
                y2 = y1
                
                ooz = 1 / (z2 + DISTANCE)
                xp = int(cols / 2 + x2 * SCALE * ooz * 1.5)
                yp = int(rows / 2 - y2 * SCALE * ooz) 
                
                if 0 <= xp < cols and 0 <= yp < rows:
                    if ooz > z_buffer[xp][yp]:
                        z_buffer[xp][yp] = ooz
                        
                        luminance_idx = int((z2 + 1.5) / 3 * (len(ASCII_CHARS) - 1))
                        luminance_idx = max(0, min(len(ASCII_CHARS) - 1, luminance_idx))
                        
                        char_buffer[xp][yp] = ASCII_CHARS[luminance_idx]
                        # Золотистый неоновый градиент
                        color_buffer[xp][yp] = (255, int(190 + luminance_idx * 5), 40)

    # Отрисовка символьной матрицы на экран
    for x in range(cols):
        for y in range(rows):
            if char_buffer[x][y] != " ":
                char_surface = font.render(char_buffer[x][y], True, color_buffer[x][y])
                screen.blit(char_surface, (x * (FONT_SIZE - 4), y * FONT_SIZE))

    pygame.display.flip()

pygame.quit()
sys.exit()



