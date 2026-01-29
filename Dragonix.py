import pygame
import sys

# `SimpleNamespace` está disponible en Python >=3.3; proporcionar fallback por compatibilidad
try:
    from types import SimpleNamespace
except Exception:
    class SimpleNamespace:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

pygame.init()
pygame.font.init()

# VENTANA
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

DEBUG = True

# Estado de teclado persistente (usarlo como `keyboard.right/left/...`)
keyboard = SimpleNamespace(right=False, left=False, up=False, down=False, space=False)

def debug_overlay(info_lines):
    """Dibuja líneas de depuración en la esquina superior izquierda."""
    global DEBUG
    if not DEBUG:
        return
    try:
        font = pygame.font.SysFont(None, 20)
        pad = 6
        # calcular tamaño del fondo (forzar a str por compatibilidad)
        widths = []
        for line in info_lines:
            try:
                widths.append(font.size(str(line))[0])
            except Exception:
                widths.append(0)
        if not widths:
            return
        w = max(widths) + pad * 2
        line_h = font.get_linesize() or 18
        h = (line_h * len(info_lines)) + pad * 2
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        screen.blit(s, (8, 8))
        y = 8 + pad
        for line in info_lines:
            try:
                t = font.render(str(line), True, (255, 255, 255))
                screen.blit(t, (8 + pad, y))
            except Exception:
                pass
            y += line_h
    except Exception:
        # Si cualquier cosa falla en el overlay, desactivar DEBUG para evitar bucles de error
        DEBUG = False
        return


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
# Historial de posiciones para cola tipo 'snake'
history = []
HISTORY_SPACING = 6
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
def show_message(text, duration_ms=500, font_size=50, bg_color=NEGRO, text_color=(255,255,255)):
    """Muestra un mensaje durante `duration_ms` milisegundos sin usar bloqueos largos."""
    start = pygame.time.get_ticks()
    font = pygame.font.SysFont(None, font_size)
    # permitir que la pausa procese eventos de teclado y actualice `keyboard`
    global keyboard
    try:
        while pygame.time.get_ticks() - start < duration_ms:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    # limpiar estado de teclado antes de salir
                    try:
                        keyboard.right = keyboard.left = keyboard.up = keyboard.down = keyboard.space = False
                    except Exception:
                        pass
                    return 'quit'
                # Propagar eventos de teclado al estado persistente para evitar "teclas pegadas"
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RIGHT:
                        keyboard.right = True
                    if ev.key == pygame.K_LEFT:
                        keyboard.left = True
                    if ev.key == pygame.K_UP:
                        keyboard.up = True
                    if ev.key == pygame.K_DOWN:
                        keyboard.down = True
                    if ev.key == pygame.K_SPACE:
                        keyboard.space = True
                if ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_RIGHT:
                        keyboard.right = False
                    if ev.key == pygame.K_LEFT:
                        keyboard.left = False
                    if ev.key == pygame.K_UP:
                        keyboard.up = False
                    if ev.key == pygame.K_DOWN:
                        keyboard.down = False
                    if ev.key == pygame.K_SPACE:
                        keyboard.space = False

            screen.fill(bg_color)
            # Evitar renderizar cadenas vacías (pueden producir superficies 0x0 en algunos backends web)
            if text:
                try:
                    t = font.render(text, True, text_color)
                    if t.get_width() > 0 and t.get_height() > 0:
                        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - t.get_height()//2))
                except Exception:
                    pass
            pygame.display.update()
            clock.tick(60)
    finally:
        # Al salir de la pausa, limpiar el estado de teclas para evitar estados pegados
        try:
            keyboard.right = keyboard.left = keyboard.up = keyboard.down = keyboard.space = False
        except Exception:
            pass
    return None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        # Actualizar estado del teclado por eventos para compatibilidad con entornos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                keyboard.right = True
            if event.key == pygame.K_LEFT:
                keyboard.left = True
            if event.key == pygame.K_UP:
                keyboard.up = True
            if event.key == pygame.K_DOWN:
                keyboard.down = True
            if event.key == pygame.K_SPACE:
                keyboard.space = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                keyboard.right = False
            if event.key == pygame.K_LEFT:
                keyboard.left = False
            if event.key == pygame.K_UP:
                keyboard.up = False
            if event.key == pygame.K_DOWN:
                keyboard.down = False
            if event.key == pygame.K_SPACE:
                keyboard.space = False

    # Calcular dx usando el estado `keyboard` (forzar int para evitar tipos raros)
    dx = ((1 if keyboard.right else 0) - (1 if keyboard.left else 0)) * vel

    # salto (solo si está en el suelo)
    if (keyboard.up or keyboard.space) and on_ground:
        vy = -JUMP_STRENGTH

    # aplicar gravedad
    vy += GRAVITY
    if vy > MAX_FALL:
        vy = MAX_FALL

    # permitir bajar más rápido con flecha abajo
    if keyboard.down:
        vy += 1

    # mover con colisiones; move_collision devuelve si aterrizó en esta iteración
    landed = move_collision(dragon, int(dx), int(vy))
    if landed:
        vy = 0
        on_ground = True
    else:
        on_ground = False

    moving = (dx != 0 or int(vy) != 0)

    # Guardar el centro del jugador en el historial (para la cola)
    try:
        history.append((dragon.centerx, dragon.centery))
    except Exception:
        history.append((int(dragon.centerx), int(dragon.centery)))
    # limitar el tamaño del historial para no crecer indefinidamente
    max_history = (len(squares) + 5) * HISTORY_SPACING
    if len(history) > max_history:
        del history[0: len(history) - max_history]

    # Si cae fuera de la pantalla
    if dragon.top > HEIGHT:
        if level == 3:
            # respawn en el círculo rojo con un salto grande
            dragon.x, dragon.y = spawn_point
            vy = -18
            screen.fill(NEGRO)
            res = show_message("¡Cuidado! Reiniciando...", duration_ms=400, font_size=40)
            if res == 'quit':
                running = False
                break
            continue
        else:
            # reiniciar el nivel actual
            if level == 1:
                load_easy_level()
            elif level == 2:
                load_level_attachment()
            else:
                load_level_three()
            # limpiar estado de teclado para evitar teclas pegadas tras el reinicio
            try:
                keyboard.right = keyboard.left = keyboard.up = keyboard.down = keyboard.space = False
            except Exception:
                pass
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
    # dibujar cuadrados ganados - intentar seguir el `history` (cola tipo 'snake')
    SQUARE_SPACING = 4
    for i, sq in enumerate(squares):
        # calcular índice en el historial para este segmento (espaciado por HISTORY_SPACING)
        hist_index = len(history) - (i + 1) * HISTORY_SPACING
        if hist_index >= 0:
            # tomar la posición guardada en el historial
            pos = history[hist_index]
            try:
                sq.center = (int(pos[0]), int(pos[1]))
            except Exception:
                sq.center = (int(pos[0]), int(pos[1]))
        else:
            # fallback: posicionarlos a la izquierda del jugador (comportamiento previo)
            x = dragon.left - (i + 1) * (sq.width + SQUARE_SPACING)
            y = dragon.bottom - sq.height
            sq.topleft = (int(x), int(y))

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

    draw_dragon()

    # Comer melocotón: añadir cuadrado y avanzar niveles/ganar
    if dragon.colliderect(peach):
        new_sq = pygame.Rect(0, 0, dragon.width, dragon.height)
        # Colocar el nuevo segmento inmediatamente a la izquierda del jugador
        try:
            new_sq.topleft = (dragon.left - new_sq.width - 4, dragon.bottom - new_sq.height)
        except Exception:
            new_sq.topleft = (int(dragon.left - new_sq.width - 4), int(dragon.bottom - new_sq.height))
        # Insertar al inicio de la lista para que el nuevo segmento quede junto al jugador
        squares.insert(0, new_sq)
        pygame.display.update()
        res = show_message("", duration_ms=300, font_size=1)  # breve pausa no bloqueante
        if res == 'quit':
            running = False
            break

        if level == 1:
            load_level_attachment()
            continue
        elif level == 2:
            load_level_three()
            continue
        else:
            screen.fill(NEGRO)
            font = pygame.font.SysFont(None, 70)
            t = font.render("¡Ganaste!", True, (255, 255, 255))
            screen.blit(t, (WIDTH//2 - 150, HEIGHT//2 - 40))
            pygame.display.update()
            res = show_message("¡Ganaste!", duration_ms=1500, font_size=70)
            running = False
            break

    # Capa de depuración (muestra dx, vy, teclas, posición)
    try:
        keys_state = "L:{0} R:{1} U:{2} D:{3} S:{4}".format(int(keyboard.left), int(keyboard.right), int(keyboard.up), int(keyboard.down), int(keyboard.space))
    except Exception:
        keys_state = "keys: ?"
    info = [
        "dx={0}".format(dx),
        "vy={0:.2f}".format(vy),
        "pos=({0},{1})".format(dragon.x, dragon.y),
        "on_ground={0}".format(on_ground),
        keys_state,
        "level={0}".format(level),
    ]
    # Añadir info de los primeros cuadrados para depuración
    try:
        for i, sq in enumerate(squares[:3]):
            info.append("sq{0}=({1},{2})".format(i, sq.x, sq.y))
        info.append("dragon.left={0} top={1} bottom={2}".format(dragon.left, dragon.top, dragon.bottom))
    except Exception:
        pass
    debug_overlay(info)
    pygame.display.update()
    clock.tick(60)
