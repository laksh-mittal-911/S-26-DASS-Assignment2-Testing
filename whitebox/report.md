# Task 1: Whitebox Testing - Money-Poly
## 1.1 Control Flow Graph
[Note: CFG drawn based on POST-REFACTORING code]
*(Placeholder for scanned image)*

## 1.2 Code Quality Analysis (Iteration Log)

### Iteration 1: bank.py (Bank Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/bank.py:1:0`
  - **Issue description**: Python files should begin with a docstring describing their overall purpose. This file lacked it.
  - **Fix applied**: Added `"""Bank module – manages the central bank's funds, loans, and payouts."""` at line 1.
- **Error 2: `C0115` (Missing class docstring)**
  - **Location**: `moneypoly/bank.py:5:0` (`class Bank:`)
  - **Issue description**: The `Bank` class lacked a docstring explaining what the class represents in the context of Money-Poly.
  - **Fix applied**: Added `"""Central bank that holds reserves, issues loans, and processes payments."""` inside the class definition.
- **Error 3: `W0611` (Unused import math)**
  - **Location**: `moneypoly/bank.py:1:0`
  - **Issue description**: The standard library module `math` was imported but never utilized anywhere within the file, unnecessarily using memory and cluttering the namespace.
  - **Fix applied**: Deleted the unused `import math` statement.
- **Error 4: `E0401` (Unable to import 'moneypoly.config')**
  - **Location**: `moneypoly/bank.py:2:0`
  - **Issue description**: Pylint raised an import error because it incorrectly analyzes absolute internal package imports (`moneypoly.*`) run dynamically.
  - **Fix applied**: Suppressed globally with `# pylint: disable=import-error` at the top of the file as per allowed assignment rules.

### Iteration 2: board.py (Board Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/board.py:1:0`
  - **Issue description**: The `board.py` file didn't have an overarching summary describing the tiles and Board class.
  - **Fix applied**: Added `"""Board module – represents the Monopoly board and its tiles."""` at the start of the file.
- **Error 2: `C0121` (Singleton comparison)**
  - **Location**: `moneypoly/board.py:108:11` (`if prop.is_mortgaged == True:`)
  - **Issue description**: In Python, comparing a boolean variable using `== True` or `== False` violates PEP 8 guidelines. It should be evaluated for truthiness directly.
  - **Fix applied**: Changed `if prop.is_mortgaged == True:` to `if prop.is_mortgaged:` which provides identical logic but strictly adheres to Python coding standards.
- **Error 3 & 4: `E0401` (Unable to import internal modules)**
  - **Location**: `moneypoly/board.py:1:0` and `2:0`
  - **Issue description**: Pylint raised errors on importing `moneypoly.property` and `moneypoly.config`.
  - **Fix applied**: Suppressed globally with `# pylint: disable=import-error` as permitted by the assignment rules.

### Iteration 3: cards.py (Cards Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/cards.py:1:0`
  - **Issue description**: The file lacked a top-level docstring explaining what it contains (the cards data and deck logic).
  - **Fix applied**: Added `"""Cards module – defines Chance and Community Chest cards and the CardDeck."""` at line 1.
- **Error 2 to 25: `C0301` (Line too long)**
  - **Location**: `moneypoly/cards.py` (lines 4 to 15, and 19 to 30)
  - **Issue description**: Pylint enforces a strict 100-character line length limit (PEP 8 standard). The lists `CHANCE_CARDS` and `COMMUNITY_CHEST_CARDS` contained dictionary entries stretched out horizontally, exceeding 111+ characters per line. This reduces readability.
  - **Fix applied**: Refactored the single-line dictionaries into multi-line formatted dictionaries. Each key (`description`, `action`, `value`) was moved to a separate indented newline, making the code 100% compliant with the 100-character limit while radically improving legibility.

### Iteration 4: config.py (Config Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/config.py:1:0`
  - **Issue description**: The configuration file containing the game's constants lacked a top-level docstring summarizing its contents.
  - **Fix applied**: Added `"""Config module – contains all constant values and game configuration settings."""` at the beginning of the file.

### Iteration 5: dice.py (Dice Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/dice.py:1:0`
  - **Issue description**: The dice simulation file lacked a top-level docstring summarizing its contents.
  - **Fix applied**: Added `"""Dice module – simulates dice rolls, tracking values and doubles."""` at the beginning of the file.
- **Error 2: `W0611` (Unused import `BOARD_SIZE`)**
  - **Location**: `moneypoly/dice.py:2:0`
  - **Issue description**: The `BOARD_SIZE` constant was imported from `moneypoly.config` but was never used in the module.
  - **Fix applied**: Removed the unused import line entirely. Since it was the only thing imported, the whole `from moneypoly.config import...` statement was removed.
