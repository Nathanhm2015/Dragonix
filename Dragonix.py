import pygame
import sys

pygame.init()

# VENTANA
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# COLORES
AZUL = (80, 110, 255)
MARRON = (150, 90, 50)
CELESTE = (120, 200, 255)
ROSA = (255, 120, 180)
NEGRO = (0, 0, 0)
DURAZNO = (255, 180, 120)
VERDE = (0, 150, 0)

# DRAGÓN
dragon = pygame.Rect(140, 220, 40, 40)
vy = 0
GRAVITY = 0.4
JUMP_STRENGTH = 14
MAX_FALL = 10
on_ground = False
vel = 4
level = 1
peaches_eaten = 0
squares = []
spawn_point = (60, 100)  # posición aproximada del círculo rojo (ajustable)
right_marker = None
# VIDAS

# MELOCOTÓN
peach = pygame.Rect(520, 140, 35, 35)

# PAREDES DEL NIVEL
walls = [
    pygame.Rect(10, 180, 40, 200),
    
    pygame.Rect(100, 180, 40, 200),
    pygame.Rect(100, 340, 350, 40),
    pygame.Rect(410, 180, 40, 200),
    pygame.Rect(260, 140, 190, 40),
]


def load_easy_level():
    """Configura un nivel fácil: suelo amplio y una pequeña plataforma con el melocotón."""
    global walls, dragon, peach, vel
    walls = [
        pygame.Rect(40, 440, 720, 40),   # suelo ancho y visible
        pygame.Rect(140, 360, 120, 20),  # plataforma inicial
        pygame.Rect(520, 300, 120, 20),  # plataforma donde aparece el melocotón
    ]
    dragon.x, dragon.y = 160, 320
    peach.x, peach.y = 560, 268
    vel = 4


    global peaches_eaten, squares, vy, on_ground, level
    peaches_eaten = 0
    vy = 0
    on_ground = False

load_easy_level()


def load_level_attachment():
    """Nivel tipo 'attachment': paredes altas a los lados, plataforma inicial pequeña, plataforma central y plataforma derecha alta con melocotón."""
    global walls, dragon, peach, vel, peaches_eaten, squares, vy, on_ground, level
    walls = [
        pygame.Rect(10, 60, 30, 440),    # pared izquierda alta
        pygame.Rect(760, 60, 30, 440),   # pared derecha alta
        pygame.Rect(80, 420, 160, 20),   # plataforma izquierda (donde empieza)
        pygame.Rect(300, 360, 140, 20),  # plataforma media
        pygame.Rect(520, 300, 140, 20),  # plataforma derecha alta (melocotón)
    ]
    dragon.x, dragon.y = 100, 380
    peach.x, peach.y = 520 + 50, 300 - peach.height
    vel = 4
    peaches_eaten = 0
    vy = 0
    on_ground = False
    level = 2


def load_level_three():
    """Nivel 3: diseño con un gran salto que, si se falla, reinicia al jugador en el círculo rojo con un salto fuerte."""
    global walls, dragon, peach, vel, peaches_eaten, squares, vy, on_ground, level, spawn_point
    walls = [
        pygame.Rect(10, 420, 160, 24),    # plataforma izquierda (inicio, cerca del spawn)
        pygame.Rect(240, 420, 160, 24),   # plataforma central (gap entre left and right)
        pygame.Rect(480, 320, 160, 20),   # plataforma derecha alta (melocotón)
        pygame.Rect(760, 60, 30, 440),    # pared derecha alta
    ]
    # colocar dragón en la izquierda baja (cerca del círculo rojo)
    # alinear bottom con la plataforma izquierda
    dragon.x = 40
    dragon.bottom = walls[0].top
    # colocar melocotón sobre la plataforma derecha alta
    peach.x = walls[2].left + 40
    peach.y = walls[2].top - peach.height
    vel = 4
    peaches_eaten = 0
    vy = 0
    on_ground = False
    level = 3
    # marcador cuadrado a la derecha de la plataforma (como en tu boceto)
    global right_marker
    right_marker = pygame.Rect(walls[2].right + 10, walls[2].top - 24, 24, 24)

# ANIMACIÓN
blink = 0
mouth = 0
moving = False


def move_collision(rect, dx, dy):
    """Movimiento con colisiones simples"""
    rect.x += dx
    for w in walls:
        if rect.colliderect(w):
            if dx > 0:
                rect.right = w.left
            if dx < 0:
                rect.left = w.right

    rect.y += dy
    landed = False
    for w in walls:
        if rect.colliderect(w):
            if dy > 0:
                rect.bottom = w.top
                landed = True
            if dy < 0:
                rect.top = w.bottom

    return landed


