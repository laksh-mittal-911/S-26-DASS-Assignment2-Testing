class ResultsSystem:
    def __init__(self, inventory, crew_mgr, sponsorships=None):
        self.inventory = inventory
        self.crew_mgr = crew_mgr
        self.driver_elos = {}
        self.driver_streaks = {}
        self.sponsorships = sponsorships

    def process_race(self, driver_id, car_id, placement):
        driver = self.crew_mgr.reg_system.get_crew_member(driver_id)
        car = self.inventory.cars.get(car_id)
        
        if driver_id not in self.driver_elos:
            self.driver_elos[driver_id] = 1000
            self.driver_streaks[driver_id] = 0
            
        if car.durability <= 0:
            driver.morale = max(0, driver.morale - 20)
            self.driver_elos[driver_id] -= 25
            self.driver_streaks[driver_id] = 0
            placement = 'DNF'
            return placement # Morale shift for DNF
            
        if placement == 1:
            driver.morale = min(100, driver.morale + 10)
            self.inventory.add_cash(10000)
            self.driver_elos[driver_id] += 50
            self.driver_streaks[driver_id] += 1
        elif placement == 2:
            self.inventory.add_cash(5000)
            self.driver_elos[driver_id] += 20
            self.driver_streaks[driver_id] = 0
        elif placement == 3:
            self.inventory.add_cash(2000)
            self.driver_elos[driver_id] += 5
            self.driver_streaks[driver_id] = 0
        else:
            driver.morale = max(0, driver.morale - 5)
            self.driver_elos[driver_id] -= 10
            self.driver_streaks[driver_id] = 0
            
        if self.sponsorships:
            self.sponsorships.process_payouts()

        return placement
