import tkinter as tk
from tkinter import Frame, Label, Button

BG = "#0d0d0d"
CARD = "#1a1a1a"
TXT = "#ffffff"
ACCENT = "#00ff99"


class MenuPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ---------- TITLE ----------
        Label(
            self,
            text="MENU",
            bg=BG,
            fg=ACCENT,
            font=("SF Pro Display", 28, "bold")
        ).pack(pady=(30, 20))

        # ---------- GRID ----------
        grid = Frame(self, bg=BG)
        grid.pack(expand=True)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # ---------- BUTTONS ----------
        self._menu_btn(grid, "INVERTER", "InverterPage", 0, 0)
        self._menu_btn(grid, "BATTERY", "BatteryPage", 0, 1)

        self._menu_btn(grid, "LIGHTING", "LightingPage", 1, 0)
        self._menu_btn(grid, "SOLAR", "SolarPage", 1, 1)

        self._menu_btn(grid, "SETTINGS", "SettingsPage", 2, 0)

        # ---------- BACK ----------
        Button(
            self,
            text="◀ BACK",
            command=lambda: controller.show_frame("MainPage"),
            bg=CARD,
            fg=TXT,
            font=("SF Pro Display", 14, "bold"),
            bd=0,
            padx=30,
            pady=15
        ).pack(pady=20)

    def _menu_btn(self, parent, text, page, r, c):
        Button(
            parent,
            text=text,
            command=lambda: self.controller.show_frame(page),
            bg=CARD,
            fg=TXT,
            font=("SF Pro Display", 18, "bold"),
            bd=0,
            width=12,
            height=3
        ).grid(row=r, column=c, padx=15, pady=15)
