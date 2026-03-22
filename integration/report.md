# StreetRace Manager - Integration Testing Report

## 1. Introduction & System Architecture
"StreetRace Manager" is a highly interconnected command-line simulation of a motorsport management ecosystem. The application logic revolves around complex, cross-module resource management:
- **Base Stats:** Crew members possess inherently trackable `base_stamina` and dynamic `morale`.
- **Granular Vehicles:** Cars have `durability`, `engine_power`, `aerodynamics`, and `tire_wear`.
- **ELO Systems:** Driver rankings scale through a custom ELO tracking mechanism that governs sponsorship unlocks and passive income.
These constraints dictate that every action has severe consequences. Running a race exhausts stamina, depletes durability, and affects morale upon crashing.

## 2. How to Run
To run the automated exhaustive test suite verifying the integrity of the 8 interconnected modules:
```bash
python3 -m pytest integration/tests/test_integration.py -v
```

To manually interact with the deep systems and run a simulation game loop using the Python REPL:
1. Navigate to the integration/code folder
2. Run the code below using python3 terminal
```python
# Import the architecture
from registration import RegistrationSystem
from crew_management import CrewManagement, DriverStats, MechanicStats
from inventory import Inventory, Car
from race_management import RaceManagement, Race
from results import ResultsSystem
from garage import Garage

# 1. Initialize Systems
reg = RegistrationSystem()
crew = CrewManagement(reg)
inv = Inventory()
results = ResultsSystem(inv, crew)
race_mgr = RaceManagement(crew, inv, results)
garage = Garage(crew, inv)

# 2. Register Your Crew!
driver = reg.register_crew_member("Dom Toretto", "Driver")
crew.assign_stats(driver.member_id, DriverStats(skill=95, aggression=100, cornering_ability=90))

mechanic = reg.register_crew_member("Jesse", "Mechanic")
crew.assign_stats(mechanic.member_id, MechanicStats(wrench_speed=95))

# 3. Buy a Car and Add Money
car = Car("Dodge Charger", engine_power=200, aerodynamics=50)
inv.add_car(car)
inv.add_cash(5000)

# 4. Check Initial Stats
print(f"[{car.name}] Durability: {car.durability}")
print(f"[{driver.name}] Morale: {driver.morale}, Stamina: {driver.base_stamina}")

# 5. Let's Race it! (Night time, No rain)
race = Race(is_raining=False, night_time=True)
print("Entering Race...")
race_mgr.enter_race(race, driver.member_id, car.car_id)

# 6. Check the Aftermath
print(f"Cash earned from Race Outcomes: ${inv.cash}")
print(f"[{car.name}] Post-Race Durability: {car.durability}")
print(f"[{driver.name}] Exhausted Stamina: {driver.base_stamina}")

# 7. Take it to the Garage for repairs
garage.pit_stop(car.car_id, mechanic.member_id)
print(f"[{car.name}] Repaired Durability: {car.durability} for $1000. Cash remaining: ${inv.cash}")
```

## 3. Module Breakdown
- **Registration (Core):** Manages `CrewMember` instantiation, allocating IDs, tracking `base_stamina`, `morale`, and strict availability `status`.
- **Crew Management (Core):** Asserts deep sub-class stats (`DriverStats`, `MechanicStats`, `StrategistStats`) bridging logic requirements.
- **Inventory (Core):** Centralized ledger for `Cash`, tracking `Car` asset degradation, and consuming upgrade parts.
- **Race Management (Core):** Matchmaking engine executing win calculations using skill + aero + engine formulas while calculating resource exhaustion.
- **Results (Core):** Distributes `Cash` to the Inventory ledger and mutates Driver ELO / streaks based on podium placement.
- **Mission Planning (Core):** Mutates crew member state to lock them inside multi-role heists/assignments while verifying threshold stamina.
- **Sponsorships (Custom 1):** Unlocks dynamic contracts triggered by explicit ELO and streak gates parsed from `ResultsSystem`. Deposits passive cash.
- **Garage (Custom 2):** Parses specific `Part` usage injected by mechanics with high `wrench_speed` to mutate the baseline `Car` stats.

## 4. Call Graph
![System Call Graph](./diagrams/CallGraph_StreetRace.png)

## 5. Integration Test Design (Task 2.2)
Exhaustive Pytest scenarios developed in `test_integration.py`:
- **The Full Lifecycle:** (Registration -> Crew -> Inventory -> Garage -> Race -> Results -> Sponsorship). Expected: Complete end-to-end success where an installed part increases stats, followed by a race win triggering ELO shifts and sponsorship deposits. Actual: Passed beautifully post-bug fixing.
- **The Crash Loop:** (Race -> Results -> Inventory -> Garage). Expected: Car with 25 durability drops to 0, triggering DNF, morale drops, and a mandatory garage visit. Actual: Passed.
- **The Multi-Role Lockout:** (Mission -> Garage). Expected: Assigning a Mechanic to 'ON_MISSION' correctly forbids using them in the Garage concurrently. Actual: Passed.
- **Driver Exhaustion:** (Race Management). Expected: Base stamina drops 30 points per race; attempting a 4th consecutive race throws a `ValueError`. Actual: Passed.
- **Strategic Weather:** (Race -> Crew). Expected: Strategist with `weather_prediction` mitigates rain penalties accurately during matchmaking logic. Actual: Passed.
- **Graceful Failures:** Expected: Invalid registry roles, unavailable drivers, and insufficient funds reject silently or safely. Actual: Passed.

## 6. Logical Bugs Found & Fixed
We planted and patched 3 distinct logical vulnerabilities during development:
1. **Bug 1: Totaled Cars Racing:** `race_management.py` initially skipped verifying internal `durability > 0`. Fixed by injecting a rigid `ValueError` check to prevent DNF farming.
2. **Bug 2: Phantom Parts:** `garage.py` correctly consumed parts via `Inventory` but skipped the assignment modifier to mutate the `Car` objects. Fixed by mapping part names to attribute additions (`engine_power += 20`).
3. **Bug 3: Concurrent Mission Lockout:** `mission_planning.py` dispatched members but failed to mutate `status = 'ON_MISSION'`, enabling duplicate task assignment in the Garage. Fixed by strongly enforcing state lockdowns during transit.
