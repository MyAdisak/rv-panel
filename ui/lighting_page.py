import tkinter as tk
from tkinter import Frame, Label, Button

DARK_BG = "#0d0d0d"
TEXT = "#eaeaea"
ACCENT = "#2B6DFF"


class LightingPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self.state = controller.state

        # ---------- HEADER ----------
        header = Frame(self, bg=DARK_BG)
        header.pack(fill="x", pady=(10, 5))

        Button(
            header,
            text="← Back",
            command=lambda: controller.show_frame("MainPage"),
            font=("SF Pro Display", 12),
            bg="#1b1b1b",
            fg=TEXT,
            bd=0,
            padx=10,
            pady=4
        ).pack(side="left", padx=10)

        Label(
            header,
            text="Lighting & 12V System",
            font=("SF Pro Display", 20, "bold"),
            bg=DARK_BG,
            fg=TEXT,
        ).pack(side="left", padx=10)

        # ---------- MAIN 12V ----------
        main_frame = Frame(self, bg=DARK_BG)
        main_frame.pack(pady=10)

        self.btn_main_12v = self._make_toggle(main_frame, "ไฟหลอดนีออน", "light_main_12v")
        self.btn_main_12v.grid(row=0, column=0, padx=10, pady=10)

        # ---------- ZONES ----------
        grid = Frame(self, bg=DARK_BG)
        grid.pack(pady=10)

        self.btn_downlight = self._make_toggle(grid, "Downlight", "light_downlight")
        self.btn_hall = self._make_toggle(grid, "Hall Center", "light_hall")
        self.btn_ambient = self._make_toggle(grid, "Ambient", "light_ambient")
        self.btn_outdoor = self._make_toggle(grid, "Outdoor", "light_outdoor")

        self.btn_downlight.grid(row=0, column=0, padx=10, pady=10)
        self.btn_hall.grid(row=0, column=1, padx=10, pady=10)
        self.btn_ambient.grid(row=1, column=0, padx=10, pady=10)
        self.btn_outdoor.grid(row=1, column=1, padx=10, pady=10)

        # ---------- Init ----------
        self.refresh()

    # ---------- Create Toggle Button ----------
    def _make_toggle(self, parent, text, attr):
        btn = Button(
            parent,
            text=text,
            font=("SF Pro Display", 14),
            width=14,
            bg="#1b1b1b",
            fg=TEXT,
            bd=0,
            command=lambda b=attr: self._toggle(b)
        )
        btn.attr = attr
        return btn

    # ---------- Toggle Handler ----------
    def _toggle(self, attr):
        current = getattr(self.state, attr)
        self.state.set_light(attr, not current)

    # ---------- Refresh Button Color ----------
    def refresh(self):
        buttons = [
            self.btn_main_12v,
            self.btn_downlight,
            self.btn_hall,
            self.btn_ambient,
            self.btn_outdoor,
        ]

        for btn in buttons:
            on = getattr(self.state, btn.attr)
            if on:
                btn.config(bg=ACCENT, fg="#ffffff")
            else:
                btn.config(bg="#1b1b1b", fg=TEXT)

    # ---------- Update From AppState ----------
    def update_data(self, st):
        self.refresh()


    # ---------- On Page Show ----------
    def on_show(self):
        self.refresh()
