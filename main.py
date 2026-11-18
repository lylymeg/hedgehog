import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hedgehog & Autumn Leaves Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Automne Doux & Forêt Cosy)
BG_COLOR = (22, 18, 28)
FOREST_GROUND = (52, 36, 32)
GROUND_HIGHLIGHT = (78, 54, 44)
HEDGEHOG_BODY = (118, 76, 52)
HEDGEHOG_SPINES = (74, 46, 32)
HEDGEHOG_FACE = (232, 198, 178)
LEAF_COLORS = [
    (245, 158, 52),   # Ambre doré
    (228, 92, 46),    # Orange automnal
    (196, 56, 68),    # Rouge érable
    (238, 198, 78)    # Jaune miel
]
TEXT_COLOR = (246, 242, 248)
GRAY = (142, 136, 158)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class AutumnLeaf:
    def __init__(self, x=None, y=None, settled=False):
        self.x = float(x if x is not None else random.uniform(50, WIDTH - 50))
        self.y = float(y if y is not None else random.uniform(80, HEIGHT - 90))
        self.settled = settled
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(0.8, 1.8) if not settled else 0.0
        self.phase = random.uniform(0, math.pi * 2)
        self.color = random.choice(LEAF_COLORS)
        self.size = random.randint(7, 11)

    def update(self, mouse_pos, ground_y):
        self.phase += 0.06
        breeze = math.sin(self.phase) * 0.65

        # Légère brise autour du curseur de la souris
        if mouse_pos[1] > 80:
            dx = self.x - mouse_pos[0]
            dy = self.y - mouse_pos[1]
            dist = math.hypot(dx, dy)
            if 0 < dist < 110:
                push = (110 - dist) / 110 * 0.25
                self.vx += (dx / dist) * push
                if self.settled and random.random() < 0.08:
                    self.settled = False
                    self.vy = -1.2

        if not self.settled:
            self.x += self.vx + breeze
            self.y += self.vy
            self.vx *= 0.96
            self.x = max(35, min(WIDTH - 35, self.x))

            if self.y >= ground_y:
                self.y = ground_y
                self.vy = 0.0
                self.vx = 0.0
                self.settled = True

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        tilt = int(math.sin(self.phase) * 3)
        pygame.draw.ellipse(surface, self.color, (ix - self.size, iy - self.size // 2 + tilt, self.size * 2, self.size))
        pygame.draw.line(surface, (110, 62, 34), (ix - self.size // 2, iy + tilt), (ix + self.size // 2, iy + tilt), 1)

class Mushroom:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.cap_color = random.choice([(235, 85, 105), (240, 175, 85), (195, 125, 225)])
        self.scale = random.uniform(0.85, 1.2)

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        stem_w = int(8 * self.scale)
        stem_h = int(12 * self.scale)
        cap_w = int(22 * self.scale)
        cap_h = int(12 * self.scale)

        # Pied du champignon
        pygame.draw.rect(surface, (240, 232, 220), (ix - stem_w // 2, iy - stem_h, stem_w, stem_h), border_radius=3)
        # Chapeau
        pygame.draw.ellipse(surface, self.cap_color, (ix - cap_w // 2, iy - stem_h - cap_h // 2, cap_w, cap_h))
        # Petits points blancs
        pygame.draw.circle(surface, (255, 250, 250), (ix - 4, iy - stem_h - 1), 2)
        pygame.draw.circle(surface, (255, 250, 250), (ix + 3, iy - stem_h - 2), 2)

class Hedgehog:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.facing_right = True
        self.walk_phase = 0.0
        self.wait_timer = random.randint(40, 100)

    def pick_new_target(self, ground_top, ground_bottom):
        self.target_x = random.uniform(100, WIDTH - 100)
        self.target_y = random.uniform(ground_top + 15, ground_bottom - 10)

    def update(self, mushrooms, ground_top, ground_bottom):
        target_mush = None
        if mushrooms:
            target_mush = min(mushrooms, key=lambda m: math.hypot(m.x - self.x, m.y - self.y))
            self.target_x, self.target_y = target_mush.x, target_mush.y
        else:
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self.wait_timer = random.randint(60, 140)
                self.pick_new_target(ground_top, ground_bottom)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 5:
            self.facing_right = dx >= 0
            speed = 1.35
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            self.walk_phase += 0.2

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        bob = int(math.sin(self.walk_phase) * 1.5)
        dir_sign = 1 if self.facing_right else -1

        # Petites pattes
        step = int(math.sin(self.walk_phase) * 3)
        pygame.draw.circle(surface, HEDGEHOG_FACE, (cx - 7 + step, cy + 8), 3)
        pygame.draw.circle(surface, HEDGEHOG_FACE, (cx + 7 - step, cy + 8), 3)

        # Corps arrondi et piquants
        pygame.draw.ellipse(surface, HEDGEHOG_BODY, (cx - 18, cy - 12 + bob, 36, 22))
        for i in range(-2, 3):
            sx = cx - dir_sign * (i * 5)
            pygame.draw.polygon(surface, HEDGEHOG_SPINES, [
                (sx - 3, cy - 8 + bob),
                (sx, cy - 17 + bob),
                (sx + 3, cy - 8 + bob)
            ])

        # Museau et petit nez
        head_x = cx + dir_sign * 13
        head_y = cy - 3 + bob
        pygame.draw.ellipse(surface, HEDGEHOG_FACE, (head_x - 8, head_y - 5, 16, 12))
        pygame.draw.circle(surface, (35, 25, 30), (head_x + dir_sign * 7, head_y), 2)
        pygame.draw.circle(surface, (25, 25, 35), (head_x + dir_sign * 1, head_y - 2), 2)

# Initialisation
ground_top = HEIGHT - 165
ground_bottom = HEIGHT - 35

hedgehog = Hedgehog(WIDTH // 2, HEIGHT - 95)
leaves = [AutumnLeaf(settled=True) for _ in range(32)]
mushrooms = [Mushroom(WIDTH // 2 - 130, HEIGHT - 85)]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 80:
                for _ in range(8):
                    lx = mouse_pos[0] + random.randint(-35, 35)
                    ly = max(85, mouse_pos[1] + random.randint(-20, 20))
                    leaves.append(AutumnLeaf(lx, ly, settled=False))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                mx = random.randint(90, WIDTH - 90)
                my = random.randint(ground_top + 15, ground_bottom - 10)
                mushrooms.append(Mushroom(mx, my))
            elif event.key == pygame.K_r:
                leaves = [AutumnLeaf(settled=True) for _ in range(25)]
                mushrooms = []
                hedgehog = Hedgehog(WIDTH // 2, HEIGHT - 95)

    # Faire tomber doucement de nouvelles feuilles
    if len(leaves) < 65 and random.random() < 0.25:
        leaves.append(AutumnLeaf(x=random.uniform(40, WIDTH - 40), y=80, settled=False))

    for leaf in leaves:
        floor_target = random.randint(ground_top + 8, ground_bottom)
        leaf.update(mouse_pos, floor_target)

    hedgehog.update(mushrooms, ground_top, ground_bottom)

    # --- RENDU GRAPHIQUE ---
    screen.fill(BG_COLOR)

    # Sol forestier d'automne
    pygame.draw.rect(screen, FOREST_GROUND, (0, ground_top, WIDTH, HEIGHT - ground_top))
    pygame.draw.line(screen, GROUND_HIGHLIGHT, (0, ground_top), (WIDTH, ground_top), 3)

    # Feuilles tombées
    for leaf in leaves:
        leaf.draw(screen)

    # Champignons
    for m in mushrooms:
        m.draw(screen)

    # Petit hérisson
    hedgehog.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("HEDGEHOG & AUTUMN LEAVES — PROMENADE DOUCE", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Feuilles : {len(leaves)} | Champignons : {len(mushrooms)}", True, (245, 175, 75))
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("CLIC GAUCHE : Faire tomber des feuilles | M : Ajouter un champignon | SOURIS : Brise | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()