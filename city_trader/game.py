from city_trader.player import Player
from city_trader.city import City
from city_trader.graph import Graph
from city_trader.history import History


class Game:
    def __init__(self, graph: Graph, cities: dict[str, City], player: Player):
        self.graph = graph
        self.cities = cities
        self.player = player
        self.starting_money = player.money
        self.history = History()

    def travel(self, destination: str):
        """Move to another city, spending fuel."""
        
        location = self.player.location

        # Prevent traveling to the same city
        if destination == location:
            return "You are already in this city."

        # Is there a road from here to there?
        if destination not in self.graph.cities.get(location, {}):
            return "Invalid destination — no road from here."

        fuel_cost = self.graph.cities[location][destination]
        if self.player.fuel < fuel_cost:
            return "Not enough fuel to travel!"

        self.player.fuel -= fuel_cost
        self.player.location = destination

        # Record the travel action
        self.history.add("Travel", f"Traveled from {location} to {destination}")

        return f"  Traveled to {destination}. Fuel left: {self.player.fuel}"

    def buy(self, item: str, quantity: int):
        """Buy goods from the current city."""
        
        city = self.cities[self.player.location]
        if item not in city.goods:
            return "This city doesn’t sell that item."

        total_cost = city.goods[item] * quantity
        if total_cost > self.player.money:
            return "You don’t have enough money."

        self.player.money -= total_cost
        self.player.inventory[item] = self.player.inventory.get(item, 0) + quantity

        # Record the buy action
        self.history.add("Buy", f"Bought {quantity} {item} in {self.player.location} for ${total_cost}")

        return f"Bought {quantity} {item} for ${total_cost}."

    def sell(self, item: str, quantity: int):
        """Sell goods from your inventory to the current city."""

        if self.player.inventory.get(item, 0) < quantity:
            return "You don’t have enough items to sell."

        city = self.cities[self.player.location]
        price = city.goods.get(item, 0)
        total_income = price * quantity

        self.player.inventory[item] -= quantity
        self.player.money += total_income

        # Record the sell action
        self.history.add("Sell", f"Sold {quantity} {item} in {self.player.location} for ${total_income}")

        return f"Sold {quantity} {item} for ${total_income}."

    def profit(self):
        """Check how much profit the player made compared to start."""
        
        return self.player.money - self.starting_money
