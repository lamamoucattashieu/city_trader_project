# city_trader/optimizer.py

# ...existing code...
def suggest_best_move(graph, cities, current_city, fuel_left):
    best_profit = 0
    best_city = None
    best_good = None

    # get shortest fuel cost to every city
    dist, _ = graph.dijkstra(current_city)

    for dest, fuel_cost in dist.items():
        if dest == current_city:
            continue
        if fuel_cost == float('inf') or fuel_cost > fuel_left:
            continue
        if current_city not in cities or dest not in cities:
            continue
        for good, price_here in cities[current_city].goods.items():
            if good in cities[dest].goods:
                margin = cities[dest].goods[good] - price_here - (fuel_cost * 0.5)
                if margin > best_profit:
                    best_profit = margin
                    best_city = dest
                    best_good = good

    return best_city, best_good, best_profit
