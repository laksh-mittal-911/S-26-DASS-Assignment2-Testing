from registration import CrewMember

class DriverStats:
    def __init__(self, skill: int=50, aggression: int=50, cornering_ability: int=50):
        self.skill = skill
        self.aggression = aggression
        self.cornering_ability = cornering_ability

class MechanicStats:
    def __init__(self, wrench_speed: int=50, aero_knowledge: int=50):
        self.wrench_speed = wrench_speed
        self.aero_knowledge = aero_knowledge

class StrategistStats:
    def __init__(self, weather_prediction: int=50, tire_management: int=50):
        self.weather_prediction = weather_prediction
        self.tire_management = tire_management

class CrewManagement:
    def __init__(self, registration_system):
        self.reg_system = registration_system
        self.driver_stats = {}
        self.mechanic_stats = {}
        self.strategist_stats = {}

    def assign_stats(self, member_id: str, stats_obj):
        member = self.reg_system.get_crew_member(member_id)
        if not member: return
        if member.role == 'Driver' and isinstance(stats_obj, DriverStats):
            self.driver_stats[member_id] = stats_obj
        elif member.role == 'Mechanic' and isinstance(stats_obj, MechanicStats):
            self.mechanic_stats[member_id] = stats_obj
        elif member.role == 'Strategist' and isinstance(stats_obj, StrategistStats):
            self.strategist_stats[member_id] = stats_obj

    def get_stats(self, member_id: str):
        member = self.reg_system.get_crew_member(member_id)
        if not member: return None
        if member.role == 'Driver': return self.driver_stats.get(member_id)
        if member.role == 'Mechanic': return self.mechanic_stats.get(member_id)
        if member.role == 'Strategist': return self.strategist_stats.get(member_id)
