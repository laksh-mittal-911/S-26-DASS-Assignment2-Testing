import pytest
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property

def test_game_init():
    g = Game(["Alice", "Bob"])
    assert len(g.players) == 2
    assert g.current_player().name == "Alice"

def test_advance_turn():
    g = Game(["Alice", "Bob"])
    assert g.state["current_index"] == 0
    g.advance_turn()
    assert g.state["current_index"] == 1
    assert g.state["turn_number"] == 1
    g.advance_turn()
    assert g.state["current_index"] == 0  # Wraps around
    assert g.state["turn_number"] == 2

def test_play_turn_in_jail(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    p.in_jail = True
    
    # Pretend we chose not to pay the jail fine
    monkeypatch.setattr('moneypoly.ui.confirm', lambda _: False)
    g.play_turn()
    
    # They should have served 1 turn in jail
    assert p.jail_turns == 1
    assert p.in_jail is True

def test_play_turn_normal_roll(monkeypatch):
    g = Game(["Alice", "Bob"])
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # We will let the natural dice roll happen. The turn should advance immediately 
    # unless they roll doubles. But even if they roll doubles, the function returns.
    g.play_turn()
    # Depending on doubles, index is either 0 or 1. Let's just assure it doesn't crash.

def test_play_turn_three_doubles_jail(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    
    # Force the dice to act like it just rolled its 3rd double
    def force_doubles():
        g.dice.doubles_streak = 3
        return 2
    monkeypatch.setattr(g.dice, 'roll', force_doubles)
    
    g.play_turn()
    assert p.in_jail is True
    assert p.position == 10

def test_move_and_resolve_taxes():
    g = Game(["Alice"])
    p = g.players[0]
    
    # Land on income tax
    g._move_and_resolve(p, 4)
    assert p.balance == 1300  # 1500 - 200
    
    # Land on luxury tax
    p.position = 0
    g._move_and_resolve(p, 38)
    assert p.balance == 1225  # 1300 - 75

def test_move_and_resolve_go_to_jail():
    g = Game(["Alice"])
    p = g.players[0]
    
    g._move_and_resolve(p, 30)
    assert p.in_jail is True
    assert p.position == 10

def test_move_and_resolve_chance_community_chest(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # 7 is chance
    g._move_and_resolve(p, 7)
    # 2 is community chest
    g._move_and_resolve(p, 2)
    # Just ensuring it hits the branch without crashing
    
def test_move_and_resolve_railroad_missing(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # Temporarily remove railroads from board to hit the `if prop is not None` False branch
    g.board.properties = []
    g._move_and_resolve(p, 5) # Railroad
    g._move_and_resolve(p, 1) # Property

def test_move_and_resolve_free_parking():
    g = Game(["Alice"])
    p = g.players[0]
    
    # Nothing should happen
    g._move_and_resolve(p, 20)
    assert p.balance == 1500

def test_buy_property(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)  # Mediterranean
    
    # Buy it!
    monkeypatch.setattr('builtins.input', lambda _: 'b')
    g._handle_property_tile(p, prop)
    
    assert p.balance == 1440
    assert prop.owner == p

def test_skip_property(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    
    monkeypatch.setattr('builtins.input', lambda _: 's')
    g._handle_property_tile(p, prop)
    
def test_handle_property_tile_auction(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    
    # Press 'a' to force an auction
    monkeypatch.setattr('builtins.input', lambda prompt: 'a' if 'Buy' in prompt else '0')
    g._handle_property_tile(p, prop)
    assert prop.owner is None # We passed the auction
    
    assert p.balance == 1500
    assert prop.owner is None

def test_buy_property_cannot_afford():
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(39) # Boardwalk (400)
    p.balance = 5 # Completely broke
    
    success = g.buy_property(p, prop)
    assert success is False
    assert prop.owner is None

def test_pay_rent():
    g = Game(["Alice", "Bob"])
    alice = g.players[0]
    bob = g.players[1]
    
    prop = g.board.get_property_at(1) # Rent is 2
    prop.owner = bob
    
    g._handle_property_tile(alice, prop)
    assert alice.balance == 1498
    assert bob.balance == 1502

    # If it's yours, no rent
    g._handle_property_tile(bob, prop)
    assert bob.balance == 1502

    # If it has NO owner, no rent (should hit the early return)
    # Since handle_property_tile diverts to 'buy' menu, we must invoke pay_rent directly
    # to hit the internal sanity check on line 161.
    prop.owner = None
    g.pay_rent(bob, prop)
    assert bob.balance == 1502
    prop.owner = bob

    # If it's mortgaged, no rent
    prop.is_mortgaged = True
    g.pay_rent(alice, prop)
    assert alice.balance == 1498

def test_mortgage_mechanics():
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1) # Price 60
    
    # Fails if you don't own it
    assert g.mortgage_property(p, prop) is False
    
    prop.owner = p
    
    assert g.mortgage_property(p, prop) is True
    assert p.balance == 1500 + 30
    
    # Fails if already mortgaged
    assert g.mortgage_property(p, prop) is False

def test_unmortgage_mechanics():
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1) # Price 60, Mortgage 30, Unmortgage ~33
    
    assert g.unmortgage_property(p, prop) is False # Not owner
    
    prop.owner = p
    assert g.unmortgage_property(p, prop) is False # Not mortgaged
    
    prop.is_mortgaged = True
    
    assert g.unmortgage_property(p, prop) is True
    assert p.balance == 1500 - 33
    
    # Test cannot afford unmortgage
    prop.is_mortgaged = True
    p.balance = 5
    assert g.unmortgage_property(p, prop) is False

def test_trade_logic():
    g = Game(["Alice", "Bob"])
    alice, bob = g.players
    prop = g.board.get_property_at(1)
    
    assert g.trade(alice, bob, prop, 100) is False # Alice doesn't own it
    
    prop.owner = alice
    assert g.trade(alice, bob, prop, 5000) is False # Bob is too poor
    
    assert g.trade(alice, bob, prop, 500) is True
    assert prop.owner == bob
    assert alice.balance == 2000
    assert bob.balance == 1000

def test_auction(monkeypatch):
    g = Game(["Alice", "Bob"])
    alice, bob = g.players
    prop = g.board.get_property_at(1)
    
    # Need to simulate inputs for an auction
    # Alice bids 50. Bob bids 60 but only has 5. We also need someone to bid lower than min.
    # Charlie bids 51 (min is 50+10=60)
    g = Game(["Alice", "Bob", "Charlie"])
    alice, bob, charlie = g.players
    prop = g.board.get_property_at(1)
    
    bob.balance = 5
    def mock_input(prompt, default=0):
        s = getattr(mock_input, 'state', 0)
        mock_input.state = s + 1
        return [50, 60, 51][s]
    
    import moneypoly.ui as ui
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    
    g.auction_property(prop)
    
    # Alice won!
    assert prop.owner == alice
    assert alice.balance == 1450

def test_auction_no_bids(monkeypatch):
    g = Game(["Alice"])
    prop = g.board.get_property_at(1)
    
    def mock_input(prompt, default=0): return 0
    import moneypoly.ui as ui
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    
    g.auction_property(prop)
    assert prop.owner is None

def test_cards(monkeypatch):
    g = Game(["Alice", "Bob"])
    alice, bob = g.players
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # Collect
    g._apply_card(alice, {"action": "collect", "value": 50, "description": ""})
    assert alice.balance == 1550
    
    # Pay
    g._apply_card(alice, {"action": "pay", "value": 50, "description": ""})
    assert alice.balance == 1500
    
    # Jail
    g._apply_card(alice, {"action": "jail", "value": 0, "description": ""})
    assert alice.in_jail is True
    alice.in_jail = False # reset
    
    # Missing coverage
    g._apply_card(alice, {"action": "fake_action", "value": 0, "description": ""})
    g.board.properties = []
    g._apply_card(alice, {"action": "move_to", "value": 39, "description": ""})
    
    # Jail Free
    g._apply_card(alice, {"action": "jail_free", "value": 0, "description": ""})
    assert alice.get_out_of_jail_cards == 1
    
    # Move to
    g._apply_card(alice, {"action": "move_to", "value": 39, "description": ""})
    assert alice.position == 39
    
    # Birthday
    g._apply_card(alice, {"action": "birthday", "value": 10, "description": ""})
    assert alice.balance == 1510
    assert bob.balance == 1490
    
    # Collect from all
    g._apply_card(alice, {"action": "collect_from_all", "value": 15, "description": ""})
    assert alice.balance == 1525
    assert bob.balance == 1475

def test_jail_mechanics(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    p.in_jail = True
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # Case 1: Use jail card
    p.get_out_of_jail_cards = 1
    monkeypatch.setattr('moneypoly.ui.confirm', lambda _: True)
    g._handle_jail_turn(p)
    assert p.in_jail is False
    assert p.get_out_of_jail_cards == 0
    
    # Case 1b: Has jail card, refuses to use it, then refuses to pay fine
    p.in_jail = True
    p.get_out_of_jail_cards = 1
    p.jail_turns = 1
    monkeypatch.setattr('moneypoly.ui.confirm', lambda _: False)
    g._handle_jail_turn(p)
    assert p.in_jail is True
    assert p.jail_turns == 2
    
    # Case 2: Pay fine
    p.in_jail = True
    monkeypatch.setattr('moneypoly.ui.confirm', lambda _: True)
    g._handle_jail_turn(p)
    assert p.in_jail is False
    
    # Case 3: wait 3 turns
    p.in_jail = True
    p.jail_turns = 2
    monkeypatch.setattr('moneypoly.ui.confirm', lambda _: False)
    g._handle_jail_turn(p)
    assert p.in_jail is False

def test_bankruptcy():
    g = Game(["Alice", "Bob", "Charlie", "Dave"])
    
    # Dave is current player index 3
    g.state["current_index"] = 3
    
    p = g.players[3] # Dave
    p.balance = -50
    
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    
    g._check_bankruptcy(p)
    
    assert p not in g.players
    assert prop.owner is None # Returned to bank
    # Index should wrap to 0 because 3 >= len(players=3)
    assert g.state["current_index"] == 0

def test_bankruptcy_no_wrap():
    g = Game(["Alice", "Bob", "Charlie", "Dave"])
    g.state["current_index"] = 0 # Alice
    p = g.players[0]
    p.balance = -50
    g._check_bankruptcy(p)
    assert g.state["current_index"] == 0 # Didn't wrap
    g = Game(["Alice", "Bob"])
    g.players[0].balance = 500
    g.players[1].balance = 5000
    
    # The fix ensures the HIGHEST net worth wins, not lowest!
    assert g.find_winner().name == "Bob"

def test_run_game_loop(monkeypatch):
    # Full run
    g = Game(["Alice", "Bob"])
    monkeypatch.setattr('builtins.input', lambda _: '0') # Roll constantly
    
    # End the game magically after 1 turn
    import moneypoly.config as config
    config.MAX_TURNS = 1
    g.run()
    assert g.state["running"] is True # It breaks out cleanly after loop
    
def test_interactive_menus_edge_cases(monkeypatch):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    
    import moneypoly.ui as ui
    def mock_input(prompt, default=0): return 0
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    
    # Trade error paths
    g.players.remove(g.players[1]) # Only Alice left
    g._menu_trade(p) # "No other players"
    
    g.players.append(Player("Bob")) # Back
    g.players[1].balance = 500
    p.properties.clear() # Alice has no properties
    
    def mock_input2(prompt, default=0):
        s = getattr(mock_input2, 'state', 0)
        mock_input2.state = s + 1
        return [1, 1, 200][s]
    # ui.safe_int_input = mock_input2
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input2)
    
    g._menu_trade(p) # "Has no properties" 

def test_interactive_menus(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    
    import moneypoly.ui as ui
    # Feed it sequences to test menus
    def mock_input(prompt, default=0):
        s = getattr(mock_input, 'state', 0)
        mock_input.state = s + 1
        return [1, 2, 6, 100, 0][s]
        
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    g.interactive_menu(p)
    
    # We borrowed 100 from the bank!
    assert p.balance == 1600

def test_menu_trade(monkeypatch):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    
    import moneypoly.ui as ui
    def mock_input(prompt, default=0):
        s = getattr(mock_input, 'state', 0)
        mock_input.state = s + 1
        # Partner index 1 (Bob), Prop index 1 (Mediterannean), cash 200
        return [1, 1, 200][s]
        
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    g._menu_trade(p)
    
    assert prop.owner == g.players[1]
    assert p.balance == 1700

def test_menu_mortgage_and_unmortgage(monkeypatch):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    
    import moneypoly.ui as ui
    def mock_input(prompt, default=0): return 1
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    
    g._menu_mortgage(p)
    assert prop.is_mortgaged is True
    
    def mock_invalid(prompt, default=0): return 99
    # ui.safe_int_input = mock_invalid
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_invalid)
    g._menu_unmortgage(p)
    # also try bad indices on trade
    g._menu_trade(p)
    g._menu_mortgage(p)
    
    # View standings, view board
    def mock_options(prompt, default=0):
        s = getattr(mock_options, 'state', 0)
        mock_options.state = s + 1
        return [1, 2, 0][s]
    # ui.safe_int_input = mock_options
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_options)
    g.interactive_menu(p)
    
    # ui.safe_int_input = mock_input
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_input)
    g._menu_unmortgage(p)
    assert prop.is_mortgaged is False
    
def test_find_winner_empty():
    g = Game([])
    assert g.find_winner() is None

from unittest.mock import patch

@patch('builtins.input', side_effect=['n', 'y', 's'])
def test_jail_mechanics_pay_fine(mock_input):
    g = Game(["Alice"])
    p = g.players[0]
    p.in_jail = True
    p.get_out_of_jail_cards = 1
    # First confirm (use card) = 'n', Second confirm (pay fine) = 'y'
    g._handle_jail_turn(p)
    assert p.in_jail is False

def test_missing_property_branches():
    g = Game(["Alice"])
    p = g.players[0]
    p.position = 5 # Railroad
    # Clear board properties to force `if prop is not None` False branch
    g.board.properties.clear()
    g._move_and_resolve(p, 5) # tile == "railroad" but no prop
    
    p.position = 1 # Property
    g._move_and_resolve(p, 0) # tile == "property" but no prop
    
    g._apply_card(p, {"action": "move_to", "value": 1, "description": ""})

def test_apply_card_none():
    g = Game(["Alice"])
    g._apply_card(g.players[0], None)

def test_bankruptcy_no_wrap_false():
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    p.balance = -50
    # Current index is 0. If Alice is removed, Bob becomes index 0. 
    # The length is 1. `current_index >= 1` evaluates to False (0 >= 1).
    g._check_bankruptcy(p)
    assert g.state["current_index"] == 0

@patch('moneypoly.ui.safe_int_input', side_effect=[1, 2, 3, 1, 4, 1, 5, 1, 1, 100, 999, 6, 50, 0])
def test_interactive_menu_all_branches(mock_input):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    
    # Needs a 2nd player with money for trade to not abort early
    g.players[1].balance = 500
    
    # The flat sequence will handle 1, 2, then 3(mortgage)->1, 4(unmortgage)->1, 
    # 5(trade)->1->1->100, 999(invalid), 6(loan)->50, 0(exit)
    g.interactive_menu(p)

@patch('moneypoly.ui.safe_int_input', side_effect=[999])
def test_menu_mortgage_invalid_index(mock_input):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    g._menu_mortgage(p)

@patch('moneypoly.ui.safe_int_input', side_effect=[999])
def test_menu_unmortgage_invalid_index(mock_input):
    g = Game(["Alice"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    prop.is_mortgaged = True
    p.add_property(prop)
    g._menu_unmortgage(p)
    
@patch('moneypoly.ui.safe_int_input', side_effect=[1, 1, 100])
def test_menu_trade_valid(mock_input):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    g._menu_trade(p)

def test_run_empty_players():
    g = Game([])
    g.run()

def test_missing_coverage_more_branches(monkeypatch):
    g = Game(["Alice", "Bob"])
    alice = g.players[0]
    
    # Mock builtins.input for property landing prompts
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # Hit railroad branch in _move_and_resolve
    alice.position = 0
    g._move_and_resolve(alice, 5) # Railroad 5
    
    # Hit property branch in _move_and_resolve
    alice.position = 0
    g._move_and_resolve(alice, 1) # Property 1
    
    # Hit _menu_unmortgage "no mortgaged properties" branch
    monkeypatch.setattr('moneypoly.ui.safe_int_input', lambda prompt, default=0: 0)
    g._menu_unmortgage(alice)
    
    # Hit _menu_trade invalid partner/property index branches
    # 1. Invalid partner index
    monkeypatch.setattr('moneypoly.ui.safe_int_input', lambda prompt, default=0: 99)
    g._menu_trade(alice)
    
    # 2. Invalid property index
    # Need partner to be valid first
    def mock_trade(prompt, default=0):
        s = getattr(mock_trade, 'state', 0)
        mock_trade.state = s + 1
        return [1, 99][s] # partner 1, then property 99
    
    prop = g.board.get_property_at(1)
    prop.owner = alice
    alice.add_property(prop)
    
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_trade)
    g._menu_trade(alice)

def test_bankruptcy_no_players():
    g = Game(["Alice"])
    p = g.players[0]
    p.balance = -100
    g.players.clear()
    g._check_bankruptcy(p)
    assert len(g.players) == 0

def test_clinch_100_coverage(monkeypatch):
    g = Game(["Alice", "Bob"])
    p = g.players[0]
    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # 1. Hit railroad body (Line 112)
    # Railroads are not in board.properties by default. Let's add one.
    from moneypoly.property import Property
    fake_rail = Property("Reading RR", 5, 200, 25)
    g.board.properties.append(fake_rail)
    p.position = 0
    g._move_and_resolve(p, 5) # Lands on railroad, prop is now not None
    
    # 2. Hit card move_to property (Lines 344-346)
    # Needs to land on a VALID property while board.properties IS NOT empty
    # Position 1 is Mediterranean
    g._apply_card(p, {"action": "move_to", "value": 1, "description": "Go to Med"})
    assert p.position == 1
    
    # 3. Hit loan amount <= 0 branch (Line 433 skipping 434)
    # And hit find_winner empty check (Line 371-373)
    # We do this via interactive_menu
    def mock_loan_esc(prompt, default=0):
        s = getattr(mock_loan_esc, 'state', 0)
        mock_loan_esc.state = s + 1
        return [6, 0, 0][s] # choice 6 (loan), amount 0, choice 0 (exit)
    monkeypatch.setattr('moneypoly.ui.safe_int_input', mock_loan_esc)
    g.interactive_menu(p)
    
    # 4. Final find_winner and check_bankruptcy survivors
    g.players = []
    assert g.find_winner() is None
    g._check_bankruptcy(p)
