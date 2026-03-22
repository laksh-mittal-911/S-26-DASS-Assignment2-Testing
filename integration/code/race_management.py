import random

class Race:
    def __init__(self, is_raining: bool, night_time: bool):
        self.is_raining = is_raining
        self.night_time = night_time

class RaceManagement:
    def __init__(self, crew_mgr, inventory, results_system):
        self.crew_mgr = crew_mgr
        self.inventory = inventory
        self.results_system = results_system

    def enter_race(self, race: Race, driver_id: str, car_id: str, strategist_id: str = None):
        driver = self.crew_mgr.reg_system.get_crew_member(driver_id)
        if not driver or driver.status != 'AVAILABLE':
            raise ValueError("Driver not available")
        if driver.base_stamina < 30:
            raise ValueError("Driver exhausted")

        driver_stats = self.crew_mgr.get_stats(driver_id)
        car = self.inventory.cars.get(car_id)
        
        # BUG 1 (FIXED): Race management originally allowed a car with 0 durability to race.
        if car.durability <= 0:
            raise ValueError("Car is completely totaled and cannot race.")
            
        driver.status = 'RACING'
        
        # Win calculation formula
        base_score = driver_stats.skill + car.engine_power + (car.aerodynamics * driver_stats.cornering_ability / 100)
        
        if race.is_raining:
            penalty = 20
            if strategist_id:
                strat = self.crew_mgr.reg_system.get_crew_member(strategist_id)
                if strat and strat.status == 'AVAILABLE':
                    strat.status = 'RACING'
                    s_stats = self.crew_mgr.get_stats(strategist_id)
                    penalty -= (s_stats.weather_prediction / 5)
            penalty = max(0, penalty)
            base_score -= penalty

        base_score += driver_stats.aggression * 0.5
        
        # Matchmaking vs NPC opponent score
        opponent_score = random.randint(150, 300)
        placement = 1 if base_score > opponent_score + 50 else (2 if base_score > opponent_score else (3 if base_score > opponent_score - 50 else 4))
        
        # Post-race consequences
        driver.base_stamina = max(0, driver.base_stamina - 30)
        durability_loss = 25
        if driver_stats.aggression > 70:
            durability_loss *= 2
        car.durability = max(0, car.durability - durability_loss)
        car.tire_wear = min(100, car.tire_wear + 40)
        
        # Invoke Results System
        placement = self.results_system.process_race(driver_id, car_id, placement)
        
        driver.status = 'AVAILABLE'
        if strategist_id:
            strat = self.crew_mgr.reg_system.get_crew_member(strategist_id)
            if strat: strat.status = 'AVAILABLE'
            
        return placement
