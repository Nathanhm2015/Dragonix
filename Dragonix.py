import pygame
import sys
import random

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
dragon = pygame.Rect(120, 420, 40, 40)
vy = 0
GRAVITY = 0.5
JUMP_STRENGTH = 14
MAX_FALL = 10
on_ground = False
vel = 4
level = 1
peaches_eaten = 0
required_peaches = {1: 2, 2: 3}
GROWTH = 6
tail = []
tail_size = 20

# MELOCOTÓN
peach = pygame.Rect(540, 225, 35, 35)

# PAREDES DEL NIVEL
walls = [
    pygame.Rect(50, 460, 700, 30),   
    pygame.Rect(50, 200, 30, 260),   
    pygame.Rect(720, 200, 30, 260),  
    pygame.Rect(300, 340, 200, 20), 
    pygame.Rect(520, 260, 120, 20),  
]

# ANIMACIÓN
blink = 0
mouth = 0
moving = False


def move_collision(rect, dx, vy):
    """Movimiento con colisiones simples. Acepta velocidad vertical y devuelve (vy, on_ground)."""
    rect.x += dx
    for w in walls:
        if rect.colliderect(w):
            if dx > 0:
                rect.right = w.left
            if dx < 0:
                rect.left = w.right

    rect.y += int(vy)
    on_ground = False
    for w in walls:
        if rect.colliderect(w):
            if vy > 0:
                rect.bottom = w.top
                vy = 0
                on_ground = True
            elif vy < 0:
                rect.top = w.bottom
                vy = 0

    return vy, on_ground


def draw_dragon():
    global blink, mouth

    # cuadro pequeño detrás del dragón (decoración inicial)
    back_box = pygame.Rect(dragon.x - 12, dragon.y + dragon.height - 18, 12, 12)
    pygame.draw.rect(screen, (200, 80, 50), back_box)

    # triángulo pequeño (como una aleta o pico) delante del dragón
    tri_x = dragon.x + dragon.width
    tri_y = dragon.y + dragon.height // 2
    pygame.draw.polygon(screen, (255, 200, 0), [(tri_x, tri_y - 6), (tri_x + 10, tri_y), (tri_x, tri_y + 6)])

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


def load_level(n):
    """Carga configuración de niveles. n=1 (fácil) o n=2 (más difícil)."""
    global walls, dragon, peach, vel, vy, on_ground, JUMP_STRENGTH
    if n == 1:
        # crear un gran gap al inicio: dos plataformas separadas
        walls = [
            pygame.Rect(50, 460, 220, 30),    # suelo izquierdo
            pygame.Rect(520, 460, 230, 30),   # suelo derecho (gap en el medio)
            pygame.Rect(140, 380, 120, 20),   # plataforma inicial pequeña donde empieza el dragón
            pygame.Rect(560, 300, 120, 20),   # plataforma lejana con melocotón
            pygame.Rect(50, 200, 30, 260),    # pared izquierda
            pygame.Rect(760, 200, 30, 260),   # pared derecha
        ]
        dragon.x, dragon.y = 160, 350
        peach.x, peach.y = 590, 268
        vel = 4
        JUMP_STRENGTH = JUMP_STRENGTH
    elif n == 2:
        walls = [
            pygame.Rect(50, 460, 700, 30),
            pygame.Rect(50, 300, 30, 160),
            # gran separación: plataforma izquierda y plataforma con melocotón a la derecha
            pygame.Rect(140, 420, 200, 20),  # pequeña plataforma inicial
            pygame.Rect(520, 300, 120, 20),  # plataforma lejana (requiere gran salto)
            pygame.Rect(720, 260, 30, 240),
        ]
        dragon.x, dragon.y = 80, 420
        peach.x, peach.y = 560, 270
        vel = 4
        # mantener la misma fuerza de salto para más reto
    vy = 0
    on_ground = False
    # reiniciar contador y generar melocotón
    global peaches_eaten
    peaches_eaten = 0
    spawn_peach()
    # reset tail
    global tail
    tail = []


