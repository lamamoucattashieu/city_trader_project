# City Trader Project

A Python trading game based on a city graph. Features a console interface and an optional graphical board interface.

# Description

The goal of the game is to make profit by moving between connected cities, buying goods at low prices, and selling them at higher prices. Each move costs fuel, so you have to plan routes carefully and pay attention to market prices.

# Notes
The graphical board interface uses the game2dboard library, it uses Python's built-in Tkinter module.

# Tkinter warning

If your Python installation does not include Tkinter, the graphical interface will not work.
The game interface does not render properly on native Windows or macOS. For best user experience, use WSL. 

Do not run the game through VS Code’s “Run” button.
Use a real terminal inside WSL.

Make sure the folder structure is unchanged so the game can load its world data.
