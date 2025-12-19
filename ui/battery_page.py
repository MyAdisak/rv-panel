import tkinter as tk
from tkinter import Frame, Label

BG = "#0d0d0d"
CARD = "#1a1a1a"
TEXT = "#ffffff"
MUTED = "#888888"
ACCENT = "#2B6DFF"


class BatteryPage(Frame):
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
            header, text="Battery Status",
            font=("SF Pro Display", 24, "bold"),
            bg=BG, fg=TEXT
        ).pack(side="left", padx=10)

        # ---------- 3 CARDS ----------
        row = Frame(self, bg=BG)
        row.pack(pady=20)

        self.card12 = self._battery_card(row, "Battery 12V", "12")
        self.card24 = self._battery_card(row, "Battery 24V", "24")
        self.card48 = self._battery_card(row, "Battery 48V", "48")

        self.card12.grid(row=0, column=0, padx=15)
        self.card24.grid(row=0, column=1, padx=15)
        self.card48.grid(row=0, column=2, padx=15)

    # ---------- CREATE CARD ----------
    def _battery_card(self, parent, title, key):
        f = Frame(parent, bg=CARD, width=240, height=230)
        f.pack_propagate(False)  # ใช้ขนาดจริง

        # title
        Label(
            f, text=title,
            font=("SF Pro Display", 14),
            bg=CARD, fg=MUTED
        ).pack(pady=(12, 4))

        # SOC
        soc = Label(
            f, text="0%",
            font=("SF Pro Display", 40, "bold"),
            bg=CARD, fg=TEXT
        )
        soc.pack(pady=(0, 10))

        # voltage
        volt = Label(
            f, text="0.0 V",
            font=("SF Pro Display", 16),
            bg=CARD, fg=MUTED
        )
        volt.pack(pady=3)

        # current
        curr = Label(
            f, text="0.0 A",
            font=("SF Pro Display", 16),
            bg=CARD, fg=MUTED
        )
        curr.pack(pady=3)

        # power
        power = Label(
            f, text="0 W",
            font=("SF Pro Display", 16),
            bg=CARD, fg=MUTED
        )
        power.pack(pady=3)

        # เก็บ label ไว้อัปเดต
        f.labels = {
            "key": key,
            "soc": soc,
            "volt": volt,
            "curr": curr,
            "power": power,
        }

        return f

    # ---------- UPDATE DATA ----------
    def update_data(self, st):
        cards = [self.card12, self.card24, self.card48]

        for card in cards:
            key = card.labels["key"]

            if key == "12":
                soc = st.batt12_soc
                volt = st.batt12_volt
                curr = st.batt12_curr
            elif key == "24":
                soc = st.batt24_soc
                volt = st.batt24_volt
                curr = st.batt24_curr
            else:
                soc = st.batt48_soc
                volt = st.batt48_volt
                curr = st.batt48_curr

            power = volt * curr

            # update text
            card.labels["soc"].config(text=f"{int(soc)}%")
            card.labels["volt"].config(text=f"{volt:.2f} V")
            card.labels["curr"].config(text=f"{curr:.2f} A")
            card.labels["power"].config(text=f"{power:.0f} W")

            # color logic
            if curr > 1:
                card.labels["curr"].config(fg="#00ff99")   # charging green
            elif curr < -1:
                card.labels["curr"].config(fg="#ff4444")   # discharging red
            else:
                card.labels["curr"].config(fg=MUTED)

    def on_show(self):
        self.update_data(self.state)

