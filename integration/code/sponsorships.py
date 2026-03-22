class SponsorshipContract:
    def __init__(self, name: str, req_elo: int, req_streak: int, payout: int):
        self.name = name
        self.req_elo = req_elo
        self.req_streak = req_streak
        self.payout = payout

class SponsorshipSystem:
    def __init__(self, results_system, inventory):
        self.results = results_system
        self.inventory = inventory
        self.contracts = [
            SponsorshipContract("Apex Dynamics", 1050, 1, 2000), 
            SponsorshipContract("Velocity Corp", 1500, 3, 5000)
        ]
        self.active_sponsors = []

    def check_eligibility(self, driver_id: str):
        elo = self.results.driver_elos.get(driver_id, 0)
        streak = self.results.driver_streaks.get(driver_id, 0)
        for c in self.contracts:
            if elo >= c.req_elo and streak >= c.req_streak and c not in self.active_sponsors:
                self.active_sponsors.append(c)

    def process_payouts(self):
        # Dynamically trigger payouts directly to inventory
        for driver_id in self.results.driver_elos:
            self.check_eligibility(driver_id)
            
        for sponsor in self.active_sponsors:
            self.inventory.add_cash(sponsor.payout)
