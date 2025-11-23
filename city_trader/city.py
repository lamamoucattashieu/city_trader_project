class City:
    def __init__(self, name, goods):
        """
        name: str — city name
        goods: dict — items and their prices, e.g. {'wheat': 30, 'iron': 50}
        """
        self.name = name
        self.goods = goods

    def __repr__(self):
        return f"City({self.name}, goods={self.goods})"
