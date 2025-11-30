from game2dboard import Board
from tkinter import simpledialog, Tk
from pathlib import Path
import json
import math
import random
import os
import sys

from city_trader.graph import Graph
from city_trader.city import City
from city_trader.player import Player
from city_trader.game import Game
from city_trader.optimizer import suggest_best_move

# loading the world data 
world_path = Path(__file__).parent / "data" / "world.json"
try:
    world = json.loads(world_path.read_text(encoding="utf-8"))
except Exception:
    world = {"cities": {}, "roads": []}

g = Graph()
for road in world.get("roads", []):
    try:
        a, b, cost = road
        g.add_road(a, b, cost)
    except Exception:
        continue

cities = {name: City(name, goods) for name, goods in world.get("cities", {}).items()}
start_city = random.choice(list(cities.keys())) if cities else "Paris"
player = Player(start_city, fuel=100, money=500)
game = Game(g, cities, player)

#  Grid sizing (decide rows/cols before Board)
n = max(1, len(cities))
# place cities in a compact grid determined by number of cities
grid_side = math.ceil(math.sqrt(n))
grid_rows = max(6, min(12, grid_side + 1))          # keep rows small but >=6
grid_cols = max(10, min(28, grid_side * 2))         # wider grid for labels

# reduce total cells if there are very few cities to make cells larger
if n <= 4:
    grid_rows = max(6, 6)
    grid_cols = max(8, 8)
elif n <= 9:
    grid_rows = max(6, 7)
    grid_cols = max(10, 10)

# Layout helper (must exist before Board) 
def compute_positions_fixed(graph: Graph, rows: int, cols: int):
    # Deterministic even grid placement: spreads N nodes across rows/cols so all are visible.S
    nodes = list(getattr(graph, "cities", {}).keys())
    if not nodes:
        return {}
    m = len(nodes)
    # choose a small internal grid to place nodes (grid_r x grid_c)
    grid_r = math.ceil(math.sqrt(m))
    grid_c = math.ceil(m / grid_r)
    positions = {}
    for i, name in enumerate(nodes):
        r_idx = i // grid_c
        c_idx = i % grid_c
        if grid_r > 1:
            r = 1 + int(r_idx * (rows - 3) / max(1, grid_r - 1))
        else:
            r = rows // 2
        if grid_c > 1:
            c = 1 + int(c_idx * (cols - 3) / max(1, grid_c - 1))
        else:
            c = cols // 2
        positions[name] = (min(rows - 2, max(1, r)), min(cols - 2, max(1, c)))
    return positions

# Board (compute cell_size to maximize size but fit screen)
board = Board(grid_rows, grid_cols)
_original_cell_size = getattr(board, "cell_size", 35)
_original_margin = getattr(board, "margin", 10)

MIN_CELL = 16
MAX_CELL = 96

