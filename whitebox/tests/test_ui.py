import pytest
from moneypoly import ui
from moneypoly.player import Player
from moneypoly.property import Property

def test_print_banner(capsys):
    ui.print_banner("Test Title")
    captured = capsys.readouterr().out
    assert "Test Title" in captured
    assert "===" in captured

def test_print_player_card(capsys):
    p = Player("Alice", balance=1500)
    p.position = 5
    p.in_jail = True
    p.get_out_of_jail_cards = 1
    
    prop = Property("Baltic Avenue", 3, 60, 4)
    prop.is_mortgaged = True
    p.properties.append(prop)
    
    ui.print_player_card(p)
    captured = capsys.readouterr().out
    assert "IN JAIL" in captured
    assert "Alice" in captured
    assert "Jail cards: 1" in captured
    assert "Baltic Avenue" in captured
    assert "MORTGAGED" in captured

def test_print_player_card_no_props(capsys):
    p = Player("Bob")
    ui.print_player_card(p)
    assert "Properties: none" in capsys.readouterr().out

def test_print_standings(capsys):
    p1 = Player("P1", balance=100)
    p2 = Player("P2", balance=500)
    p2.in_jail = True
    
    ui.print_standings([p1, p2])
    captured = capsys.readouterr().out
    assert "1. P2" in captured  # P2 has more money, should be first
    assert "JAILED" in captured

def test_print_board_ownership(capsys):
    class DummyBoard:
        def __init__(self):
            self.properties = [
                Property("Oriental", 6, 100, 6),
                Property("Vermont", 8, 100, 6)
            ]
    b = DummyBoard()
    b.properties[0].owner = Player("Alice")
    b.properties[1].is_mortgaged = True
    
    ui.print_board_ownership(b)
    captured = capsys.readouterr().out
    assert "Oriental" in captured
    assert "Alice" in captured
    assert "Vermont" in captured
    assert "*" in captured

def test_format_currency():
    assert ui.format_currency(1500) == "$1,500"
    assert ui.format_currency(-50) == "$-50"

def test_safe_int_input(monkeypatch):
    # Simulate valid input
    monkeypatch.setattr('builtins.input', lambda _: "42")
    assert ui.safe_int_input("Test: ") == 42
    
    # Simulate invalid input, should return default
    monkeypatch.setattr('builtins.input', lambda _: "not_a_number")
    assert ui.safe_int_input("Test: ", default=99) == 99

def test_confirm(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "  y  ")
    assert ui.confirm("Test? ") is True
    
    monkeypatch.setattr('builtins.input', lambda _: "n")
    assert ui.confirm("Test? ") is False
