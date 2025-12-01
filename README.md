City Trader

A simple board-style trading game built with Python.
Important: The interface only works correctly when run inside WSL (Ubuntu on Windows).
Do not use Windows Python or macOS — the UI will break.

Requirements:

Run these inside WSL:

pip install game2dboard


(WSL already includes Tkinter support needed for the UI.)

How to Run:

From the project root, inside WSL, run:

python -m city_trader.ui


This will launch the interactive board game window.

Important Notes:

Use WSL only!
The game interface does not render properly on native Windows or macOS.

Do not run the game through VS Code’s “Run” button.
Use a real terminal inside WSL.

Make sure the folder structure is unchanged so the game can load its world data.
