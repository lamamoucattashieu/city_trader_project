# -*- coding: utf-8 -*-
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

# ---------- Load world ----------
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
start_city = next(iter(cities.keys()), "Paris")
player = Player(start_city, fuel=100, money=500)
game = Game(g, cities, player)

# ---------- Layout helper (must exist before Board) ----------
def compute_positions(graph: Graph, rows: int, cols: int):
    nodes = list(getattr(graph, "cities", {}).keys())
    if not nodes:
        return {}
    if len(nodes) == 1:
        return {nodes[0]: (rows // 2, cols // 2)}

    W, H = max(2, cols - 2), max(2, rows - 2)
    pos = {n: [random.uniform(1, W), random.uniform(1, H)] for n in nodes}
    edges = []
    for u in nodes:
        for v, cost in graph.cities.get(u, {}).items():
            if (v, u) in [(e[0], e[1]) for e in edges]:
                continue
            try:
                w = 1.0 / max(1.0, float(cost))
            except Exception:
                w = 1.0
            edges.append((u, v, w))

    def dist(a, b):
        dx = pos[a][0] - pos[b][0]
        dy = pos[a][1] - pos[b][1]
        return math.hypot(dx, dy) + 1e-6

    def repel(d): return 2.0 / (d * d + 1e-3)
    def attract(d, w): return w * (d * d) / 2.0

    for _ in range(100):
        disp = {n: [0.0, 0.0] for n in nodes}
        for i, u in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                d = dist(u, v)
                f = repel(d)
                dx = pos[u][0] - pos[v][0]; dy = pos[u][1] - pos[v][1]
                if d > 0:
                    fx, fy = f * dx / d, f * dy / d
                    disp[u][0] += fx; disp[u][1] += fy
                    disp[v][0] -= fx; disp[v][1] -= fy
        for (u, v, w) in edges:
            d = dist(u, v)
            f = attract(d, w)
            dx = pos[u][0] - pos[v][0]; dy = pos[u][1] - pos[v][1]
            if d > 0:
                fx, fy = f * dx / d, f * dy / d
                disp[u][0] -= fx; disp[u][1] -= fy
                disp[v][0] += fx; disp[v][1] += fy
        for n in nodes:
            pos[n][0] += 0.05 * disp[n][0]
            pos[n][1] += 0.05 * disp[n][1]
            pos[n][0] = min(max(pos[n][0], 1), W)
            pos[n][1] = min(max(pos[n][1], 1), H)

    mapping = {}
    for n in nodes:
        r = 1 + int((pos[n][1] / max(1.0, W)) * (rows - 3))
        c = 1 + int((pos[n][0] / max(1.0, H)) * (cols - 3))
        mapping[n] = (min(rows - 2, max(1, r)), min(cols - 2, max(1, c)))
    return mapping

# ...existing code...
# ---------- Board ----------
# fewer cells and larger boxes for clearer UI
board = Board(12, 20)          # was Board(20, 36) — fewer rows/cols => larger visible cells
_original_cell_size = getattr(board, "cell_size", 35)
_original_margin = getattr(board, "margin", 10)

# compute a screen-aware cell size but cap it so boxes are large
MAX_CELL = 48                  # maximum pixel size per cell (increase if you want bigger boxes)
MIN_CELL = 12                  # minimum allowed cell size

try:
    _root_tmp = Tk()
    sw, sh = _root_tmp.winfo_screenwidth(), _root_tmp.winfo_screenheight()
    _root_tmp.destroy()
    # conservative bounds to fit the new smaller grid
    max_cell_w = max(MIN_CELL, min(MAX_CELL, sw // (board.ncols + 4)))
    max_cell_h = max(MIN_CELL, min(MAX_CELL, sh // (board.nrows + 6)))
    board.cell_size = min(max_cell_w, max_cell_h)
except Exception:
    board.cell_size = _original_cell_size

board.title = "City Trader (Board Game)"
board.margin = _original_margin
board.create_output(background="white")
board.output = board.print

# recompute positions for the new grid size
POS = compute_positions(g, board.nrows, board.ncols)

# ---------- Compact-view toggle (no restart, preserves state) ----------
_compact_view = False

def toggle_compact_view():
    """Toggle compact info (hide long controls/help). Preserves game state."""
    global _compact_view
    _compact_view = not _compact_view
    if _compact_view:
        draw_world("Compact view: controls hidden. Press V to restore.")
    else:
        draw_world("Controls restored.")

# ---------- Helpers ----------
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

# ---------- Display ----------
def draw_world(message=None):
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

    if _compact_view:
        # very small footer so output area stays minimal
        info = f"\n{here} | ${game.player.money} | Fuel: {game.player.fuel}   (V restores controls)"
    else:
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
            "  V - Toggle compact view (hides this menu)\n"
            "  ENTER - Back to map\n"
            "  Q - Quit\n"
        )
    if message:
        info += "\n" + message
    board.output(info)

# ---------- Gameplay displays ----------
def show_prices():
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
    inv = getattr(game.player, "inventory", {}) or {}
    lines = ["\nYour Inventory:"]
    if not inv:
        lines.append("  (Empty)")
    else:
        for k, v in inv.items():
            lines.append(f"  - {k}: {v}")
    lines.append("\nPress ENTER to return.")
    board.output("\n".join(lines))

# ---------- Interaction ----------
def click_city(button, r, c):
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
            return

board.on_mouse_click = click_city

def on_key(k):
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
    elif k == "v":
        toggle_compact_view()
    elif k == "h":
        show_history()
    elif k == "i":
        show_inventory()
    elif k == "\r":
        draw_world("Returned to main map.")
    elif k == "q":
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

# ---------- Start ----------
draw_world("Welcome! Click a [>] city to travel or use keys below.")
board.show()