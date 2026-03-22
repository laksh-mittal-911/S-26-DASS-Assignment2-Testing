import pytest
from moneypoly.bank import Bank
from moneypoly.config import BANK_STARTING_FUNDS
from unittest.mock import MagicMock

def test_bank_initialization():
    bank = Bank()
    assert bank.get_balance() == BANK_STARTING_FUNDS
    assert bank.loan_count() == 0
    assert bank.total_loans_issued() == 0
    assert "Bank(funds=" in repr(bank)

def test_bank_collect_positive():
    bank = Bank()
    initial_funds = bank.get_balance()
    bank.collect(500)
    assert bank.get_balance() == initial_funds + 500
    assert bank._total_collected == 500

def test_bank_collect_negative_ignored():
    bank = Bank()
    initial_funds = bank.get_balance()
    bank.collect(-100)
    # The docstring says negative amounts are silently ignored
    assert bank.get_balance() == initial_funds
    assert bank._total_collected == 0

def test_bank_pay_out_normal():
    bank = Bank()
    initial_funds = bank.get_balance()
    paid = bank.pay_out(500)
    assert paid == 500
    assert bank.get_balance() == initial_funds - 500

def test_bank_pay_out_negative_or_zero():
    bank = Bank()
    assert bank.pay_out(0) == 0
    assert bank.pay_out(-50) == 0

def test_bank_pay_out_insufficient_funds():
    bank = Bank()
    with pytest.raises(ValueError, match="Bank cannot pay"):
        bank.pay_out(BANK_STARTING_FUNDS + 1000)

def test_bank_give_loan_normal():
    bank = Bank()
    initial_funds = bank.get_balance()
    mock_player = MagicMock()
    mock_player.name = "TestPlayer"
    
    bank.give_loan(mock_player, 1000)
    mock_player.add_money.assert_called_once_with(1000)
    
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == 1000
    # Docstring says "The bank's own funds are reduced accordingly."
    assert bank.get_balance() == initial_funds - 1000

def test_bank_give_loan_zero_or_negative():
    bank = Bank()
    mock_player = MagicMock()
    
    bank.give_loan(mock_player, 0)
    bank.give_loan(mock_player, -100)
    
    mock_player.add_money.assert_not_called()
    assert bank.loan_count() == 0

def test_bank_summary(capsys):
    bank = Bank()
    bank.collect(200)
    mock_player = MagicMock()
    mock_player.name = "P1"
    bank.give_loan(mock_player, 500)
    
    bank.summary()
    captured = capsys.readouterr()
    
    assert "Bank reserves" in captured.out
    assert "Total collected: $200" in captured.out
    assert "Loans issued   : 1 ($500)" in captured.out
