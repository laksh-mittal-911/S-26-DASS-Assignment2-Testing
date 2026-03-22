import uuid
from typing import Optional

class CrewMember:
    def __init__(self, name: str, role: str):
        self.member_id: str = str(uuid.uuid4())
        self.name: str = name
        self.role: str = role
        # Deep stats (stamina, skill, repair_speed, etc.) will be managed by crew_management.py
        self.stats: dict = {}

    def __str__(self) -> str:
        return f"[{self.member_id[:8]}] {self.name} - Role: {self.role}"

class RegistrationSystem:
    def __init__(self):
        self.registry: dict[str, CrewMember] = {}

    def register_crew_member(self, name: str, role: str) -> CrewMember:
        """
        Registers a new crew member with a name and a specific role in the StreetRace Manager.
        """
        if not name or not role:
            raise ValueError("Name and role are required for registration.")
            
        valid_roles = ['Driver', 'Mechanic', 'Strategist']
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")

        new_member = CrewMember(name, role)
        self.registry[new_member.member_id] = new_member
        return new_member

    def get_crew_member(self, member_id: str) -> Optional[CrewMember]:
        return self.registry.get(member_id)
        
    def get_all_crew_members(self) -> list[CrewMember]:
        return list(self.registry.values())
