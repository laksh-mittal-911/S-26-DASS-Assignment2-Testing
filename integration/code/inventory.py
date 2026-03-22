import uuid

class Car:
    def __init__(self, name: str, engine_power: int=100, aerodynamics: int=100, durability: int=100):
        self.car_id = str(uuid.uuid4())
        self.name = name
        self.engine_power = engine_power
        self.aerodynamics = aerodynamics
        self.durability = durability
        self.tire_wear = 0

class Inventory:
    def __init__(self):
        self.cash: int = 0
        self.cars: dict[str, Car] = {}
        self.parts: dict[str, int] = {} # e.g. {"V6_Turbo": 2}

    def add_cash(self, amount: int):
        self.cash += amount

    def spend_cash(self, amount: int) -> bool:
        if self.cash >= amount:
            self.cash -= amount
            return True
        return False

    def add_car(self, car: Car):
        self.cars[car.car_id] = car

    def add_part(self, part_name: str, count: int=1):
        self.parts[part_name] = self.parts.get(part_name, 0) + count

    def consume_part(self, part_name: str, count: int=1) -> bool:
        if self.parts.get(part_name, 0) >= count:
            self.parts[part_name] -= count
            return True
        return False