def spawn_peach():
    """Coloca el melocotón sobre una de las plataformas (no en el suelo)."""
    global peach
    # plataformas candidatas: anchas y no el suelo (top suficientemente alto)
    candidates = [w for w in walls if w.width >= 50 and w.top < HEIGHT - 120]
    if not candidates:
        # fallback: colocarlo en la posición por defecto
        peach.x, peach.y = 540, 225
        return
    p = random.choice(candidates)
    # colocar melocotón centrado en parte de la plataforma
    x = random.randint(p.left + 5, max(p.right - 40, p.left + 5))
    peach.x = x
    peach.y = p.top - peach.height


# cargar nivel inicial
load_level(level)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    keys = pygame.key.get_pressed()

    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * vel
    # guardar posición previa para la cola
    prev_pos = (dragon.x, dragon.y)

    # salto si está en suelo
    if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
        vy = -JUMP_STRENGTH

    # aplicar gravedad
    vy += GRAVITY
    if vy > MAX_FALL:
        vy = MAX_FALL

    moving = (dx != 0 or int(vy) != 0)

    vy, on_ground = move_collision(dragon, dx, vy)

    # si está en nivel 2 y cae fuera de la ventana -> muere (reinicia nivel 2)
    if level == 2 and dragon.top > HEIGHT:
        screen.fill(NEGRO)
        font = pygame.font.SysFont(None, 70)
        t = font.render("¡Perdiste!", True, (255, 0, 0))
        screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 40))
        pygame.display.update()
        pygame.time.wait(1000)
        load_level(2)
        continue

    # DIBUJAR
    screen.fill(AZUL)

    for w in walls:
        pygame.draw.rect(screen, MARRON, w)

    # Melocotón
    pygame.draw.circle(screen, DURAZNO, (peach.x + 18, peach.y + 18), 18)
    pygame.draw.line(screen, VERDE, (peach.x+20, peach.y+5), (peach.x+25, peach.y-8), 4)

    # actualizar cola: insertar la posición previa como segmento
    if peaches_eaten > 0:
        tail.insert(0, pygame.Rect(prev_pos[0] - tail_size//2, prev_pos[1], tail_size, tail_size))
        if len(tail) > peaches_eaten:
            tail.pop()

    # dibujar cola detrás del dragón
    for seg in tail:
        pygame.draw.rect(screen, (0, 80, 160), seg)

    draw_dragon()

    # Comer melocotón: crecer y reaparecer el melocotón
    if dragon.colliderect(peach):
        peaches_eaten += 1
        # aumentar tamaño manteniendo la base (bottom) y la izquierda
        base_bottom = dragon.bottom
        base_left = dragon.left
        dragon.width += GROWTH
        dragon.height += GROWTH
        dragon.left = base_left
        dragon.bottom = base_bottom

        # breve animación / pausa al comer
        for w in walls:
            pygame.draw.rect(screen, MARRON, w)
        draw_dragon()
        pygame.display.update()
        pygame.time.wait(200)

        spawn_peach()

        # comprobar si alcanzó la meta de melocotones para avanzar
        if peaches_eaten >= required_peaches.get(level, 1):
            pygame.time.wait(200)
            if level == 1:
                level = 2
                screen.fill(NEGRO)
                font2 = pygame.font.SysFont(None, 50)
                t2 = font2.render("Nivel 2", True, (255, 255, 255))
                screen.blit(t2, (WIDTH//2 - 70, HEIGHT//2 - 25))
                pygame.display.update()
                pygame.time.wait(1000)
                load_level(2)
                continue
            else:
                screen.fill(NEGRO)
                font = pygame.font.SysFont(None, 70)
                t = font.render("¡Ganaste!", True, (255, 255, 255))
                screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 40))
                pygame.display.update()
                pygame.time.wait(1000)
                sys.exit()

    pygame.display.update()
    clock.tick(60)
