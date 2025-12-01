class ActionNode:
    def __init__(self, action, details):
        self.action = action      # e.g. "Travel", "Buy", "Sell"
        self.details = details    # e.g. "Traveled to Berlin"
        self.next = None

class History:
    def __init__(self):
        self.head = None
        self.tail = None

    def add(self, action, details):
        node = ActionNode(action, details)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    def show(self):
        # Let n be the number of actions in history
        # Average-case time complexity: O(n)
        # Worst-case time complexity: O(n)
        
        # Return a list of formatted history strings.
        if not self.head:
            return ["No actions recorded."]
        result = []
        current = self.head
        i = 1
        while current:
            result.append(f"{i}. {current.action}: {current.details}")
            current = current.next
            i += 1
        return result
