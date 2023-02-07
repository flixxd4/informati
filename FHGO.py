import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import requests
import ast

class FHGO:
    def __init__(self, root, white_begins=True, color="#9c6644", safefile="go.txt"):
        self.safefile = safefile
        self.color = color
        self.white = white_begins
        self.root = root

    def SetGameSettings(self, white_stone_path, black_stone_path, ):
        white_stone = Image.open(white_stone_path)
        black_stone = Image.open(black_stone_path)
        Online = Image.open("/Users/felixhempel/PycharmProjects/informatik/img/browser.png")
        offline = Image.open("/Users/felixhempel/PycharmProjects/informatik/img/no-wifi.png")

        self.online = ImageTk.PhotoImage(Online.resize((50, 50), Image.ANTIALIAS))
        self.offline = ImageTk.PhotoImage(offline.resize((50, 50), Image.ANTIALIAS))
        self.white_sized = ImageTk.PhotoImage(white_stone.resize((50, 50), Image.ANTIALIAS))
        self.black_sized = ImageTk.PhotoImage(black_stone.resize((50, 50), Image.ANTIALIAS))

        self.online_player = ""
        self.playsonline = False
        self.win = False

    def startplaymenu(self):
        self.root.config(bg=self.color)

        ab = tk.Label(self.root, text="Choose Gamemode", bg=self.color, fg="black")
        ab.grid(column=0, row=0, pady=10, padx=10)
        cd = tk.Button(self.root, image=self.online, command=lambda: delandload("online"))
        cd.grid(column=0, row=1)
        fg = tk.Button(self.root, image=self.offline, command=lambda: delandload("offline"))
        fg.grid(column=1, row=1, padx=10)
        de = tk.Label(self.root, text="Online", bg=self.color, fg="black")
        de.grid(column=0, row=2)
        ha =tk.Label(self.root, text="Offline", bg=self.color, fg="black")
        ha.grid(column=1, row=2)

        objects = [ab, cd, fg, de, ha]

        def delandload(mode):
            for object in objects:
                object.grid_forget()
            if mode == "offline":
                self.StartFHGoGame()
            else:
                self.online_mode()


    def online_mode(self):
        self.playsonline = True

        self.root.config(bg=self.color)

        label1 = tk.Label(self.root, text="Type in Your gamesession name", bg=self.color)
        label1.pack(pady=10)
        text = tk.Entry(self.root)
        text.pack(padx=10)
        button1 = tk.Button(self.root, text="Create session", bg=self.color, command= lambda: creategameses(text))
        button1.pack(pady=10)
        button2 = tk.Button(self.root, text="join session", bg=self.color, command= lambda: joings(text))
        button2.pack(pady=10)

        widgets = [label1, text, button1, button2]

        def delete():
            for widget in widgets:
                widget.pack_forget()


        def creategameses(gs):
            self.online_player = 1
            requests.get(f"http://felixhempel.xyz/go/gs/?creategs={gs.get()}")
            delete()
            self.StartFHGoGame()

        def joings(gs):
            self.online_player = 2
            req = requests.get(f"http://felixhempel.xyz/go/gs/?joings={gs.get()}")
            if req.text == "true":
                delete()
                self.StartFHGoGame()

    def StartFHGoGame(self, gridsize=9, debugmode=None):
        frame = tk.Frame(self.root)
        frame.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(frame, width=gridsize * 50, height=gridsize * 50, bg=self.color)
        canvas.pack(fill="both", expand=True)

        for i in range(gridsize + 1):
            canvas.create_line(50 * i, 0, 50 * i, gridsize * 50, fill="#b08968")
            canvas.create_line(0, 50 * i, gridsize * 50, 50 * i, fill="#b08968")

        main_menu = tk.Menu(self.root)
        filemenu = tk.Menu(main_menu, tearoff=0)
        filemenu.add_command(label="Safe", command=lambda: safegame())
        filemenu.add_command(label="Load", command=lambda: loadgame())
        filemenu.add_command(label="New game", command=lambda: ())
        main_menu.add_cascade(label="file", menu=filemenu)
        self.root.config(menu=main_menu)

        self.player = np.zeros((gridsize, gridsize))

        #stone events
        def detcol(row, col, stone):
            if self.player[row][col - 1] == stone:
                for col1 in range(col + 1, gridsize):
                    if self.player[row][col1] == stone:
                        return True
                    elif not (row, col1) in self.player_to_del:
                        self.player_to_del.append((row, col1))
                    elif self.player[row][col1] == 0:
                        break

        def detrow(row, col, stone):
            detected_rows = 0
            if self.player[row - 1][col] == stone:
                for row1 in range(row + 1, gridsize):
                    if self.player[row1][col] == stone:
                        if row1 - row > 1 and self.player[row][col - 1] == stone:
                            for row2 in range(row +1, row1):
                                if not (row2, col) in self.player_to_del:
                                    self.player_to_del.append((row2, col))
                                if detcol(row2, col, stone):
                                    detected_rows += 1
                            if detected_rows == (row1 - 1) - row:
                                return True
                        else:
                            return True
                    elif self.player[row1][col] == 0:
                        break


        def SourroundCol(row, col, stone):
            detected_rows = 0
            if self.player[row][col - 1] == stone:
                for col1 in range(col + 1, gridsize):
                    if self.player[row][col1] == stone:
                        for col2 in range(col, col1):
                            if not (row, col2) in self.player_to_del:
                                self.player_to_del.append((row, col2))
                            if detrow(row, col2, stone):
                                detected_rows += 1
                        if detected_rows == col1 - col:
                            for deleting in self.player_to_del:
                                row, col = deleting
                                self.loosestone = self.player[row][col]
                                self.player[row][col] = 0
                                delete = canvas.find_closest(col * 50 + 50, row* 50 + 50)
                                canvas.delete(delete)
                                wingame()
                    elif self.player[row][col1] == 0:
                        break

        def CheckRules(stone, stone2):
            self.player_to_del = []
            for row in range(gridsize):
                for col in range(gridsize):
                    if self.player[row][col] == stone2 and self.player[row][col - 1] == stone:
                        SourroundCol(row, col, stone)
                        if debugmode:
                            for deleting in self.player_to_del:
                                y, x = deleting
                                canvas.create_rectangle(x * 50, y * 50, x * 50 + 20, y * 50 + 20, fill="red")


        def image_stone():
            for i in range(0, len(self.player)):
                for f in range(0, len(self.player[i])):
                    if self.player[i][f] == 2:
                        a, = canvas.find_closest(f * 50 + 50, i * 50 + 50)
                        if a < 20:
                            canvas.create_image(f * 50 + 50, i * 50 + 50, image=self.black_sized)
                    if self.player[i][f] == 1:
                        a, = canvas.find_closest(f * 50 + 50, i * 50 + 50)
                        if a < 20:
                            canvas.create_image(f * 50+ 50, i * 50 + 50, image=self.white_sized)

        def place_stone(event):
            if not self.win:
                row, col = int((event.y - 25) / 50), int((event.x - 25) / 50)
                self.white = not self.white
                stone = 1 if not self.white else 2
                if self.player[row][col] == 0:
                    self.player[row][col] = stone
                    self.root.after(300, lambda: CheckRules(1, 2))
                    self.root.after(300, lambda: CheckRules(2, 1))
                    image_stone()
                    if self.playsonline:
                        self.sendstones()
        def wingame():
            if self.loosestone == 2:
                text = "white"
            elif self.loosestone == 1:
                text = "black"
            if self.playsonline:
                self.player = np.zeros((gridsize, gridsize))
                self.sendstones()
            self.win = True
            winlabel = tk.Label(self.root, text=f"{text} wins!", font="sans-serif")
            winlabel.place(x=gridsize * 50 / 2, y=gridsize * 50 / 2)

        def loadgame():
            with open(self.safefile, "r") as f:
                self.player = eval(f.read())
                image_stone()

        def safegame():
            global vanilla_arr
            with open(self.safefile, "w") as f:
                f.write(str(vanilla_arr))

        def getstones():
            array = requests.get("http://felixhempel.xyz/go/")
            try:
                self.player = np.array(ast.literal_eval(array.text))
            except:
                print("error")

            image_stone()
            if not self.win:
                self.root.after(100, lambda: getstones())

        canvas.bind("<Button-1>", place_stone)
        if self.playsonline == True:
            getstones()

    def sendstones(self):
        msg = str(self.player).replace(" ", ",").replace("\n", " ")
        requests.post(f'http://felixhempel.xyz/go/?post={msg}')


