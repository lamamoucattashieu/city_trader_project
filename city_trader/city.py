class City:
    def __init__(self, name, goods):
        # average time complexity: O(n)
        # worst case time complexity: O(n)
        self.name = name
        self.goods = goods

    def __repr__(self):
        return f"City({self.name}, goods={self.goods})"