- **Error 3: `W0201` (Attribute defined outside `__init__`)**
  - **Location**: `moneypoly/dice.py:25:12`
  - **Issue description**: Pylint detected that `self.doubles_streak` was being assigned within the `reset()` and `roll()` methods, but it was not present directly inside the `__init__` constructor. For predictability and maintainability, all instance variables should be explicitly defined in `__init__`.
  - **Fix applied**: Added `self.doubles_streak = 0` inside the `__init__` method, prior to calling `self.reset()`.
- **Error 4: `E0401` (Unable to import)**
  - **Location**: `moneypoly/dice.py:2:0`
  - **Issue description**: Pylint raised an import error because it incorrectly analyzes internal codebase structure.
  - **Fix applied**: Added the global suppression flag `# pylint: disable=import-error` at the top of the file as per allowed rules.

### Iteration 6: game.py (Game Module)
- **Error 1: `C0114` (Missing module docstring)**
  - **Location**: `moneypoly/game.py:1:0`
  - **Issue description**: The core loop and state management file was missing its high-level docstring.
  - **Fix applied**: Inserted `"""Game module – manages the Monopoly game state and main loop."""` at line 1.
- **Error 2: `R0902` (Too many instance attributes 9/7)**
  - **Location**: `moneypoly/game.py:20:0` (in `Game.__init__`)
  - **Issue description**: The class contained nine direct attributes, exceeding the recommended limit of seven. This makes the class too complex and indicates missing abstractions.
  - **Fix applied**: Bundled `chance_deck` and `community_deck` into a single `self.decks` dictionary. Similarly bundled `current_index`, `turn_number`, and `running` into a `self.state` dictionary. Updated all corresponding references throughout the file. This reduced instance attributes to just five.
- **Error 3: `R0912` (Too many branches 15/12)**
  - **Location**: `moneypoly/game.py:295:4` (in `_apply_card`)
  - **Issue description**: The `_apply_card` function employed a massive `if-elif` chain (15 branches total counting nested conditionals) to route card actions, causing high cyclomatic complexity.
  - **Fix applied**: Extracted the card handler logic. Decomposed the giant block into 7 specific methods (`_card_collect`, `_card_pay`, `_card_jail`, `_card_jail_free`, `_card_move_to`, `_card_birthday`, `_card_collect_from_all`) and mapped them inside a `handlers` dictionary, dramatically simplifying `_apply_card`.
- **Error 4 & 5: `C0325` (Unnecessary parens)**
  - **Location**: `moneypoly/game.py:453:0` and `462:0`
  - **Issue description**: The statements `if not (0 <= idx < len(others)):` contained redundant outer parentheses.
  - **Fix applied**: Restructured to Pythonic syntax `if not 0 <= idx < len(others):`.
- **Error 6: `R1723` (Unnecessary "elif" after "break")**
  - **Location**: `moneypoly/game.py:402:12`
  - **Issue description**: In the interactive menu block, a leading `if` executed a `break`. Directly following was an `elif`, which is conceptually redundant.
  - **Fix applied**: Stripped the leading `el` to leave `if choice == 1:`, decoupling it optimally.
- **Error 7: `W1309` (f-string without interpolation)**
  - **Location**: `moneypoly/game.py:381:28`
  - **Issue description**: The string `f"GAME OVER"` contained an `f` prefix but didn't actually embed any variables.
  - **Fix applied**: Changed to a normal string literal `"GAME OVER"`.
- **Error 8 & 9: `W0611` (Unused imports)**
  - **Location**: `moneypoly/game.py:1:0` (`os`) and `3:0` (`GO_TO_JAIL_POSITION`)
  - **Issue description**: Modules fetched but not utilized waste namespace space.
  - **Fix applied**: Entirely purged the unused `import os` and removed the `GO_TO_JAIL_POSITION` variable from the config import block.
- **Error 10: `C0304` (Final newline missing)**
  - **Location**: `moneypoly/game.py:468:0`
  - **Issue description**: A basic formatting requirement indicating EOF without a trailing newline.
  - **Fix applied**: Appended an empty trailing newline to the end of the file.
- **Error 11-17: `E0401` (Unable to import)**
  - **Location**: `moneypoly/game.py:3:0` onwards
  - **Issue description**: Pylint parsing flaws for sibling/internal module imports.
  - **Fix applied**: Suppressed globally with `# pylint: disable=import-error`.

## 1.3 White Box Test Cases
*(Summary of coverage and logical bugs fixed)*