import pytest
from moneypoly.property import Property, PropertyGroup

class DummyPlayer:
    """A minimal dummy player so we don't have to deal with heavy mocks."""
    def __init__(self, name):
        self.name = name

def test_property_initialization():
    # Test creating a basic property without a group
    p = Property("Baltic", 1, 60, 2)
    assert p.name == "Baltic"
    assert p.position == 1
    assert p.price == 60
    assert p.base_rent == 2
    assert p.mortgage_value == 30
    assert p.owner is None
    assert p.is_mortgaged is False
    assert p.group is None

def test_property_rent_mechanics():
    p = Property("Oriental", 6, 100, 6)
    
    # Normal rent
    assert p.get_rent() == 6
    
    # Mortgaged properties shouldn't charge rent
    p.is_mortgaged = True
    assert p.get_rent() == 0

def test_property_group_monopoly_rent_bug():
    # Check if holding the full group actually doubles the rent correctly
    group = PropertyGroup("Light Blue", "light_blue")
    p1 = Property("Oriental", 6, 100, 6, group)
    p2 = Property("Vermont", 8, 100, 6, group)
    p3 = Property("Connecticut", 9, 120, 8, group)
    
    player1 = DummyPlayer("Alice")
    player2 = DummyPlayer("Bob")
    
    # Assign only TWO of the properties to Alice
    p1.owner = player1
    p2.owner = player1
    p3.owner = player2
    
    # Alice DOES NOT own the whole group (Bob owns Connecticut).
    # Therefore, her rent on Oriental should just be the base 6, NOT doubled!
    assert p1.get_rent() == 6

    # Now if Alice actually buys the third one...
    p3.owner = player1
    # Check Monopoly rent (doubled)
    assert p1.get_rent() == 12

def test_property_group_all_owned_by_none():
    group = PropertyGroup("Pink", "pink")
    Property("St. Charles", 11, 140, 10, group)
    
    # The bank (None) can't inherently 'own' a monopoly to charge double rent
    assert group.all_owned_by(None) is False

def test_property_mortgage_logic():
    p = Property("Virginia", 14, 160, 12)
    
    # Mortgaging should yield half price (80)
    payout = p.mortgage()
    assert payout == 80
    assert p.is_mortgaged is True
    
    # Trying to mortgage it again should politely do nothing and yield 0
    assert p.mortgage() == 0
    
    # Unmortgaging costs 10% interest. 80 * 1.1 = 88.
    cost = p.unmortgage()
    assert cost == 88
    assert p.is_mortgaged is False
    
    # Unmortgaging an already unmortgaged property shouldn't charge you
    assert p.unmortgage() == 0

def test_property_is_available():
    p = Property("St. James", 16, 180, 14)
    
    # Nobody owns it, it's available for purchase!
    assert p.is_available() is True
    
    # Alice buys it
    p.owner = DummyPlayer("Alice")
    assert p.is_available() is False
    
    # Even if she mortgages it, it STILL belongs to her. It is firmly NOT available
    # for another player to just buy from the bank.
    p.is_mortgaged = True
    assert p.is_available() is False
    
    # Edge case: Bank repossesses it, but it somehow remains mortgaged
    p.owner = None
    assert p.is_available() is True  # If nobody owns it, it's available, period.

def test_property_group_utilities():
    g = PropertyGroup("Orange", "orange")
    p1 = Property("NY Ave", 19, 200, 16)
    
    g.add_property(p1)
    # Check that duplication ignores it
    g.add_property(p1)
    
    assert g.size() == 1
    assert "PropertyGroup('Orange', 1 properties)" in repr(g)

def test_property_group_owner_counts():
    g = PropertyGroup("Red", "red")
    p1 = Property("Kentucky", 21, 220, 18, g)
    p2 = Property("Indiana", 23, 220, 18, g)
    p3 = Property("Illinois", 24, 240, 20, g)  # Unowned to hit the 'if owner is not None' false branch
    
    alice = DummyPlayer("Alice")
    p1.owner = alice
    p2.owner = alice
    
    counts = g.get_owner_counts()
    assert counts[alice] == 2

def test_property_repr():
    p = Property("Boardwalk", 39, 400, 50)
    assert "unowned" in repr(p)
    p.owner = DummyPlayer("Richie")
    assert "Richie" in repr(p)
