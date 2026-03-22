class MissionPlanning:
    def __init__(self, crew_mgr, inventory):
        self.crew_mgr = crew_mgr
        self.inventory = inventory
        self.active_missions = []

    def dispatch_mission(self, mission_name: str, driver_id: str, mechanic_ids: list[str]) -> bool:
        driver = self.crew_mgr.reg_system.get_crew_member(driver_id)
        mechanics = [self.crew_mgr.reg_system.get_crew_member(m_id) for m_id in mechanic_ids]
        
        if not driver or driver.status != 'AVAILABLE':
            return False
        for m in mechanics:
            if not m or m.status != 'AVAILABLE':
                return False
                
        if driver.base_stamina < 40:
             return False
             
        # BUG 3 (FIXED): Mission planner previously didn't lock crew member statuses to 'ON_MISSION'.
        # This allowed them to be used concurrently in Garage. Now strictly enforced.
        driver.status = 'ON_MISSION'
        for m in mechanics:
            m.status = 'ON_MISSION'
            
        self.active_missions.append({
            "name": mission_name,
            "driver": driver_id,
            "mechanics": mechanic_ids
        })
        return True

    def resolve_missions(self):
        for m in self.active_missions:
            driver = self.crew_mgr.reg_system.get_crew_member(m['driver'])
            driver.status = 'AVAILABLE'
            driver.base_stamina = max(0, driver.base_stamina - 40)
            for m_id in m['mechanics']:
                mech = self.crew_mgr.reg_system.get_crew_member(m_id)
                mech.status = 'AVAILABLE'
                
            if m['name'] == 'Chop Shop Raid':
                self.inventory.add_cash(5000)
                self.inventory.add_part("V6_Turbo", 1)
        self.active_missions = []
