import pytest
from moneypoly.player import Player
from moneypoly.config import STARTING_BALANCE, BOARD_SIZE, GO_SALARY, JAIL_POSITION

class DummyProperty:
    """A simple dummy class to act like a Property without needing complex mocks."""
    def __init__(self, name, price):
        self.name = name
        self.price = price

def test_player_starts_with_correct_defaults():
    # Make sure a brand new player has the right start state
    p = Player("Alice")
    assert p.name == "Alice"
    assert p.balance == STARTING_BALANCE
    assert p.position == 0
    assert len(p.properties) == 0
    assert p.in_jail is False

def test_player_adds_and_deducts_money_correctly():
    p = Player("Bob", balance=1000)
    
    # Simple math checks
    p.add_money(500)
    assert p.balance == 1500
    
    p.deduct_money(300)
    assert p.balance == 1200
    
    # We should definitely not be allowed to deduct or add negative money. 
    # That makes no sense.
    with pytest.raises(ValueError, match="Cannot add a negative amount"):
        p.add_money(-50)
        
    with pytest.raises(ValueError, match="Cannot deduct a negative amount"):
        p.deduct_money(-100)

def test_player_bankruptcy():
    p = Player("Charlie", balance=100)
    assert p.is_bankrupt() is False
    
    p.deduct_money(100)
    # At 0 dollars, you're bankrupt
    assert p.is_bankrupt() is True
    
def test_player_net_worth_includes_properties():
    # In Monopoly, your net worth is your cash PLUS the value of your assets
    p = Player("Dave", balance=100)
    
    # I built a little dummy property to attach to the player
    prop1 = DummyProperty("Park Place", price=350)
    prop2 = DummyProperty("Boardwalk", price=400)
    
    p.add_property(prop1)
    p.add_property(prop2)
    
    # Dave's total worth is  100 (cash) + 350 + 400 = 850
    assert p.net_worth() == 850

def test_player_normal_move_no_go():
    # Make sure normal moves (not passing go) work and don't award money
    p = Player("Garry", balance=1000)
    p.position = 10
    
    new_pos = p.move(5)
    
    assert new_pos == 15
    assert p.position == 15
    assert p.balance == 1000  # Cash shouldn't change

def test_player_movement_and_passing_go():
    p = Player("Eve", balance=1000)
    p.position = 38 # Start two spaces from Go
    
    # Roll a 5. New position should be 3.
    # We passed Go! So we should collect GO_SALARY ($200 by default)
    new_pos = p.move(5)
    
    assert new_pos == 3
    assert p.position == 3
    # Balance should go up by 200 because we passed Go
    assert p.balance == 1000 + GO_SALARY

def test_player_landing_exactly_on_go():
    p = Player("Frank", balance=1000)
    p.position = 38
    
    # Roll exactly a 2 to land directly on 0 (Go)
    p.move(2)
    assert p.position == 0
    assert p.balance == 1000 + GO_SALARY

def test_player_going_to_jail():
    p = Player("Grace")
    p.go_to_jail()
    
    assert p.position == JAIL_POSITION
    assert p.in_jail is True
    assert p.jail_turns == 0

def test_player_add_and_remove_properties():
    p = Player("Hank")
    prop = DummyProperty("Reading Railroad", 200)
    
    p.add_property(prop)
    assert p.count_properties() == 1
    
    # Adding the same property again shouldn't do anything because of the if-check
    p.add_property(prop)
    assert p.count_properties() == 1
    
    p.remove_property(prop)
    assert p.count_properties() == 0
    
    # Removing it again shouldn't crash
    p.remove_property(prop)

def test_player_status_and_repr():
    p = Player("Ivy", balance=1500)
    p.position = 10
    
    status = p.status_line()
    assert "Ivy: $1500" in status
    assert "pos=10" in status
    
    p.in_jail = True
    assert "[JAILED]" in p.status_line()
    
    rep = repr(p)
    assert "Player('Ivy'" in rep
