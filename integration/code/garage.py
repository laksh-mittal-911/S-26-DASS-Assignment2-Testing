class Garage:
    def __init__(self, crew_mgr, inventory):
        self.crew_mgr = crew_mgr
        self.inventory = inventory

    def install_part(self, car_id: str, mechanic_id: str, part_name: str) -> bool:
        car = self.inventory.cars.get(car_id)
        mech = self.crew_mgr.reg_system.get_crew_member(mechanic_id)
        if not car or not mech or mech.status != 'AVAILABLE' or mech.role != 'Mechanic':
            return False
            
        if self.inventory.consume_part(part_name, 1):
            # BUG 2 (FIXED): Garage previously consumed part but didn't apply the buff.
            if part_name == "V6_Turbo":
                car.engine_power += 20
            elif part_name == "Carbon_Wing":
                car.aerodynamics += 15
            elif part_name == "Slick_Tires":
                car.tire_wear = 0
            return True
        return False

    def pit_stop(self, car_id: str, mechanic_id: str) -> bool:
        car = self.inventory.cars.get(car_id)
        mech = self.crew_mgr.reg_system.get_crew_member(mechanic_id)
        if not car or not mech or mech.status != 'AVAILABLE' or mech.role != 'Mechanic':
            return False
            
        mech_stats = self.crew_mgr.get_stats(mechanic_id)
        cost = 1000
        if self.inventory.spend_cash(cost):
            # Restore durability mapping to mechanic's inherent wrench_speed skill
            heal_amount = mech_stats.wrench_speed
            car.durability = min(100, car.durability + heal_amount)
            car.tire_wear = 0
            return True
        return False
