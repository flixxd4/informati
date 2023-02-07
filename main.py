import tkinter as tk
from FHGO import FHGO

root = tk.Tk()
root.title("Go Game")
go_root = FHGO(root=root)

go_root.SetGameSettings("/Users/felixhempel/PycharmProjects/informatik/img/image.png", "/Users/felixhempel/PycharmProjects/informatik/img/stone.png")
go_root.startplaymenu()

root.mainloop()

