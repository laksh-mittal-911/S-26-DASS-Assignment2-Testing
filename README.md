# DASS Assignment 2: Software Testing & Architecture

**Author:** Laksh Mittal  
**Roll Number:** 2024113003  

**Link to OneDrive Folder:** https://iiithydresearch-my.sharepoint.com/:f:/g/personal/laksh_mittal_research_iiit_ac_in/IgA_5eRd5T-UQ5ha9WVn_XHTAf0Cwdcq7TReiOsUkrObSQc?e=CdfQRc

**Link to Github Repository:** https://github.com/laksh-mittal-911/S-26-DASS-Assignment2-Testing

---

## Overview
This repository contains the complete implementation, refactoring, and automated testing suites for **DASS Assignment 2**.

The project is divided into three distinct phases:
- **Whitebox Testing**
- **Integration Testing**
- **Black-Box API Testing**

---

## Repository Structure
    S'26-DASS-Assignment2-Testing/
    ├── README.md                           # Master project documentation
    │
    ├── whitebox/                           # Task 1: Money-Poly
    │   ├── moneypoly/                      # Refactored source code (10/10 Pylint)
    │   ├── tests/                          # 100% coverage pytest suite
    │   ├── diagrams/
    │   │   └── controlflowgraph.png        # Hand-drawn Control Flow Graph
    │   └── report.pdf                      # Task 1 Code Quality & Testing Report
    │
    ├── integration/                        # Task 2: StreetRace Manager
    │   ├── code/                           # 8 Interconnected system modules
    │   ├── tests/
    │   │   └── test_integration.py         # Cross-module logic testing
    │   ├── diagrams/
    │   │   └── callgraph.png               # Hand-drawn System Call Graph
    │   └── report.pdf                      # Task 2 Architecture & Bug Report
    │
    └── blackbox/                           # Task 3: QuickCart API
        ├── tests/
        │   └── test_quickcart.py           # 77-scenario automated API attack
        └── report.pdf                      # Task 3 Vulnerability & Bug Report

---

## Task 1: Whitebox Testing (Money-Poly)

A comprehensive refactoring and structural analysis of a monolithic Monopoly-style simulation engine.

### Key Highlights
- **Code Quality:**  
  Achieved a perfect **10.00/10 Pylint score** by eliminating static analysis errors.

- **Unit Testing:**  
  Designed an exhaustive `pytest` suite achieving **near 100% branch coverage** across all game modules.

- **Bug Resolution:**  
  Fixed critical logical flaws such as:
  - Money destruction loops  
  - Mortgage constraint bypass  
  - `ZeroDivisionError` crashes  

- **Architecture:**  
  Developed a detailed **Control Flow Graph (CFG)**.

### Run Tests
    cd whitebox/
    python3 -m pytest tests/ -v

---

## Task 2: Integration Testing (StreetRace Manager)

Designed and implemented a motorsport-inspired simulation backend focusing on cross-module state management.

### Key Highlights
- **System Design:**  
  - Built **6 core modules + 2 custom modules**
    - `garage.py`
    - `sponsorships.py`
  - Features include:
    - Driver stamina tracking  
    - Car durability metrics  
    - Dynamic ELO ranking  

- **Integration Testing:**  
  Created advanced scenarios such as:
  - Crash Loop  
  - Multi-role concurrency lockouts  

- **Bug Resolution:**  
  Identified and fixed:
  - Cross-module state leaks  
  - Invalid matchmaking with destroyed cars  
  - Phantom garage parts  

- **Architecture:**  
  Constructed a **System Call Graph**.

###  Run Tests
    cd integration/
    python3 -m pytest tests/test_integration.py -v

---

## Task 3: Black-Box API Testing (QuickCart)

Performed black-box QA testing on a Dockerized REST API.

### Key Highlights
- **Test Engineering:**  
  Built a **77-test automated suite** using:
  - `pytest`
  - `requests`

- **Vulnerability Discovery:**  
  Identified **8 critical flaws**, including:
  - Discount cap bypass  
  - Cart total miscalculations  
  - COD limit violations  
  - Invalid data type injections  

- **Documentation:**  
  Produced a detailed bug report with:
  - Payloads  
  - Headers  
  - Expected vs actual behavior  

###  Run Tests
>  Ensure the QuickCart Docker container is running on **port 8080**

    cd blackbox/
    python3 -m pytest tests/test_quickcart.py -v

---

## Dependencies

- Python 3.10+
- pytest
- requests
- pylint
- Docker (for Task 3)

---

##  Summary

| Task   | Focus Area           | Outcome                                      |
|--------|---------------------|----------------------------------------------|
| Task 1 | Whitebox Testing    | Full refactor + near 100% coverage           |
| Task 2 | Integration Testing | Robust multi-module system                   |
| Task 3 | Black-box Testing   | 8 critical vulnerabilities discovered        |

---

## Notes
- All diagrams (CFG & Call Graphs) are available in the `diagrams/` directory.
- Each module is independently testable and follows clean architecture principles.

---