try:
    _root_tmp = Tk()
    sw, sh = _root_tmp.winfo_screenwidth(), _root_tmp.winfo_screenheight()
    _root_tmp.destroy()
    usable_w = max(300, sw - 160)
    usable_h = max(240, sh - 200)
    # compute largest cell that fits both directions
    cell_w = usable_w // (board.ncols + 2)
    cell_h = usable_h // (board.nrows + 4)
    cell_size = max(MIN_CELL, min(MAX_CELL, min(cell_w, cell_h)))
    board.cell_size = cell_size
    board.margin = max(4, int(cell_size // 6))
except Exception:
    board.cell_size = _original_cell_size
    board.margin = _original_margin

board.title = "City Trader (Board Game)"
board.create_output(background="white")
board.output = board.print

POS = compute_positions_fixed(g, board.nrows, board.ncols)

# Game state
_game_over = False

# Helpers
def _clear():
    for r in range(board.nrows):
        for c in range(board.ncols):
            board[r][c] = ""

def neighbors(city):
    return set(g.cities.get(city, {}).keys())

def neighbor_text(city):
    return ", ".join(f"{n} ({g.cities[city][n]} fuel)" for n in g.cities.get(city, {})) or "(none)"

def get_input(prompt):
    try:
        val = simpledialog.askstring("City Trader", prompt)
        return val.strip() if val else None
    except Exception:
        return None

def check_game_over():
    # Let d = degree of the current city (number of neighbors)
    # Average-case time complexity: O(d)
    # Worst-case time complexity: O(d)
    # Check if player can reach any connected city. If not, end game.
    global _game_over
    here = game.player.location
    reach = neighbors(here)
    can_travel = False
    for city in reach:
        fuel_cost = g.cities[here].get(city, float('inf'))
        if fuel_cost <= game.player.fuel:
            can_travel = True
            break
    if not can_travel:
        _game_over = True
        end_game()

def end_game():
    # Let H be the number of actions in history
    # Average-case time complexity: O(H)
    # Worst-case time complexity: O(H)
    # Display game over screen with history and final profit.
    _clear()
    board.output("GAME OVER - Out of fuel!\n")
    try:
        node = game.history.head
        lines = ["Your Journey:"]
        i = 1
        while node:
            lines.append(f"{i}. {node.action}: {node.details}")
            node = node.next
            i += 1
        lines.append(f"\nFinal Profit: ${game.profit()}")
        lines.append("Thanks for playing!")
        board.output("\n".join(lines))
    except Exception:
        board.output(f"Final Profit: ${game.profit()}\nThanks for playing!")

#  Display 
def draw_world(message=None):
    # Let N be the number of cities
    # Average-case time complexity: O(N)
    # Worst-case time complexity: O(N)

    if _game_over:
        return
    
    _clear()
    here = game.player.location
    reach = neighbors(here)
    for name, (r, c) in POS.items():
        if name == here:
            board[r][c] = f"[P]{name}"
        elif name in reach:
            board[r][c] = f"[>]{name}"
        else:
            board[r][c] = f"[C]{name}"

    info = (
        f"\nYou are in {here}\n"
        f"Money: ${game.player.money} | Fuel: {game.player.fuel}\n"
        f"Connected cities: {neighbor_text(here)}\n"
        "Click a [>] city to travel.\n\n"
        "Controls:\n"
        "  P - Show prices\n"
        "  B - Buy items\n"
        "  S - Sell items\n"
        "  A - Ask AI for trade advice\n"
        "  H - Show travel history\n"
        "  I - View inventory\n"
        "  ENTER - Back to map\n"
        "  Q - Quit\n"
    )
    if message:
        info += "\n" + message
    board.output(info)

#  Gameplay displays 
def show_prices():
    # Let C = number of cities, G = total unique goods
    # Average-case time complexity: O(C·G)
    # Worst-case time complexity: O(C·G)

    goods = sorted({g for c in cities.values() for g in c.goods})
    lines = ["\nMarket Prices:"]
    header = "City".ljust(14) + "".join(g[:10].rjust(10) for g in goods)
    lines.append(header)
    lines.append("-" * len(header))
    for name in sorted(cities):
        row = name.ljust(14)
        for good in goods:
            val = str(cities[name].goods.get(good, "-")).rjust(10)
            row += val
        lines.append(row)
    lines.append("\nPress ENTER to return to the main map.")
    board.output("\n".join(lines))

def show_history():
    # Let H be the number of actions in history
    # Average-case time complexity: O(H)
    # Worst-case time complexity: O(H)

    try:
        node = game.history.head
        lines = ["\nYour Journey:"]
        i = 1
        while node:
            lines.append(f"{i}. {node.action}: {node.details}")
            node = node.next
            i += 1
        lines.append("\nPress ENTER to return.")
        board.output("\n".join(lines))
    except Exception:
        board.output("No history available.")

def show_inventory():
    # Let I be the number of distinct items in the inventory
    # Average-case time complexity: O(I)
    # Worst-case time complexity: O(I)

    inv = getattr(game.player, "inventory", {}) or {}
    lines = ["\nYour Inventory:"]
    if not inv:
        lines.append("  (Empty)")
    else:
        for k, v in inv.items():
            lines.append(f"  - {k}: {v}")
    lines.append("\nPress ENTER to return.")
    board.output("\n".join(lines))

#  Interaction 
def click_city(button, r, c):
    # Let N be the number of cities, d be degree of current city
    # Average-case time complexity: O(N + d)
    # Worst-case time complexity: O(N + d)
    #   (scan POS for clicked city, then possibly scan neighbors for fuel check)
    global _game_over
    if _game_over:
        return
    here = game.player.location
    for name, pos in POS.items():
        if pos == (r, c):
            if name == here:
                board.output("You are already here.")
                return
            if name not in g.cities.get(here, {}):
                board.output("You cannot travel there directly.")
                return
            res = game.travel(name)
            draw_world(res)
            
            # Only end game if travel failed AND player can't go anywhere
            if "Not enough fuel" in res:
                reach = neighbors(game.player.location)
                can_travel = any(
                    g.cities[game.player.location].get(c, float('inf')) <= game.player.fuel
                    for c in reach
                )
                if not can_travel:
                    _game_over = True
                    end_game()
            return

board.on_mouse_click = click_city

def on_key(k):
    # on_key itself is O(1) per press, ignoring the cost of called helpers.
    # The heaviest call it triggers is suggest_best_move, which is:
    #   O((V + E) log V + V·G)  (same as earlier annotation)

    global _game_over
    if _game_over:
        return
    
    k = k.lower()
    if k == "p":
        show_prices()
    elif k == "b":
        here = game.player.location
        goods = cities.get(here, City(here, {})).goods
        if not goods:
            board.output("This city sells nothing.")
            return
        item = get_input(f"Available goods: {list(goods.keys())}\nEnter item to buy:")
        if not item or item.lower() not in goods:
            board.output("Invalid item.")
            return
        qty_txt = get_input("Quantity to buy:")
        if not qty_txt or not qty_txt.isdigit() or int(qty_txt) <= 0:
            board.output("Invalid quantity.")
            return
        res = game.buy(item.lower(), int(qty_txt))
        draw_world(res)
    elif k == "s":
        inv = getattr(game.player, "inventory", {}) or {}
        if not inv:
            board.output("You have nothing to sell.")
            return
        item = get_input(f"Your inventory: {inv}\nEnter item to sell:")
        if not item or item.lower() not in inv or inv.get(item.lower(), 0) <= 0:
            board.output("Invalid item.")
            return
        qty_txt = get_input("Quantity to sell:")
        if not qty_txt or not qty_txt.isdigit() or int(qty_txt) <= 0:
            board.output("Invalid quantity.")
            return
        res = game.sell(item.lower(), int(qty_txt))
        draw_world(res)
    elif k == "a":
        try:
            here = game.player.location
            best_city, best_good, best_profit = suggest_best_move(g, cities, here, game.player.fuel)
        except Exception as e:
            board.output(f"AI suggestion failed: {e}")
            return
        if not best_city or not best_good:
            draw_world("AI Suggestion: No profitable trades found.")
            return
        try:
            ph = cities.get(here).goods.get(best_good)
            pt = cities.get(best_city).goods.get(best_good)
            fc = g.cities.get(here, {}).get(best_city)
            if ph is None or pt is None or fc is None:
                draw_world("AI Suggestion: incomplete data for suggested route.")
                return
            msg = f"AI Suggestion: Buy {best_good} in {here} (${ph}), travel to {best_city} (fuel {fc}), sell for ${pt}."
        except Exception as e:
            board.output(f"AI post-process error: {e}")
            return
        draw_world(msg)
    elif k == "h":
        show_history()
    elif k == "i":
        show_inventory()
    elif k == "\r":
        draw_world("Returned to main map.")
    elif k == "q":
        _game_over = True
        try:
            show_history()
            board.output(f"Final profit: ${game.profit()}\nThanks for playing!")
        except Exception:
            board.output("Thanks for playing!")
        finally:
            try:
                board.stop()
            except Exception:
                pass
    else:
        draw_world("Use valid key.")

board.on_key_press = on_key

# Start
draw_world("Welcome! Click a [>] city to travel or use keys below.")
board.show()