def draw_dragon():
    global blink, mouth

    pygame.draw.rect(screen, CELESTE, dragon)

    # Boca animada
    if moving:
        mouth = (mouth + 1) % 20
        if mouth < 10:
            pygame.draw.rect(screen, ROSA, (dragon.x + 8, dragon.y + 18, 25, 13))
        else:
            pygame.draw.rect(screen, ROSA, (dragon.x + 8, dragon.y + 20, 25, 10))
    else:
        pygame.draw.rect(screen, ROSA, (dragon.x + 8, dragon.y + 20, 25, 10))

    # Ojos
    blink = (blink + 1) % 120
    if 5 < blink < 12:
        pygame.draw.line(screen, NEGRO, (dragon.x+15, dragon.y+15), (dragon.x+20, dragon.y+15), 3)
        pygame.draw.line(screen, NEGRO, (dragon.x+25, dragon.y+15), (dragon.x+30, dragon.y+15), 3)
    else:
        pygame.draw.circle(screen, NEGRO, (dragon.x+18, dragon.y+15), 3)
        pygame.draw.circle(screen, NEGRO, (dragon.x+28, dragon.y+15), 3)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    keys = pygame.key.get_pressed()

    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * vel

    # salto (solo si está en el suelo)
    if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
        vy = -JUMP_STRENGTH

    # aplicar gravedad
    vy += GRAVITY
    if vy > MAX_FALL:
        vy = MAX_FALL

    # permitir bajar más rápido con flecha abajo
    if keys[pygame.K_DOWN]:
        vy += 1

    # mover con colisiones; move_collision devuelve si aterrizó en esta iteración
    landed = move_collision(dragon, int(dx), int(vy))
    if landed:
        vy = 0
        on_ground = True
    else:
        on_ground = False

    moving = (dx != 0 or int(vy) != 0)

    # Si cae fuera de la pantalla
    if dragon.top > HEIGHT:
        if level == 3:
            # respawn en el círculo rojo con un salto grande
            dragon.x, dragon.y = spawn_point
            vy = -18
            screen.fill(NEGRO)
            font = pygame.font.SysFont(None, 50)
            t = font.render("¡Cuidado! Reiniciando...", True, (255, 255, 255))
            screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 25))
            pygame.display.update()
            pygame.time.wait(400)
            continue
        else:
            # reiniciar el nivel actual
            if level == 1:
                load_easy_level()
            elif level == 2:
                load_level_attachment()
            else:
                load_level_three()
            continue

    # DIBUJAR
    screen.fill(AZUL)

    for w in walls:
        pygame.draw.rect(screen, MARRON, w)

    # Melocotón
    pygame.draw.circle(screen, DURAZNO, (peach.x + 18, peach.y + 18), 18)
    pygame.draw.line(screen, VERDE, (peach.x+20, peach.y+5), (peach.x+25, peach.y-8), 4)

    # dibujar marcador derecho (solo en nivel 3)
    if level == 3 and right_marker:
        pygame.draw.rect(screen, (170, 120, 60), right_marker)

    draw_dragon()

    # dibujar cuadrados ganados (adjuntos a la izquierda del dragón, visibles)
    for i, sq in enumerate(squares):
        # posicionar junto al dragon (separados hacia la izquierda)
        off_x = (i+1) * (sq.width + 4)
        x = dragon.left - off_x
        y = dragon.bottom - sq.height
        sq.topleft = (x, y)
        pygame.draw.rect(screen, CELESTE, sq)
        # dibujar triángulo encima del cuadrado (como adorno)
        tri_h = max(6, sq.width // 4)
        tri_top = sq.top - tri_h
        tri_points = [
            (sq.centerx, tri_top),
            (sq.right, sq.top + tri_h // 2),
            (sq.left, sq.top + tri_h // 2),
        ]
        pygame.draw.polygon(screen, (0, 80, 160), tri_points)

    # Comer melocotón: añadir cuadrado y avanzar niveles
    if dragon.colliderect(peach):
        # añadir un cuadrado al dragon (mismo tamaño que el dragón)
        new_sq = pygame.Rect(0, 0, dragon.width, dragon.height)
        squares.append(new_sq)

        pygame.display.update()
        pygame.time.wait(300)

        if level == 1:
            load_level_attachment()
            continue
        elif level == 2:
            # pasar a nivel 3 (el del círculo rojo)
            load_level_three()
            continue
        else:
            screen.fill(NEGRO)
            font = pygame.font.SysFont(None, 70)
            t = font.render("¡Ganaste!", True, (255, 255, 255))
            screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 40))
            pygame.display.update()
            pygame.time.wait(1500)
            sys.exit()
    draw_dragon()

    # VICTORIA
    if dragon.colliderect(peach):
        screen.fill(NEGRO)
        font = pygame.font.SysFont(None, 70)
        t = font.render("¡Ganaste!", True, (255, 255, 255))
        screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 40))
        pygame.display.update()
        pygame.time.wait(2000)
        sys.exit()

    pygame.display.update()
    clock.tick(60)
