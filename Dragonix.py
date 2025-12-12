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
vel = 4

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
    for w in walls:
        if rect.colliderect(w):
            if dy > 0:
                rect.bottom = w.top
            if dy < 0:
                rect.top = w.bottom


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
    dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * vel

    moving = (dx != 0 or dy != 0)

    move_collision(dragon, dx, dy)

    # DIBUJAR
    screen.fill(AZUL)

    for w in walls:
        pygame.draw.rect(screen, MARRON, w)

    # Melocotón
    pygame.draw.circle(screen, DURAZNO, (peach.x + 18, peach.y + 18), 18)
    pygame.draw.line(screen, VERDE, (peach.x+20, peach.y+5), (peach.x+25, peach.y-8), 4)

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
