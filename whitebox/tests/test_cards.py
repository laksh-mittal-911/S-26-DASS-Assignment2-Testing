import pytest
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS

def test_cards_loaded_correctly():
    # Just a quick sanity check to make sure the standard lists aren't empty
    assert len(CHANCE_CARDS) > 0
    assert len(COMMUNITY_CHEST_CARDS) > 0

def test_deck_initialization():
    deck = CardDeck([{"name": "test card"}])
    assert len(deck) == 1
    assert deck.cards_remaining() == 1
    assert "1 cards" in repr(deck)

def test_deck_draw_and_peek():
    fake_cards = [{"id": 1}, {"id": 2}]
    deck = CardDeck(fake_cards)
    
    # Peek should let me look at the top card without pulling it
    assert deck.peek() == {"id": 1}
    assert deck.cards_remaining() == 2
    
    # Draw actually pulls it
    drawn = deck.draw()
    assert drawn == {"id": 1}
    assert deck.cards_remaining() == 1
    
    assert deck.draw() == {"id": 2}
    
    # Once it's exhausted, does it cycle back to the beginning?
    # The docstring says yes, so let's verify it loops.
    assert deck.draw() == {"id": 1}

def test_deck_reshuffle():
    # If we have a sequence, reshuffling should reset the index
    deck = CardDeck([1, 2, 3, 4, 5])
    deck.draw()
    deck.draw()
    assert deck.cards_remaining() == 3
    
    deck.reshuffle()
    # Index should be back to 0, so remaining cards is back to 5
    assert deck.cards_remaining() == 5
    # The list is physically shuffled, but its length is the same
    assert len(deck) == 5

def test_deck_empty_deck_crash_bugs():
    # If someone weirdly creates an empty deck, it shouldn't crash
    empty_deck = CardDeck([])
    
    # Draw and peek should gracefully return None
    assert empty_deck.draw() is None
    assert empty_deck.peek() is None
    
    # Check if cards_remaining crashes with ZeroDivisionError (len is 0)
    assert empty_deck.cards_remaining() == 0
    
    # Check if the string representation crashes
    rep = repr(empty_deck)
    assert "0 cards" in rep
    assert "next=0" in rep
