class Creature:
    def __init__(self):
        self.damage = 3
        self.armor = 2
        self.hp = 10
        self.repr = "g"
        self.pos = (4,2)
        self.equipment = []

    def __repr__(self):
        return self.repr


class Player(Creature):
    def __init__(self):
        super().__init__()
        self.repr = "P"
        self.name = "Markemus"
        self.hp = 10
        self.score = 0
        self.items = []