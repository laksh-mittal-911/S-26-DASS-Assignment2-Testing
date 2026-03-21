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

## 1.3 White Box Test Cases
*(Summary of coverage and logical bugs fixed)*