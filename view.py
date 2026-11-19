"""VIEW: everything pygame draws. Reads the model, never changes it.
All the visual polish (space background, ship, monster sprites, particles, glow) lives here."""
import math
import os
import random
import pygame
from model import (WIDTH, HEIGHT, NormalMonster, FastMonster, StrongMonster,
                   FlyingMonster, ImmobileMonster, ShieldedMonster)

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
MONSTER_COLORS = {          # main color of each monster (used for explosions)
    NormalMonster: (230, 50, 60), FastMonster: (255, 150, 30), StrongMonster: (170, 70, 230),
    FlyingMonster: (60, 210, 90), ImmobileMonster: (150, 150, 165), ShieldedMonster: (70, 200, 255),
}

# ------------------------------------------------------------------ helpers
_GLOW = {}


def scale(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


def glow(surf, x, y, radius, color):
    """Soft additive light blob."""
    key = (radius, color)
    if key not in _GLOW:
        g = pygame.Surface((radius * 2, radius * 2))
        for r in range(radius, 0, -2):
            pygame.draw.circle(g, scale(color, (1 - r / radius) ** 2), (radius, radius), r)
        _GLOW[key] = g
    surf.blit(_GLOW[key], (int(x) - radius, int(y) - radius), special_flags=pygame.BLEND_RGB_ADD)


def face(s, x, y, t, eye_dx=13, eye_y=12, angry=True, pupil=(20, 20, 30)):
    """Two eyes + brows, drawn on a monster whose top-left is (x, y)."""
    for ex in (x + eye_dx, x + 40 - eye_dx):
        pygame.draw.circle(s, WHITE, (ex, y + eye_y), 5)
        pygame.draw.circle(s, pupil, (ex - 2, y + eye_y), 2)
    if angry:
        pygame.draw.line(s, (30, 10, 20), (x + 7, y + eye_y - 8), (x + 17, y + eye_y - 4), 2)
        pygame.draw.line(s, (30, 10, 20), (x + 33, y + eye_y - 8), (x + 23, y + eye_y - 4), 2)


# ------------------------------------------------------------------ monster sprites
def draw_normal(s, m, t):
    x, y = int(m.x), int(m.y)
    glow(s, x + 20, y + 15, 34, (110, 10, 20))
    body = pygame.Rect(x, y + 2, 40, 27)
    pygame.draw.ellipse(s, (215, 40, 55), body)
    pygame.draw.ellipse(s, (255, 130, 130), body, 2)
    face(s, x, y, t)
    for i in range(4):  # teeth
        pygame.draw.polygon(s, WHITE, [(x + 12 + i * 5, y + 22), (x + 16 + i * 5, y + 22), (x + 14 + i * 5, y + 26)])


def draw_fast(s, m, t):
    x, y = int(m.x), int(m.y)
    glow(s, x + 20, y + 15, 36, (150, 70, 0))
    for i in range(3):  # speed trail
        ln = 12 + (t // 40 + i * 5) % 10
        pygame.draw.line(s, scale((255, 170, 60), 0.7 - i * 0.2), (x + 34, y + 8 + i * 7), (x + 34 + ln, y + 8 + i * 7), 2)
    pygame.draw.polygon(s, (255, 150, 30), [(x - 2, y + 15), (x + 38, y), (x + 28, y + 15), (x + 38, y + 30)])
    pygame.draw.polygon(s, (255, 220, 120), [(x - 2, y + 15), (x + 38, y), (x + 28, y + 15), (x + 38, y + 30)], 2)
    pygame.draw.circle(s, WHITE, (x + 14, y + 10), 4)
    pygame.draw.circle(s, WHITE, (x + 14, y + 20), 4)
    pygame.draw.circle(s, (20, 20, 30), (x + 12, y + 10), 2)
    pygame.draw.circle(s, (20, 20, 30), (x + 12, y + 20), 2)


def draw_strong(s, m, t):
    x, y = int(m.x), int(m.y)
    glow(s, x + 20, y + 15, 38, (80, 20, 120))
    pygame.draw.polygon(s, (200, 200, 220), [(x + 4, y + 6), (x + 9, y - 6), (x + 14, y + 6)])    # horns
    pygame.draw.polygon(s, (200, 200, 220), [(x + 26, y + 6), (x + 31, y - 6), (x + 36, y + 6)])
    body = pygame.Rect(x, y + 3, 40, 27)
    pygame.draw.rect(s, (120, 40, 175), body, border_radius=8)
    pygame.draw.rect(s, (200, 130, 255), body, 2, border_radius=8)
    pygame.draw.rect(s, (90, 25, 135), (x + 3, y + 20, 34, 7), border_radius=3)                  # armor plate
    pulse = 4 + int(math.sin(t * 0.008) * 1.5)
    pygame.draw.circle(s, (255, 230, 60), (x + 20, y + 12), pulse + 2)                           # cyclops eye
    pygame.draw.circle(s, (160, 0, 0), (x + 18, y + 12), 2)


def draw_flying(s, m, t):
    x, y = int(m.x), int(m.y)
    flap = math.sin(t * 0.03) * 10
    glow(s, x + 20, y + 15, 34, (0, 90, 30))
    pygame.draw.polygon(s, (150, 245, 170), [(x + 12, y + 12), (x + 26, y - 6 + flap), (x + 36, y + 10)])
    pygame.draw.polygon(s, (150, 245, 170), [(x + 12, y + 18), (x + 26, y + 36 - flap), (x + 36, y + 20)])
    pygame.draw.ellipse(s, (35, 170, 75), (x + 2, y + 6, 32, 20))
    pygame.draw.ellipse(s, (170, 255, 190), (x + 2, y + 6, 32, 20), 2)
    pygame.draw.circle(s, WHITE, (x + 11, y + 13), 4)
    pygame.draw.circle(s, WHITE, (x + 11, y + 20), 4)
    pygame.draw.circle(s, (20, 20, 30), (x + 9, y + 13), 2)
    pygame.draw.circle(s, (20, 20, 30), (x + 9, y + 20), 2)


def draw_immobile(s, m, t):
    x, y = int(m.x), int(m.y)
    glow(s, x + 20, y + 15, 32, (50, 50, 70))
    for sx in (6, 20, 33):  # spikes
        pygame.draw.polygon(s, (190, 190, 205), [(x + sx - 4, y + 6), (x + sx, y - 6), (x + sx + 4, y + 6)])
    rock = [(x + 2, y + 12), (x + 8, y + 3), (x + 32, y + 3), (x + 40, y + 13), (x + 36, y + 28), (x + 8, y + 29)]
    pygame.draw.polygon(s, (105, 105, 120), rock)
    pygame.draw.polygon(s, (190, 190, 205), rock, 2)
    pygame.draw.line(s, (70, 70, 85), (x + 22, y + 5), (x + 16, y + 14), 2)                      # crack
    face(s, x, y, t, eye_dx=14, eye_y=15, angry=False)


def draw_shielded(s, m, t):
    x, y = int(m.x), int(m.y)
    glow(s, x + 20, y + 15, 36, (0, 60, 90))
    body = pygame.Rect(x + 2, y + 3, 36, 25)
    pygame.draw.rect(s, (35, 35, 55), body, border_radius=7)
    pygame.draw.rect(s, (90, 90, 130), body, 2, border_radius=7)
    pygame.draw.rect(s, (255, 60, 60), (x + 8, y + 11, 24, 5), border_radius=2)                  # visor slit
    a = 70 + int(math.sin(t * 0.008) * 35)
    bubble = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(bubble, (80, 210, 255, a // 2), (32, 32), 28)
    pygame.draw.circle(bubble, (140, 235, 255, a + 90), (32, 32), 28, 2)
    s.blit(bubble, (x + 20 - 32, y + 15 - 32))


SPRITES = {NormalMonster: draw_normal, FastMonster: draw_fast, StrongMonster: draw_strong,
           FlyingMonster: draw_flying, ImmobileMonster: draw_immobile, ShieldedMonster: draw_shielded}


# ------------------------------------------------------------------ resources (SRP)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


class Assets:
    """Loads images and sounds from the assets/ folders.
    Replace a file in assets/ to change the look: no code needs to be touched.
    If a file is missing, the value is None and the View falls back to drawing it with code."""

    def __init__(self, root=ASSETS_DIR):
        self.root = root
        self.player = self._image("player", "player.png")
        self.bullet = self._image("bullets", "bullet.png")
        self.background = self._image("backgrounds", "background.png", (WIDTH, HEIGHT))
        self.monsters = {cls: self._image("monsters", cls.__name__.lower() + ".png") for cls in SPRITES}
        self.sounds = {name: self._sound(name + ".wav") for name in ("shoot", "hit", "kill")}

    def _image(self, folder, name, size=None):
        path = os.path.join(self.root, folder, name)
        if not os.path.isfile(path):
            return None
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size) if size else img

    def _sound(self, name):
        path = os.path.join(self.root, "sounds", name)
        if not (os.path.isfile(path) and pygame.mixer.get_init()):
            return None
        return pygame.mixer.Sound(path)

    def play(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()


# ------------------------------------------------------------------ health bar (SRP)
class HealthBar:
    def draw(self, screen, monster):
        ratio = max(0, monster.health) / monster.max_health
        color = (80, 220, 100) if ratio > 0.6 else (240, 200, 60) if ratio > 0.3 else (235, 70, 70)
        x, y, w = int(monster.x) - 2, int(monster.y) - 14, monster.W + 4
        pygame.draw.rect(screen, (20, 20, 35), (x, y, w, 7), border_radius=3)
        if ratio > 0:
            pygame.draw.rect(screen, color, (x + 1, y + 1, int((w - 2) * ratio), 5), border_radius=2)
        pygame.draw.rect(screen, (200, 205, 230), (x, y, w, 7), 1, border_radius=3)


# ------------------------------------------------------------------ the View
class View:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shooting Monster Game (MVC)")
        self.world = pygame.Surface((WIDTH, HEIGHT))        # drawn here, then shaken onto the screen
        self.font_big = pygame.font.Font(None, 44)
        self.font_small = pygame.font.Font(None, 22)
        self.health_bar = HealthBar()
        self.assets = Assets()
        self.bg = self.assets.background or self._make_background()
        # stars: x, y, speed, size, twinkle phase
        self.stars = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT), sp, sz, random.uniform(0, 6.28)]
                      for sp, sz, n in ((0.3, 1, 70), (0.7, 1, 40), (1.4, 2, 20)) for _ in range(n)]
        self.particles, self.rings, self.shake = [], [], 0

    # ---- static background: gradient + nebula clouds
    def _make_background(self):
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            k = y / HEIGHT
            pygame.draw.line(bg, (int(6 + 18 * k), int(8 + 4 * k), int(28 + 22 * k)), (0, y), (WIDTH, y))
        rnd = random.Random(7)
        for col in ((60, 20, 90), (15, 50, 95), (90, 25, 60)):
            glow(bg, rnd.randint(100, WIDTH - 100), rnd.randint(60, HEIGHT - 60), 190, scale(col, 0.55))
        return bg

    # ---- events coming from the model -> visual effects
    def _consume(self, events):
        for ev in events:
            self.assets.play(ev[0])
            if ev[0] == "shoot":
                self._burst(ev[1], ev[2], 4, (120, 230, 255), 2.5, 14)
            elif ev[0] == "hit":
                self._burst(ev[1], ev[2], 10, (255, 230, 150), 4, 18)
            elif ev[0] == "kill":
                col = MONSTER_COLORS[ev[3]]
                self._burst(ev[1], ev[2], 28, col, 6, 40)
                self._burst(ev[1], ev[2], 14, WHITE, 4, 25)
                self.rings.append([ev[1], ev[2], 6, 22, col])
                self.shake = 10

    def _burst(self, x, y, n, color, speed, life):
        for _ in range(n):
            a, v = random.uniform(0, 6.28), random.uniform(0.3, 1) * speed
            self.particles.append([x, y, math.cos(a) * v, math.sin(a) * v, life, life, color, random.choice((1, 2, 2, 3))])

    def _update_fx(self):
        for p in self.particles:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.06; p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]
        for r in self.rings:
            r[2] += 3; r[3] -= 1
        self.rings = [r for r in self.rings if r[3] > 0]

    # ---- drawing pieces
    @staticmethod
    def _blit_centered(surf, img, e):
        """Draw an image centered on the entity's box (so any image size works)."""
        surf.blit(img, (int(e.x + e.W / 2 - img.get_width() / 2), int(e.y + e.H / 2 - img.get_height() / 2)))

    def _draw_stars(self, w, t):
        for st in self.stars:
            st[0] -= st[2]
            if st[0] < 0:
                st[0], st[1] = WIDTH, random.uniform(0, HEIGHT)
            b = 150 + int(80 * math.sin(t * 0.004 + st[4]))
            pygame.draw.circle(w, (b, b, min(255, b + 30)), (int(st[0]), int(st[1])), st[3])

    def _draw_player(self, w, p, t):
        x, y = int(p.x), int(p.y)
        flame = 10 + random.randint(0, 8)
        glow(w, x - 2, y + 15, 30, (120, 60, 0))
        pygame.draw.polygon(w, (255, 210, 80), [(x + 6, y + 11), (x - flame, y + 15), (x + 6, y + 19)])
        pygame.draw.polygon(w, (255, 110, 30), [(x + 6, y + 12), (x - flame // 2, y + 15), (x + 6, y + 18)])
        glow(w, x + 20, y + 15, 34, (0, 50, 110))
        pygame.draw.polygon(w, (40, 90, 200), [(x + 4, y - 2), (x + 22, y + 10), (x + 10, y + 15)])       # wings
        pygame.draw.polygon(w, (40, 90, 200), [(x + 4, y + 32), (x + 22, y + 20), (x + 10, y + 15)])
        hull = [(x + 44, y + 15), (x + 12, y + 2), (x + 4, y + 15), (x + 12, y + 28)]
        pygame.draw.polygon(w, (70, 150, 255), hull)
        pygame.draw.polygon(w, (190, 225, 255), hull, 2)
        pygame.draw.ellipse(w, (190, 245, 255), (x + 20, y + 10, 14, 10))                                # cockpit
        pygame.draw.ellipse(w, WHITE, (x + 23, y + 11, 6, 4))

    def _draw_bullet(self, w, b):
        x, y = int(b.x), int(b.y)
        glow(w, x + 5, y + 2, 16, (0, 120, 170))
        pygame.draw.line(w, (60, 170, 220), (x - 14, y + 2), (x, y + 2), 2)                              # trail
        pygame.draw.rect(w, (200, 250, 255), (x, y, b.W, b.H), border_radius=2)

    def _draw_fx(self, w):
        for r in self.rings:
            pygame.draw.circle(w, scale(r[4], r[3] / 22), (int(r[0]), int(r[1])), int(r[2]), 2)
        for p in self.particles:
            k = p[4] / p[5]
            pygame.draw.circle(w, scale(p[6], 0.3 + 0.7 * k), (int(p[0]), int(p[1])), max(1, int(p[7] * k + 0.5)))

    def _panel(self, x, y, w, h):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (255, 255, 255, 28), (0, 0, w, h), border_radius=12)
        pygame.draw.rect(panel, (150, 190, 255, 120), (0, 0, w, h), 2, border_radius=12)
        self.screen.blit(panel, (x, y))

    def _draw_hud(self, model):
        """Information panel: score (left), monster health and game status (right)."""
        self._panel(12, 12, 170, 58)
        self.screen.blit(self.font_small.render("SCORE", True, (150, 175, 230)), (26, 20))
        self.screen.blit(self.font_big.render(str(model.score), True, WHITE), (26, 36))

        m = model.monster
        name = type(m).__name__.replace("Monster", "") + " monster"
        self._panel(WIDTH - 232, 12, 220, 70)
        lines = ((f"TARGET: {name}", (150, 175, 230)),
                 (f"HEALTH: {max(0, m.health):g} / {m.max_health:g}", WHITE),
                 (f"STATUS: {model.status}", (140, 235, 160)))
        for i, (text, col) in enumerate(lines):
            self.screen.blit(self.font_small.render(text, True, col), (WIDTH - 218, 20 + i * 19))

        hint = self.font_small.render("UP / DOWN : move      SPACE : shoot", True, (130, 145, 190))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 24))

    # ---- main entry used by the controller
    def render(self, model):
        t = pygame.time.get_ticks()
        self._consume(model.pop_events())
        self._update_fx()

        w = self.world
        w.blit(self.bg, (0, 0))
        self._draw_stars(w, t)
        for b in model.bullets:
            if self.assets.bullet:
                self._blit_centered(w, self.assets.bullet, b)
            else:
                self._draw_bullet(w, b)
        m = model.monster
        img = self.assets.monsters.get(type(m))
        if img:
            self._blit_centered(w, img, m)
        else:
            SPRITES[type(m)](w, m, t)
        self.health_bar.draw(w, m)
        if self.assets.player:
            self._blit_centered(w, self.assets.player, model.player)
        else:
            self._draw_player(w, model.player, t)
        self._draw_fx(w)

        ox = oy = 0
        if self.shake > 0:
            ox, oy = random.randint(-4, 4), random.randint(-4, 4)
            self.shake -= 1
        self.screen.fill((0, 0, 0))
        self.screen.blit(w, (ox, oy))
        self._draw_hud(model)
        pygame.display.update()
