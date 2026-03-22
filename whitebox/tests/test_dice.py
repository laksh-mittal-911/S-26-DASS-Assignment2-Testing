from unittest.mock import patch
from moneypoly.dice import Dice

def test_dice_initial_state():
    # Make sure a brand new dice object is zeroed out
    d = Dice()
    assert d.die1 == 0
    assert d.die2 == 0
    assert d.doubles_streak == 0
    assert d.total() == 0

def test_dice_roll_boundaries():
    # Roll the dice a bunch of times to make sure we only get 1 through 6
    # If the logic is flawed (e.g. only rolls 1 to 5), this will catch it eventually!
    d = Dice()
    seen_values = set()
    
    for _ in range(100):
        d.roll()
        seen_values.add(d.die1)
        seen_values.add(d.die2)
        
        # Every roll should be between 1 and 6 inclusively
        assert 1 <= d.die1 <= 6
        assert 1 <= d.die2 <= 6

    # We rolled 100 times, we should have seen every number from 1 to 6 at least once
    assert seen_values == {1, 2, 3, 4, 5, 6}

@patch("moneypoly.dice.random.randint")
def test_dice_handles_doubles(mock_randint):
    d = Dice()
    
    # Force the dice to roll double 4s
    mock_randint.side_effect = [4, 4]
    total = d.roll()
    
    assert total == 8
    assert d.is_doubles() is True
    assert d.doubles_streak == 1
    assert "(DOUBLES)" in d.describe()

@patch("moneypoly.dice.random.randint")
def test_dice_resets_streak_on_non_doubles(mock_randint):
    d = Dice()
    d.doubles_streak = 2  # Pretend we just rolled doubles twice
    
    # Now force a normal roll consisting of 2 and 3
    mock_randint.side_effect = [2, 3]
    d.roll()
    
    assert d.is_doubles() is False
    assert d.doubles_streak == 0  # Streak must be wiped out
    assert "(DOUBLES)" not in d.describe()
    
    # Just to hit the __repr__ method for full coverage
    rep = repr(d)
    assert "Dice(die1=2, die2=3, streak=0)" in rep
