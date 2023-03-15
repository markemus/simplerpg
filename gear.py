from enum import Enum, auto
class Attaches(Enum):
    head = "head"
    body = "body"
    r_hand = "right hand"
    l_hand = "left hand"
    test = "test"


class Gear:
    def __init__(self):
        self.damage = 0
        self.armor = 0
        self.pos = None
        self.attaches = None

    def __repr__(self):
        return "i"


class Sword(Gear):
    def __init__(self):
        super().__init__()
        self.damage = 5
        self.name = "sword"
        self.attaches = Attaches.r_hand

    def __repr__(self):
        return "s"

class Spear(Gear):
    def __init__(self):
        super().__init__()
        self.name = "spear"
        self.damage = 3
        self.attaches = Attaches.r_hand

    def __repr__(self):
        return "|"

class Shield(Gear):
    def __init__(self):
        super().__init__()
        self.armor = 5
        self.name = "shield"
        self.attaches = Attaches.l_hand

    def __repr__(self):
        return "b"

class Helm(Gear):
    def __init__(self):
        super().__init__()
        self.armor = 5
        self.name = "helmet"
        self.attaches = Attaches.head

    def __repr__(self):
        return "h"

class Breastplate(Gear):
    def __init__(self):
        super().__init__()
        self.armor = 5
        self.name = "breastplate"
        self.attaches = Attaches.body

    def __repr__(self):
        return "a"

class TestWeapon(Gear):
    def __init__(self):
        super().__init__()
        self.attaches = Attaches.test
        self.name = "test_weapon"

# This gear can spawn
gear_list = [Sword, Shield, Helm, Breastplate]