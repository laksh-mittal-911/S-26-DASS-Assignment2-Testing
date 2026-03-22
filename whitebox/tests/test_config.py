import moneypoly.config as cfg

def test_config_constants():
    assert cfg.STARTING_BALANCE == 1500
    assert cfg.GO_SALARY == 200
    assert cfg.BOARD_SIZE == 40
    assert cfg.JAIL_POSITION == 10
    assert cfg.GO_TO_JAIL_POSITION == 30
    assert cfg.FREE_PARKING_POSITION == 20
    assert cfg.INCOME_TAX_POSITION == 4
    assert cfg.LUXURY_TAX_POSITION == 38
    assert cfg.INCOME_TAX_AMOUNT == 200
    assert cfg.LUXURY_TAX_AMOUNT == 75
    assert cfg.JAIL_FINE == 50
    assert cfg.MAX_TURNS == 100
    assert cfg.AUCTION_MIN_INCREMENT == 10
    assert cfg.BANK_STARTING_FUNDS == 20580
