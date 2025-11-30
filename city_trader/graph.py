class Graph:
    def __init__(self):
        # adjacency list: { city: { neighbor: fuel_cost } }
        self.cities = {}

    def add_city(self, name):
        if name not in self.cities:
            self.cities[name] = {}

    def add_road(self, city1, city2, fuel_cost):
        self.add_city(city1)
        self.add_city(city2)
        self.cities[city1][city2] = fuel_cost
        self.cities[city2][city1] = fuel_cost  # undirected

    def neighbors(self, city):
        return self.cities.get(city, {}).items()

    def dijkstra(self, source):
        # Let V = number of cities, E = number of roads
        # Average-case time complexity: O((V + E) log V)
        # Worst-case time complexity: O((V + E) log V)

        # Return (dist, prev) where dist[city] is min fuel cost from source, prev is predecessor map.
        import heapq
        if source not in self.cities:
            return {}, {}

        dist = {node: float('inf') for node in self.cities}
        prev = {node: None for node in self.cities}
        dist[source] = 0.0
        pq = [(0.0, source)]

        while pq:
            d, u = heapq.heappop(pq)
            if d != dist.get(u, float('inf')):
                continue
            for v, cost in self.cities.get(u, {}).items():
                try:
                    cost_v = float(cost)
                except Exception:
                    continue
                nd = d + cost_v
                if nd < dist.get(v, float('inf')):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev
