import pytest
import sys
import os

# Add the parent directory to sys.path so 'code' can be imported properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../code')))

from registration import RegistrationSystem
from crew_management import CrewManagement, DriverStats, MechanicStats, StrategistStats
from inventory import Inventory, Car
from race_management import RaceManagement, Race
from results import ResultsSystem
from mission_planning import MissionPlanning
from sponsorships import SponsorshipSystem
from garage import Garage

@pytest.fixture
def system():
    reg = RegistrationSystem()
    crew = CrewManagement(reg)
    inv = Inventory()
    results = ResultsSystem(inv, crew)
    sponsor = SponsorshipSystem(results, inv)
    results.sponsorships = sponsor
    race_mgr = RaceManagement(crew, inv, results)
    mission = MissionPlanning(crew, inv)
    garage = Garage(crew, inv)
    return {
        "reg": reg, "crew": crew, "inv": inv,
        "results": results, "sponsor": sponsor,
        "race_mgr": race_mgr, "mission": mission, "garage": garage
    }

def test_full_lifecycle(system):
    """Test 1: Full Lifecycle spanning 7 modules"""
    driver = system["reg"].register_crew_member("Dom", "Driver")
    system["crew"].assign_stats(driver.member_id, DriverStats(skill=500, aggression=80, cornering_ability=85))
    
    car = Car("Charger", engine_power=100, aerodynamics=50)
    system["inv"].add_car(car)
    system["inv"].add_part("V6_Turbo", 1)
    
    mech = system["reg"].register_crew_member("Letty", "Mechanic")
    system["crew"].assign_stats(mech.member_id, MechanicStats(wrench_speed=95))
    
    # Garage upgrade (Fixes Bug 2 validation)
    assert system["garage"].install_part(car.car_id, mech.member_id, "V6_Turbo") == True
    assert car.engine_power == 120
    
    # Trigger Apex Dynamics threshold
    race = Race(is_raining=False, night_time=True)
    system["race_mgr"].enter_race(race, driver.member_id, car.car_id)
    
    assert system["results"].driver_elos[driver.member_id] > 1000
    assert system["inv"].cash >= 10000 
    assert driver.base_stamina == 70
    assert car.durability < 100

def test_crash_loop(system):
    """Test 2: Crash Loop and DNF Morale"""
    driver = system["reg"].register_crew_member("Brian", "Driver")
    system["crew"].assign_stats(driver.member_id, DriverStats(skill=60, aggression=100))
    car = Car("Skyline")
    car.durability = 25 
    system["inv"].add_car(car)
    system["inv"].add_cash(1000)
    
    mech = system["reg"].register_crew_member("Jesse", "Mechanic")
    system["crew"].assign_stats(mech.member_id, MechanicStats(wrench_speed=80))
    
    race = Race(is_raining=False, night_time=False)
    placement = system["race_mgr"].enter_race(race, driver.member_id, car.car_id)
    assert placement == 'DNF'
    assert car.durability == 0
    assert driver.morale < 100
    
    # Fixes Bug 1 validation by not allowing broken car to race again
    with pytest.raises(ValueError, match="Car is completely totaled"):
        system["race_mgr"].enter_race(race, driver.member_id, car.car_id)
        
    assert system["garage"].pit_stop(car.car_id, mech.member_id) == True
    assert car.durability == 80 
    assert system["inv"].cash == 0

def test_lockout_mission_to_garage(system):
    """Test 3: Mission Dispatch applies Lockout"""
    driver = system["reg"].register_crew_member("Vince", "Driver")
    mech1 = system["reg"].register_crew_member("Leon", "Mechanic")
    mech2 = system["reg"].register_crew_member("Hector", "Mechanic")
    
    system["crew"].assign_stats(driver.member_id, DriverStats())
    system["crew"].assign_stats(mech1.member_id, MechanicStats())
    system["crew"].assign_stats(mech2.member_id, MechanicStats())
    
    car = Car("Civic")
    system["inv"].add_car(car)
    system["inv"].add_cash(1000)
    
    # Fixes Bug 3 validation
    assert system["mission"].dispatch_mission("Chop Shop Raid", driver.member_id, [mech1.member_id, mech2.member_id]) == True
    assert mech1.status == 'ON_MISSION'
    
    # Lockout Check
    assert system["garage"].pit_stop(car.car_id, mech1.member_id) == False
    system["mission"].resolve_missions()
    assert mech1.status == 'AVAILABLE'
    assert system["garage"].pit_stop(car.car_id, mech1.member_id) == True

def test_strategic_weather_mitigation(system):
    """Additional Coverage: Strategist mitigating weather"""
    driver = system["reg"].register_crew_member("DK", "Driver")
    system["crew"].assign_stats(driver.member_id, DriverStats(skill=80))
    strat = system["reg"].register_crew_member("Han", "Strategist")
    system["crew"].assign_stats(strat.member_id, StrategistStats(weather_prediction=100))
    
    car = Car("Z")
    system["inv"].add_car(car)
    
    race = Race(is_raining=True, night_time=True)
    placement = system["race_mgr"].enter_race(race, driver.member_id, car.car_id, strat.member_id)
    assert strat.status == 'AVAILABLE'
    assert placement in [1, 2, 3, 4]

def test_driver_exhaustion(system):
    """Additional Coverage: Stamina calculation limits"""
    driver = system["reg"].register_crew_member("Sean", "Driver")
    system["crew"].assign_stats(driver.member_id, DriverStats(skill=100))
    car = Car("Mustang", durability=100)
    system["inv"].add_car(car)
    
    race = Race(is_raining=False, night_time=False)
    system["race_mgr"].enter_race(race, driver.member_id, car.car_id)
    system["race_mgr"].enter_race(race, driver.member_id, car.car_id)
    system["race_mgr"].enter_race(race, driver.member_id, car.car_id) 
    
    assert driver.base_stamina == 10
    with pytest.raises(ValueError, match="Driver exhausted"):
         system["race_mgr"].enter_race(race, driver.member_id, car.car_id)

def test_garage_insufficient_funds_and_parts(system):
    """Additional Coverage: Failing gracefully"""
    car = Car("RX7")
    system["inv"].add_car(car)
    mech = system["reg"].register_crew_member("Tej", "Mechanic")
    system["crew"].assign_stats(mech.member_id, MechanicStats(wrench_speed=100))
    
    assert system["garage"].pit_stop(car.car_id, mech.member_id) == False
    assert system["garage"].install_part(car.car_id, mech.member_id, "Nitrous") == False

def test_invalid_registration(system):
    """Additional Coverage: Registration errors"""
    with pytest.raises(ValueError, match="Invalid role"):
        system["reg"].register_crew_member("Nobody", "Hacker")
        
def test_driver_unavailable_for_race(system):
    """Additional Coverage: Race lockout via Mission"""
    driver = system["reg"].register_crew_member("Roman", "Driver")
    system["crew"].assign_stats(driver.member_id, DriverStats())
    mech1 = system["reg"].register_crew_member("Ramsey", "Mechanic")
    mech2 = system["reg"].register_crew_member("Hobbs", "Mechanic")
    car = Car("Buggy")
    system["inv"].add_car(car)
    
    system["mission"].dispatch_mission("Chop Shop Raid", driver.member_id, [mech1.member_id, mech2.member_id])
    
    with pytest.raises(ValueError, match="Driver not available"):
        system["race_mgr"].enter_race(Race(True, True), driver.member_id, car.car_id)
