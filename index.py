"""A simple rpg. No pressure."""
import copy
import random

import numpy as np

import creatures as c
import gear as g
from custom_exceptions import *

# Globals
DEBUG = False


class Model:
    """Model should include all the data for the game."""
    def __init__(self):
        self.turn = 0
        self.player = c.Player()
        # TODO potions have an expiry turn
        self.reset_board()

    def add_creature(self, creature):
        self.creatures.append(creature)

    def reset_board(self):
        """Remove all creatures except player (reset room)."""
        self.creatures = [self.player]
        self.board = np.zeros((5, 5), dtype=object)
        self.floor_items = []
        self.player.pos = (4,2)


class Controller:
    """Controller should include all the functions for generating/advancing the game."""
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.commands = {
            "w": lambda: self.round("w"),
            "a": lambda: self.round("a"),
            "s": lambda: self.round("s"),
            "d": lambda: self.round("d"),
            "inv": self.show_inventory,
            "eq": self.show_equipment,
            "e": self.equip_cmd,
            "u": self.unequip_cmd,
            "q": self.quaff_cmd,
        }
        self.descriptions = {
            "w": "walk forward",
            "a": "walk left",
            "s": "walk backward",
            "d": "walk right",
            "inv": "show inventory",
            "eq": "show equipped items",
            "e": "equip an item",
            "u": "unequip an item",
            "q": "quaff a potion",
        }


    def interface(self):
        name = input("Name your character:")
        if name: self.model.player.name = name

        endgame = False
        while not endgame:
            command = input("\nChoose an action or 'help':")
            if command == "help":
                # Help output is updated somewhat manually. Don't forget!
                for key, val in self.commands.items():
                    print(f"{key}: {self.descriptions[key]}")
                print("help")
                print("exit")

            elif command in self.commands.keys():
                # Run command and catch if player dies.
                try:
                    self.commands[command]()
                except DeathError as e:
                    print(e)
                    self.view.print(f"\nscore:{self.model.player.score}\nYou must begin a new game. Exiting...")
                    endgame = True
            elif command == "exit":
                endgame = True
            else:
                self.view.print("Command not recognized.")
            self.view.print_board()

    def create_creature(self):
        """Create a Creature and assign it a position."""
        creature = random.choice(c.spawn_list)()

        # ensure unique positions
        while creature.pos in [x.pos for x in self.model.creatures]:
            if DEBUG: print(f"Whiling creature.pos: {creature.pos}")
            creature.pos = (np.random.randint(0, self.model.board.shape[0]), np.random.randint(0, self.model.board.shape[1]))
        self.model.add_creature(creature)

    def populate_room(self):
        """Generate a random number of creatures."""
        min = 3
        max = 7
        n = random.randint(min, max)
        for c in range(1, n+1):
            self.create_creature()

    def move(self, creature, wasd):
        """Move a creature one tile in any direction."""
        moves = {
            "w": (-1,0),
            "a": (0,-1),
            "s": (1,0),
            "d": (0,1),
        }
        # Move
        move = moves[wasd]
        new_pos = (creature.pos[0] + move[0], creature.pos[1] + move[1])
        # attack if position is occupied (and don't move)
        if new_pos in [x.pos for x in self.model.creatures]:
            other_creature = self.model.creatures[[x.pos for x in self.model.creatures].index(new_pos)]
            self.attack(creature, other_creature)
        # move instead of attacking
        elif (new_pos[0] >= 0 and new_pos[1] >= 0) and (new_pos[0] <= self.model.board.shape[0] - 1 and new_pos[1] <= self.model.board.shape[1] - 1):
            creature.pos = new_pos
            # Exit if on exit
            if (creature == self.model.player) and creature.pos == (0,2):
                # Start a new level
                self.model.reset_board()
                self.populate_room()
        else:
            self.view.print("Invalid move.")

    def pickup(self, creature):
        """Player picks up items that he's standing on."""
        if creature == self.model.player:
            # pick up gear
            if creature.pos in [x.pos for x in self.model.floor_items]:
                gear = self.model.floor_items[[x.pos for x in self.model.floor_items].index(creature.pos)]
                self.model.floor_items.remove(gear)
                self.model.player.items.append(gear)

    def round(self, wasd):
        """Player move, pickup, attack, and have other creatures move."""
        self.move(self.model.player, wasd)
        self.pickup(self.model.player)
        for agg_creature in [x for x in self.model.creatures if x.aggressive]:
            self.view.print(f"{agg_creature} moves towards you!")
            self.move_toward(agg_creature, self.model.player)
        self.model.turn += 1

    def attack(self, attacker, defender):
        """damage should be calculated as a ratio between armor and damage, and applied to hp."""
        # damage round
        p_hp = attacker.hp
        o_o_hp = defender.hp
        attacker.hp -= (defender.damage / attacker.armor)
        defender.hp -= (attacker.damage / defender.armor)

        # Report damage
        self.view.print(f"{attacker} attacks the {defender}!")
        self.view.print(f"Damage: \n{attacker}:{round(p_hp - self.model.player.hp, 2)}\n{defender}: {round(o_o_hp - defender.hp, 2)}")
        self.view.print(f"HP: \n{attacker}:{round(self.model.player.hp, 2)}\n{defender}: {round(defender.hp, 2)}")

        # Death
        if defender.hp < 0:
            self.view.print(f"{defender} dies!")
            # Flip a coin to determine if gear is dropped
            flip = np.random.randint(0,2)
            if flip:
                dropped_gear = random.choice(g.gear_list)()
                dropped_gear.pos = copy.copy(defender.pos)
                self.model.floor_items.append(dropped_gear)
            self.model.creatures.remove(defender)
            attacker.score += 1
        if (attacker == self.model.player and attacker.hp <= 0) or (defender == self.model.player and defender.hp <= 0):
            raise DeathError("YOU DIED")

    def move_toward(self, creature, other_creature):
        """Move a creature one tile towards another creature."""
        diff = (other_creature.pos[0] - creature.pos[0], other_creature.pos[1] - creature.pos[1])
        if diff[0] < 0:
            wasd = "w"
        elif diff[0] > 0:
            wasd = "s"
        elif diff[1] < 0:
            wasd = "a"
        elif diff[1] > 0:
            wasd = "d"
        else:
            raise ValueError("Creatures should not occupy the same spot!")
        self.move(creature, wasd)

    def show_inventory(self):
        """Show the player's inventory"""
        for i, item in enumerate([x.name for x in self.model.player.items]):
            self.view.print(f"{i}. {item}")
        # self.view.print([x.name for x in self.model.player.items])
    def show_equipment(self):
        """Show the player's inventory"""
        for i, item in enumerate([x.name for x in self.model.player.equipment]):
            self.view.print(f"{i}. {item}")

    def equip_cmd(self):
        """Interface command to equip an item from inventory."""
        self.show_inventory()
        try:
            i = input("Which item would you like to equip?")
            i = int(i)
            try:
                item = self.model.player.items[i]
                self.equip(self.model.player, item)
                self.view.print(f"You equip the {item.name}.")
            except (ValueError, IndexError) as e:
                if isinstance(e, ValueError):
                    self.view.print(e)
                    self.view.print("Please select valid gear to equip.")
                else:
                    self.view.print(f"{e} ({i})\nYou must select a valid slot.")
        except (ValueError):
            self.view.print(f"You must enter a valid integer, not {i}.")

    def unequip_cmd(self):
        """Interface command to remove an item that is equipped."""
        self.show_equipment()
        try:
            i = input("Which item would you like to remove?")
            i = int(i)
            try:
                self.unequip(self.model.player, self.model.player.equipment[i])
            except (IndexError) as e:
                self.view.print(f"{e} ({i})\nYou must select valid gear.")
        except (ValueError):
            self.view.print(f"You must enter a valid integer, not {i}.")

    def equip(self, creature, gear):
        # equip unique items per attaches slot
        if gear.attaches == g.Attaches.noeq:
            raise ValueError("Cannot equip this item!")
        elif gear.attaches not in [x.attaches for x in creature.equipment]:
            creature.equipment.append(gear)
            creature.items.remove(gear)
            creature.damage += gear.damage
            creature.armor += gear.armor
        else:
            raise ValueError("Cannot equip gear in occupied slot!")

    def unequip(self, creature, gear):
        if gear in creature.equipment:
            creature.equipment.remove(gear)
            creature.items.append(gear)
            creature.damage -= gear.damage
            creature.armor -= gear.armor
        else:
            raise ValueError("gear is not equipped!")

    def quaff_cmd(self):
        """Interface command to equip an item from inventory."""
        self.show_inventory()
        try:
            i = input("Which item would you like to quaff?")
            i = int(i)
            try:
                self.quaff(self.model.player, self.model.player.items[i])
            except (IndexError, AttributeError) as e:
                if isinstance(e, AttributeError):
                    self.view.print(f"{type(e)} {e} ({i})\nYou must select a potion.")
                else:
                    self.view.print(f"{type(e)} {e} ({i})\nYou must select a valid index.")
        except (ValueError):
            self.view.print(f"You must enter a valid integer, not {i}.")
    def quaff(self, creature, potion):
        if potion in creature.items:
            creature.items.remove(potion)
            # TODO active potions
            # creature.active.append((potion, self.view.turn + potion.turntimer))
            potion.take_effect(creature)
        else:
            raise ValueError("Potion is not in inventory!")


class View:
    def __init__(self, model):
        self.model = model
        self.print = print

    def print_board(self):
        """Display everything in the room."""
        board_show = copy.copy(self.model.board)
        board_show[4, 2] = 1
        board_show[0, 2] = 9

        for item in self.model.floor_items:
            board_show[item.pos] = item
        for creature in self.model.creatures:
            board_show[creature.pos] = creature
        board_show[self.model.player.pos] = self.model.player


        # Print the board with header
        header = f"\n{self.model.player.name} HP:{round(self.model.player.hp,2)} DMG:{self.model.player.damage} ARM:{self.model.player.armor} SCORE:{self.model.player.score}"
        self.print(header)
        self.print(board_show)


# Main
if __name__ == "__main__":
    model = Model()
    view = View(model=model)
    controller = Controller(model=model, view=view)

    # Setup
    # Run game
    controller.populate_room()
    sword = g.Sword()
    shield = g.Shield()
    model.player.items.append(sword)
    model.player.items.append(shield)
    controller.equip(model.player, sword)
    controller.equip(model.player, shield)

    view.print_board()
    controller.interface()

    print("Done!")
