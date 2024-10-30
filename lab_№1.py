import tkinter as tk
import math


def move():
    global angle
    x = 300 + 200 * math.cos(math.radians(angle))
    y = 300 + 200 * math.sin(math.radians(angle))
    canvas.coords(small_circ, x - 5, y - 5, x + 5, y + 5)
    canvas.after(5, move)
    angle += 1


root = tk.Tk()

canvas = tk.Canvas(root, width=600, height=600)
canvas.pack()

big_circ = canvas.create_oval(100, 500, 500, 100)
small_circ = canvas.create_oval(305, 95, 295, 105, fill='red')
angle = 0

move()

root.mainloop()
