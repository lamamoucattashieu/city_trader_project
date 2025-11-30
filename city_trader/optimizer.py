
def suggest_best_move(graph, cities, current_city, fuel_left):
    # Let V = number of cities, E = number of roads, G = number of goods in the current city
    # Average-case time complexity: O((V + E) log V + V·G)
    # Worst-case time complexity: O((V + E) log V + V·G)
    #   Explanation:
    #     - Dijkstra = O((V + E) log V)
    #     - Nested loop: for each destination city, check up to G goods → O(V·G)
    #     - All dictionary lookups inside loops are O(1)
    
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
