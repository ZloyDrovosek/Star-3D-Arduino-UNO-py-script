import os
import sys
import time
import math
import pygame
import serial
import serial.tools.list_ports

BAUD_RATE = 115200

def select_com_port():
    print("\n=== ПОИСК УСТРОЙСТВ ===")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("❌ Компьютер не видит ни одного COM-порта! Проверь USB-кабель.")
        input("Нажми Enter для выхода...")
        sys.exit()
    print("Доступные порты:")
    for i, port in enumerate(ports):
        print(f" [{i}] {port.device} — {port.description}")
    while True:
        try:
            choice = int(input("\nВведите номер端口 для подключения Arduino: "))
            if 0 <= choice < len(ports):
                target_port = ports[choice].device
                ser = serial.Serial(target_port, BAUD_RATE, timeout=0.1)
                time.sleep(2)
                print("✅ Успешно сопряжено!")
                return ser
        except Exception:
            print("Ошибка подключения. Попробуй еще раз.")

def generate_3d_star():
    vertices = []
    faces = []
    
    r_out = 1.8  
    r_in = 0.7   
    height = 0.5 

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

# 1. Инициализация связи и геометрии
arduino_serial = select_com_port()
vertices, faces = generate_3d_star()

# 2. Инициализация Pygame с поддержкой изменения размеров окна
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ASCII 3D Star — Resizable Window")
clock = pygame.time.Clock()

FONT_SIZE = 12
font = pygame.font.SysFont('Courier New', FONT_SIZE, bold=True)

SCALE = 80          
DISTANCE = 5.0      
A = 0.0  
B = 0.0  

ASCII_CHARS = ".,-~:;=!*#$@"

running = True
while running:
    clock.tick(60)
    screen.fill((10, 10, 18)) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                running = False

    if arduino_serial.in_waiting > 0: 
        try:
            line = arduino_serial.readline().decode('utf-8').strip()
            if line:
                B = float(line)
        except Exception:
            pass

    A += 0.015 
    
    sinA, cosA = math.sin(A), math.cos(A)
    sinB, cosB = math.sin(B), math.cos(B)
    
    cols = max(1, WIDTH // (FONT_SIZE - 4))
    rows = max(1, HEIGHT // FONT_SIZE)
    
    char_buffer = [[" " for _ in range(rows)] for _ in range(cols)]
    z_buffer = [[0.0 for _ in range(rows)] for _ in range(cols)]
    color_buffer = [[(0,0,0) for _ in range(rows)] for _ in range(cols)]

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
                        color_buffer[xp][yp] = (255, int(190 + luminance_idx * 5), 40)

    for x in range(cols):
        for y in range(rows):
            if char_buffer[x][y] != " ":
                char_surface = font.render(char_buffer[x][y], True, color_buffer[x][y])
                screen.blit(char_surface, (x * (FONT_SIZE - 4), y * FONT_SIZE))

    pygame.display.flip()

arduino_serial.close()
pygame.quit()
sys.exit()


