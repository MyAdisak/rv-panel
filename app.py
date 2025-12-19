import tkinter as tk
from tkinter import ttk

from services.state import AppState
from ui.main_page import MainPage
from ui.lighting_page import LightingPage
from ui.solar_page import SolarPage
from ui.inverter_page import InverterPage
from ui.battery_page import BatteryPage
from ui.settings_page import SettingsPage
from ui.menu_page import MenuPage

UI_REFRESH_MS = 500
LOGIC_TICK_MS = 1000


class RVApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RV Control Panel")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.colors = {
            "bg": "#0d0d0d",
            "card": "#1a1a1a",
            "primary": "#ffffff",
            "muted": "#777777",
        }

        self.state = AppState()
        self._theme()

        container = ttk.Frame(self, style="Root.TFrame")
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}
        self.active_page = None

        pages = {
            "MainPage": MainPage,
            "MenuPage": MenuPage,
            "LightingPage": LightingPage,
            "SolarPage": SolarPage,
            "InverterPage": InverterPage,
            "BatteryPage": BatteryPage,
            "SettingsPage": SettingsPage,
        }

        for name, Page in pages.items():
            frame = Page(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

        self.after(200, self._logic_loop)
        self.after(200, self._ui_loop)

    def _theme(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Root.TFrame", background=self.colors["bg"])
        s.configure("TLabel", background=self.colors["bg"], foreground=self.colors["primary"])

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        self.active_page = frame
        if hasattr(frame, "on_show"):
            frame.on_show()

    def _logic_loop(self):
        try:
            self.state.tick()
        except Exception as e:
            print("[LOGIC ERROR]", e)

        self.after(LOGIC_TICK_MS, self._logic_loop)

    def _ui_loop(self):
        if self.active_page and hasattr(self.active_page, "update_data"):
            try:
                self.active_page.update_data(self.state)
            except Exception as e:
                print("[UI ERROR]", e)

        self.after(UI_REFRESH_MS, self._ui_loop)


if __name__ == "__main__":
    app = RVApp()
    app.mainloop()
