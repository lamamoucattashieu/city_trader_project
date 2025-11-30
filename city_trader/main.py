import json
from pathlib import Path
from city_trader.graph import Graph
from city_trader.city import City
from city_trader.player import Player
from city_trader.game import Game
from city_trader.optimizer import suggest_best_move

def show_price_table(cities):
    # Pretty-print a table of goods per city.
    # Average-case time complexity: O(C·G)
    # Worst-case time complexity: O(C·G)
    print("\n Current Market Prices:")
    goods = set()
    for city in cities.values():
        goods.update(city.goods.keys())

    goods = sorted(goods)
    header = ["City"] + goods
    rows = []
    for name, city in sorted(cities.items()):
        row = [name] + [f"${city.goods.get(g, '-')}" for g in goods]
        rows.append(row)

    # Column widths
    col_widths = [max(len(str(row[i])) for row in [header] + rows) for i in range(len(header))]

    # Header
    print(" | ".join(str(header[i]).ljust(col_widths[i]) for i in range(len(header))))
    print("-" * (sum(col_widths) + 3 * (len(header) - 1)))

    # Rows
    for row in rows:
        print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))

def main():

    world_path = Path(__file__).parent / "data" / "world.json"
    with world_path.open("r") as f:
        world = json.load(f)

    g = Graph()
    for city1, city2, cost in world["roads"]:
        g.add_road(city1, city2, cost)

    cities = {name: City(name, goods) for name, goods in world["cities"].items()}

    player = Player("Paris")
    game = Game(g, cities, player)

    print("Welcome to City Trader!")
    print(f"Starting in {player.location} with ${player.money} and {player.fuel} fuel.")

    ai_used = False  # track usage 

    while True:
        print("\nWhat would you like to do?")
        print("1. Travel")
        print("2. Buy")
        print("3. Sell")
        print("4. Check profit")
        print("5. Quit")
        print("6. Ask AI assistant (once)")
        choice = input("> ")

        if choice == "1":
            connected = list(g.cities.get(player.location, {}).keys())
            if not connected:
                print("No available routes from this city!")
                continue
            print(f"Connected cities: {connected}")
            dest = input("Enter destination city: ").strip()
            if dest not in connected:
                print("Invalid destination — must be one of the connected cities.")
                continue
            print(game.travel(dest))

        elif choice == "2":
            show_price_table(cities)
            print(f"You are in {player.location}. Available goods: {cities[player.location].goods}")
            item = input("What item to buy? ").strip().lower()

            if item not in cities[player.location].goods:
                print("This city doesn’t sell that item.")
                continue

            try:
                qty = int(input("Quantity: ").strip())
                if qty <= 0:
                    print("Quantity must be positive.")
                    continue
            except ValueError:
                print("Invalid input — please enter a number.")
                continue

            print(game.buy(item, qty))


        elif choice == "3":
            if not player.inventory:
                print("You have nothing to sell.")
                continue
            show_price_table(cities)
            print(f"You are in {player.location}. Your inventory: {player.inventory}")
            item = input("What item to sell? ").strip().lower()

            if item not in player.inventory or player.inventory[item] <= 0:
                print("You don’t have any of that item.")
                continue

            try:
                qty = int(input("Quantity: ").strip())
                if qty <= 0:
                    print("Quantity must be positive.")
                    continue
            except ValueError:
                print("Invalid input — please enter a number.")
                continue

            print(game.sell(item, qty))


        elif choice == "4":
            print(f"Profit so far: ${game.profit()}")
        
        elif choice == "5":
            print(f"Final profit: ${game.profit()}")
            print("Thanks for playing City Trader!")
            break

        elif choice == "6":
            if ai_used:
                print("You already used your AI assistant this game.")
                continue

            best_city, best_good, est_profit = suggest_best_move(g, cities, player.location, player.fuel)
            if not best_city:
                print("You can still travel, but no trades look profitable right now.")
                continue

            # spell out the plan
            here = player.location
            price_here = cities[here].goods[best_good]
            price_there = cities[best_city].goods[best_good]
            fuel_cost = g.cities[here][best_city]
            per_unit = price_there - price_here
            max_qty = player.money // price_here  # how many you could buy now
            est_total = max(0, per_unit) * max_qty  # rough upper-bound (ignores fuel)

            print(
                f"🤖 Suggestion:\n"
                f"  • Buy {best_good} in {here} at ${price_here} each.\n"
                f"  • Travel to {best_city} (fuel cost {fuel_cost}).\n"
                f"  • Sell there at ${price_there} each.\n"
                f"  • Profit per unit ≈ ${per_unit}. If you spend all your cash now, "
                f"you could buy ~{max_qty} and gross ≈ ${est_total} before travel cost."
            )
            ai_used = True

        else:
            print("Invalid choice.")



if __name__ == "__main__":
    main()
