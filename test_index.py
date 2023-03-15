import index
import pytest

import creatures as c
import gear as g
import utils as u
from unittest import mock
from custom_exceptions import *


class TestCreature:
    def test_creature_pos(self):
        """Ensure that each creature is assigned a unique position."""
        model = index.Model()
        view = index.View(model=model)
        controller = index.Controller(model, view)
        controller.populate_room()
        positions = [creature.pos for creature in model.creatures]
        assert len(set(positions)) == len(positions)

class TestEmpty:
    """These tests need an empty room (which they can populate accordingly)."""
    def setup_method(self):
        self.model = index.Model()
        self.view = index.View(model=self.model)
        self.controller = index.Controller(self.model, self.view)

    def teardown_method(self):
        del self.model
        del self.view
        del self.controller

    # @pytest.mark.skip
    def test_pickup_gear(self):
        """The player should pick up gear when walking over it."""
        assert len(self.model.floor_items) == 0
        sword = g.Sword()
        sword.pos = (3,2)
        self.model.floor_items.append(sword)
        self.controller.move(self.model.player, "w")
        assert sword not in self.model.floor_items
        assert sword in self.model.player.items

    # @pytest.mark.skip
    def test_floor_items(self):
        """Gear should be dropped on the floor."""
        assert len(self.model.floor_items) == 0
        sword = g.Sword()
        shield = g.Shield()
        self.model.player.items.append(sword)
        self.model.player.items.append(shield)
        self.controller.equip(self.model.player, sword)
        self.controller.equip(self.model.player, shield)
        self.controller.create_creature()
        self.model.creatures[-1].pos = (3, 2)
        self.view.print_board()
        self.controller.move_toward(self.model.player, self.model.creatures[1])
        self.controller.move_toward(self.model.player, self.model.creatures[1])
        self.controller.move_toward(self.model.player, self.model.creatures[1])
        # assert len(self.model.floor_items) == 1
        # assert self.model.floor_items[0].pos == (3,2)

    def test_move_towards(self):
        """Assure that creatures can move towards one another properly."""
        # Place player in center of room
        self.model.player.pos = (2,2)
        # create creatures
        self.controller.create_creature()
        self.model.creatures[-1].pos = (2,4)
        self.controller.create_creature()
        self.model.creatures[-1].pos = (2,0)
        self.controller.create_creature()
        self.model.creatures[-1].pos = (0,2)
        self.controller.create_creature()
        self.model.creatures[-1].pos = (4,2)
        # self.view.print_board()

        self.controller.move_toward(self.model.creatures[1], self.model.player)
        self.controller.move_toward(self.model.creatures[2], self.model.player)
        self.controller.move_toward(self.model.creatures[3], self.model.player)
        self.controller.move_toward(self.model.creatures[4], self.model.player)

        assert self.model.creatures[0].pos == (2,2)
        assert self.model.creatures[1].pos == (2,3)
        assert self.model.creatures[2].pos == (2,1)
        assert self.model.creatures[3].pos == (1,2)
        assert self.model.creatures[4].pos == (3,2)

    def test_wasd(self):
        """Assures the wasd controls move the player to the correct position."""
        assert self.model.player.pos == (4,2)
        self.controller.move(self.model.player, "w")
        assert self.model.player.pos == (3,2)
        self.controller.move(self.model.player, "a")
        assert self.model.player.pos == (3,1)
        self.controller.move(self.model.player, "s")
        assert self.model.player.pos == (4,1)
        self.controller.move(self.model.player, "d")
        assert self.model.player.pos == (4,2)

    def test_death(self):
        """Test that player character dying raises a DeathError properly."""
        self.controller.create_creature()
        other_creature = self.model.creatures[-1]
        other_creature.pos = (self.model.player.pos[0] - 1, self.model.player.pos[1])
        other_creature.damage = self.model.player.damage
        other_creature.armor = self.model.player.armor
        other_creature.hp = self.model.player.hp
        self.view.print_board()

        # Player character should die
        with pytest.raises(DeathError) as e_death:
            for i in range(7):
                self.controller.move(self.model.player, "w")
            # self.index.print(e_death)

    def test_equip_unequip(self):
        """Test that damage and armor are updated correctly when applying and removing gear."""
        # Equip and unequip gear
        assert self.model.player.damage == 3
        assert self.model.player.armor == 2
        sword = g.Sword()
        spear = g.Spear()
        shield = g.Shield()
        self.model.player.items.append(sword)
        self.model.player.items.append(shield)
        self.model.player.items.append(spear)
        # equip
        assert len(self.model.player.equipment) == 0
        self.controller.equip(self.model.player, sword)
        self.controller.equip(self.model.player, shield)
        # assert spear is NOT equipped since sword already is.
        with pytest.raises(ValueError):
            self.controller.equip(self.model.player, spear)
        assert self.model.player.damage == 8
        assert self.model.player.armor == 7
        assert len(self.model.player.equipment) == 2
        # unequip
        self.controller.unequip(self.model.player, sword)
        self.controller.unequip(self.model.player, shield)
        assert self.model.player.damage == 3
        assert self.model.player.armor == 2
        assert len(self.model.player.equipment) == 0
        # Try to unequip gear again
        with pytest.raises(ValueError) as e_notequipped:
            self.controller.unequip(self.model.player, sword)

    # @pytest.mark.skip
    # @mock.patch("index.input", side_effects=["0"])
    def test_equip_command(self):
        t_weapon = g.TestWeapon()
        index.input = lambda _: "0"
        self.model.player.items.append(t_weapon)
        # index.input = u.iter_cmds(["e", "0"])
        self.controller.equip_cmd()
        assert t_weapon in self.model.player.equipment

class TestPopulated:
    """These tests need a normal populated level."""
    def setup_method(self):
        self.model = index.Model()
        self.view = index.View(model=self.model)
        self.controller = index.Controller(self.model, self.view)
        self.controller.populate_room()

    def teardown_method(self):
        del self.model
        del self.view
        del self.controller

    def test_attack(self):
        """Test the attack function."""
        other_creature = self.model.creatures[1]
        other_hp = other_creature.hp
        player_hp = self.model.player.hp
        self.controller.attack(other_creature)
        assert self.model.player.hp == player_hp - (other_creature.damage / self.model.player.armor)
        assert other_creature.hp == other_hp - (self.model.player.damage / other_creature.armor)

    def test_creature_death(self):
        """Creatures should die when they reach zero hp."""
        creature = c.Creature()
        self.model.creatures.append(creature)
        creature.hp = 1
        self.controller.attack(other_creature=creature)
        assert creature not in self.model.creatures

    def test_input(self):
        """Tries each control to ensure they don't crash.
        Not a very complete test."""
        commands = iter(["w", "a", "s", "d", "exit"])
        index.input = lambda _: next(commands)
        # This should not run forever but I don't know how to check.
        self.controller.interface()