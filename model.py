"""MODEL: all game state + rules. NO pygame import here."""
import random
from abc import ABC, abstractmethod

WIDTH, HEIGHT = 800, 500


# ---------- tiny collision helper (replaces pygame.Rect so the model stays pygame-free) ----------
class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def colliderect(self, o):
        return (self.x < o.x + o.w and o.x < self.x + self.w and
                self.y < o.y + o.h and o.y < self.y + self.h)


# ---------- DIP: damage is an abstraction ----------
class DamageCalculator(ABC):
    @abstractmethod
    def compute(self, bullet): ...


class NormalDamage(DamageCalculator):
    def compute(self, bullet):
        return bullet.damage


class ResistantDamage(DamageCalculator):
    def compute(self, bullet):
        return bullet.damage * 0.5


class WeakDamage(DamageCalculator):
    def compute(self, bullet):
        return bullet.damage * 2


# ---------- ISP ----------
class Movable(ABC):
    @abstractmethod
    def move(self): ...


class Shielded(ABC):
    @abstractmethod
    def absorb(self, damage): ...


# ---------- Monsters (no color, no draw: that's the View's job) ----------
class Monster:
    W, H = 40, 30

    def __init__(self, x=700, y=220, speed=3, health=1, damage_calc=None):
        self.x, self.y, self.speed = x, y, speed
        self.max_health = self.health = health
        self.damage_calc = damage_calc or NormalDamage()

    def update(self):
        if isinstance(self, Movable):
            self.move()

    def take_hit(self, bullet):
        """Return True if the monster dies."""
        dmg = self.damage_calc.compute(bullet)
        if isinstance(self, Shielded):
            dmg = self.absorb(dmg)
        self.health -= dmg
        return self.health <= 0

    @property
    def rect(self):
        return Box(self.x, self.y, self.W, self.H)


class NormalMonster(Monster, Movable):
    def move(self):
        self.y += self.speed
        if self.y <= 0 or self.y >= HEIGHT - self.H:
            self.speed = -self.speed


class FastMonster(NormalMonster):
    def __init__(self, **kw):
        super().__init__(speed=6, **kw)


class StrongMonster(NormalMonster):
    def __init__(self, **kw):
        super().__init__(health=3, damage_calc=ResistantDamage(), **kw)


class FlyingMonster(NormalMonster):
    def __init__(self, **kw):
        super().__init__(speed=4, damage_calc=WeakDamage(), **kw)
        self.dx = -2

    def move(self):
        super().move()
        self.x += self.dx
        if self.x < 450 or self.x > 700:
            self.dx = -self.dx


class ImmobileMonster(Monster):
    def __init__(self, **kw):
        super().__init__(health=2, **kw)


class ShieldedMonster(NormalMonster, Shielded):
    def __init__(self, **kw):
        super().__init__(health=2, **kw)

    def absorb(self, damage):
        return max(0, damage - 0.5)


MONSTER_TYPES = [NormalMonster, FastMonster, StrongMonster, FlyingMonster,
                 ImmobileMonster, ShieldedMonster]


def spawn_monster():
    return random.choice(MONSTER_TYPES)(x=700, y=random.randint(0, HEIGHT - 30))


# ---------- Bullet / Player ----------
class Bullet:
    W, H = 10, 5

    def __init__(self, x, y, speed=10, damage=1):
        self.x, self.y, self.speed, self.damage = x, y, speed, damage

    def update(self):
        self.x += self.speed

    @property
    def rect(self):
        return Box(self.x, self.y, self.W, self.H)


class Player:
    W, H = 40, 30

    def __init__(self):
        self.x, self.y, self.speed = 50, 220, 5
        self.shoot_delay, self._last_shot = 150, 0

    def move(self, dy):
        self.y = max(0, min(HEIGHT - self.H, self.y + dy * self.speed))

    def shoot(self, now):
        if now - self._last_shot > self.shoot_delay:
            self._last_shot = now
            return Bullet(self.x + 40, self.y + 15)
        return None

    @property
    def rect(self):
        return Box(self.x, self.y, self.W, self.H)


# ---------- The Model facade the Controller talks to ----------
class GameModel:
    def __init__(self):
        self.player = Player()
        self.monster = NormalMonster()
        self.bullets = []
        self.score = 0
        self.events = []          # things that happened this frame (the View reads them for effects)
        self.status = "Fighting"  # game status shown in the info panel
        self._status_timer = 0

    def pop_events(self):
        ev, self.events = self.events, []
        return ev

    # actions called by the controller
    def move_player(self, dy):
        self.player.move(dy)

    def player_shoot(self, now):
        b = self.player.shoot(now)
        if b:
            self.bullets.append(b)
            self.events.append(("shoot", b.x, b.y + 2))

    def update(self):
        if self._status_timer > 0:
            self._status_timer -= 1
            if self._status_timer == 0:
                self.status = "Fighting"
        self.monster.update()
        for b in self.bullets[:]:
            b.update()
            if b.x > WIDTH:
                self.bullets.remove(b)
            elif b.rect.colliderect(self.monster.rect):
                self.bullets.remove(b)
                if self.monster.take_hit(b):
                    m = self.monster
                    self.events.append(("kill", m.x + m.W / 2, m.y + m.H / 2, type(m)))
                    self.score += 1
                    self.status, self._status_timer = "Monster defeated!", 90
                    self.monster = spawn_monster()
                else:
                    self.events.append(("hit", b.x + b.W, b.y))
