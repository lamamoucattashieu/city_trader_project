class Player:
    def __init__(self, start_city, fuel=100, money=500):
        self.location = start_city
        self.fuel = fuel
        self.money = money
        self.inventory = {}

    def __repr__(self):
        return f"Player(location={self.location}, fuel={self.fuel}, money={self.money})"
