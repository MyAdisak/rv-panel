import tkinter as tk
from tkinter import Frame, Label

BG = "#0d0d0d"
CARD = "#1a1a1a"
TEXT = "#ffffff"
MUTED = "#888888"
ACCENT = "#2B6DFF"


class SolarPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.state = controller.state

        # ---------- HEADER ----------
        header = Frame(self, bg=BG)
        header.pack(fill="x", pady=(10, 5))

        tk.Button(
            header,
            text="← Back",
            command=lambda: controller.show_frame("MainPage"),
            font=("SF Pro Display", 12),
            bg="#1b1b1b",
            fg=TEXT,
            bd=0, padx=10, pady=4
        ).pack(side="left", padx=10)

        Label(
            header, 
            text="Solar Input / MPPT",
            font=("SF Pro Display", 24, "bold"),
            bg=BG, fg=TEXT
        ).pack(side="left", padx=10)

        # ---------- MAIN CARD ----------
        card = Frame(self, bg=CARD, width=350, height=260)
        card.pack(pady=35)
        card.pack_propagate(False)

        Label(
            card, text="PV Status",
            font=("SF Pro Display", 16), bg=CARD, fg=MUTED
        ).pack(pady=(15, 8))

        # PV Voltage
        self.lbl_volt = Label(
            card, text="0.0 V",
            font=("SF Pro Display", 22, "bold"), bg=CARD, fg=TEXT
        )
        self.lbl_volt.pack(pady=5)

        # PV Current
        self.lbl_curr = Label(
            card, text="0.0 A",
            font=("SF Pro Display", 20), bg=CARD, fg=TEXT
        )
        self.lbl_curr.pack(pady=5)

        # Solar Power
        self.lbl_power = Label(
            card, text="0 W",
            font=("SF Pro Display", 26, "bold"), bg=CARD, fg=ACCENT
        )
        self.lbl_power.pack(pady=12)

        # MPPT Temp
        self.lbl_temp = Label(
            card, text="Temp: -- °C",
            font=("SF Pro Display", 16), bg=CARD, fg=MUTED
        )
        self.lbl_temp.pack(pady=3)

        # PV1 / PV2
        self.lbl_pv1 = Label(
            card, text="PV1: -- V",
            font=("SF Pro Display", 15), bg=CARD, fg=MUTED
        )
        self.lbl_pv1.pack(pady=2)

        self.lbl_pv2 = Label(
            card, text="PV2: -- V",
            font=("SF Pro Display", 15), bg=CARD, fg=MUTED
        )
        self.lbl_pv2.pack(pady=2)

        # Charging State
        self.lbl_state = Label(
            card, text="Idle",
            font=("SF Pro Display", 18), bg=CARD, fg="#00ffaa"
        )
        self.lbl_state.pack(pady=10)

    # ---------- UPDATE ----------
    def update_data(self, st):

        # ใช้ค่าแบบ simulate (ค่าจริงจะอ่านจาก sensor ภายหลัง)
        volt = getattr(st, "solar_volt", 18.5)
        curr = getattr(st, "solar_curr", 3.2)
        power = volt * curr
        temp = getattr(st, "solar_temp", 38)

        pv1 = getattr(st, "pv1_volt", volt)
        pv2 = getattr(st, "pv2_volt", volt - 1)

        # Update text
        self.lbl_volt.config(text=f"{volt:.1f} V")
        self.lbl_curr.config(text=f"{curr:.2f} A")
        self.lbl_power.config(text=f"{power:.0f} W")
        self.lbl_temp.config(text=f"Temp: {temp:.1f} °C")
        self.lbl_pv1.config(text=f"PV1: {pv1:.1f} V")
        self.lbl_pv2.config(text=f"PV2: {pv2:.1f} V")

        # State color
        if curr > 0.5:
            self.lbl_state.config(text="Charging", fg="#00ff99")
        else:
            self.lbl_state.config(text="Idle", fg=MUTED)

    def on_show(self):
        self.update_data(self.state)
