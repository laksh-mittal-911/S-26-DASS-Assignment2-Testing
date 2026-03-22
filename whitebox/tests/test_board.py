import pytest
from moneypoly.board import Board
from moneypoly.property import Property

class DummyPlayer:
    def __init__(self, name):
        self.name = name

def test_board_initialization():
    b = Board()
    assert len(b.groups) == 8
    assert len(b.properties) == 22

def test_board_get_property_at():
    b = Board()
    
    # Position 1 should be Mediterranean
    prop = b.get_property_at(1)
    assert prop is not None
    assert prop.name == "Mediterranean Avenue"
    
    # Position 0 is Go, not a property
    assert b.get_property_at(0) is None

def test_board_get_tile_type():
    b = Board()
    
    # Special tiles mapped correctly?
    assert b.get_tile_type(0) == "go"
    assert b.get_tile_type(33) == "community_chest"
    assert b.get_tile_type(5) == "railroad"
    
    # Normal properties mapped correctly?
    assert b.get_tile_type(3) == "property" # Baltic
    
    # Blank spaces (e.g. 4 is Income Tax? No wait, 4 is Income Tax. 
    # Let me check board.py. 4 is Income Tax, 38 is Luxury Tax, 20 is Free Parking, 30 goes to jail)
    # What is a blank space on a standard board?
    # Between 11 (St Charles) and 13 (States) is 12 (Electric Company).
    # Since utilities aren't in this simplistic property list, 12 should be blank!
    assert b.get_tile_type(12) == "blank"

def test_board_is_purchasable_logic():
    b = Board()
    
    # Space 0 (Go) is never purchasable
    assert b.is_purchasable(0) is False
    
    # Baltic (3) starts unowned and purchasable
    assert b.is_purchasable(3) is True
    
    # Let's buy Baltic
    baltic = b.get_property_at(3)
    baltic.owner = DummyPlayer("Alice")
    assert b.is_purchasable(3) is False
    
    # What if the bank somehow seizes it but it remains mortgaged?
    baltic.owner = None
    baltic.is_mortgaged = True
    
    # According to core Monopoly, if the bank owns it, anyone can buy it (they just assume the mortgage).
    # The board code strictly blocks this!
    assert b.is_purchasable(3) is True

def test_board_is_special_tile():
    b = Board()
    assert b.is_special_tile(7) is True  # Chance
    assert b.is_special_tile(39) is False # Boardwalk

def test_board_ownership_queries():
    b = Board()
    alice = DummyPlayer("Alice")
    
    assert len(b.properties_owned_by(alice)) == 0
    assert len(b.unowned_properties()) == 22
    
    # Alice buys Mediterranean (1) and Baltic (3)
    b.get_property_at(1).owner = alice
    b.get_property_at(3).owner = alice
    
    owned = b.properties_owned_by(alice)
    assert len(owned) == 2
    assert "Mediterranean Avenue" in [p.name for p in owned]
    
    # 22 total - 2 = 20 unowned
    assert len(b.unowned_properties()) == 20

def test_board_repr():
    b = Board()
    rep = repr(b)
    assert "22 properties" in rep
    assert "0 owned" in rep
    
    b.get_property_at(6).owner = DummyPlayer("Bob")
    rep_after = repr(b)
    assert "1 owned" in rep_after
