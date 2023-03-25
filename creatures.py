class Creature:
    def __init__(self):
        self.aggressive = False
        self.damage = 3
        self.armor = 2
        self.hp = 10
        self.repr = "C"
        self.pos = (4,2)
        self.score = 0

    def __repr__(self):
        return self.repr


class Goblin(Creature):
    """A weak creature, but aggressive."""
    def __init__(self):
        super().__init__()
        self.aggressive = True
        self.repr = "G"

class Troll(Creature):
    """A tough creature, but not aggressive."""
    def __init__(self):
        super().__init__()
        self.repr = "T"
        self.hp = 30
        self.damage = 6
        self.armor = 4

class Player(Creature):
    def __init__(self):
        super().__init__()
        self.repr = "P"
        self.name = "Markemus"
        self.hp = 10
        self.score = 0
        self.items = []
        self.equipment = []

# TODO fix troll spawns to work with tests (mock the list so they won't spawn then)
# spawn_list = [Goblin, Troll]
spawn_list = [Goblin]