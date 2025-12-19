import tkinter as tk
from tkinter import Frame, Label

BG = "#0d0d0d"
CARD = "#1a1a1a"
TEXT = "#ffffff"
MUTED = "#888888"
ACCENT = "#2B6DFF"
RED = "#ff4444"
GREEN = "#00ff99"
YELLOW = "#ffaa00"


class PowerPage(Frame):
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
            text="AC Power / Inverter",
            font=("SF Pro Display", 24, "bold"),
            bg=BG, fg=TEXT
        ).pack(side="left", padx=10)

        # ---------- GRID ----------
        grid = Frame(self, bg=BG)
        grid.pack(pady=25)

        self.card_ac = self._make_card(grid, "AC Input")
        self.card_inverter = self._make_card(grid, "Inverter Output")
        self.card_state = self._make_card(grid, "System Flow")

        self.card_ac.grid(row=0, column=0, padx=15)
        self.card_inverter.grid(row=0, column=1, padx=15)
        self.card_state.grid(row=0, column=2, padx=15)

    # ---------- CARD TEMPLATE ----------
    def _make_card(self, parent, title):
        f = Frame(parent, bg=CARD, width=260, height=280)
        f.pack_propagate(False)

        Label(f, text=title, font=("SF Pro Display", 18), bg=CARD, fg=MUTED).pack(pady=(12, 5))

        main = Label(f, text="--", font=("SF Pro Display", 32, "bold"), bg=CARD, fg=TEXT)
        main.pack(pady=10)

        sub1 = Label(f, text="--", font=("SF Pro Display", 16), bg=CARD, fg=MUTED)
        sub1.pack(pady=3)

        sub2 = Label(f, text="--", font=("SF Pro Display", 16), bg=CARD, fg=MUTED)
        sub2.pack(pady=3)

        sub3 = Label(f, text="--", font=("SF Pro Display", 16), bg=CARD, fg=MUTED)
        sub3.pack(pady=3)

        f.labels = {
            "main": main,
            "sub1": sub1,
            "sub2": sub2,
            "sub3": sub3
        }
        return f

    # ---------- UPDATE ----------
    def update_data(self, st):

        # ----- AC Input -----
        p_ac = st.ac_in_volt * st.ac_in_curr
        c1 = self.card_ac.labels
        c1["main"].config(text=f"{p_ac:.0f} W")
        c1["sub1"].config(text=f"{st.ac_in_volt:.1f} V")
        c1["sub2"].config(text=f"{st.ac_in_curr:.2f} A")
        c1["sub3"].config(text=f"{st.ac_in_freq:.1f} Hz")

        # ----- Inverter Output -----
        p_inv = st.inv_out_volt * st.inv_out_curr
        load = (p_inv / 3000) * 100  # assume 3000W inverter
        c2 = self.card_inverter.labels
        c2["main"].config(text=f"{p_inv:.0f} W")
        c2["sub1"].config(text=f"{st.inv_out_volt:.1f} V")
        c2["sub2"].config(text=f"{st.inv_out_curr:.2f} A")
        c2["sub3"].config(text=f"Load {load:.0f}%")

        # Load color
        if load > 80:
            c2["main"].config(fg=RED)
        elif load > 40:
            c2["main"].config(fg=YELLOW)
        else:
            c2["main"].config(fg=ACCENT)

        # ----- System Flow (Mode) -----
        mode = st.inv_mode
        c3 = self.card_state.labels

        if mode == "Line":
            c3["main"].config(text="LINE", fg=GREEN)
            c3["sub1"].config(text="Power from AC Input")
            c3["sub2"].config(text="Inverter Standby")
            c3["sub3"].config(text="")
        elif mode == "Inverter":
            c3["main"].config(text="INVERTER", fg=ACCENT)
            c3["sub1"].config(text="Power from Battery")
            c3["sub2"].config(text="")
            c3["sub3"].config(text="")
        else:
            c3["main"].config(text="BYPASS", fg=YELLOW)
            c3["sub1"].config(text="AC Input Direct")
            c3["sub2"].config(text="")
            c3["sub3"].config(text="")

    def on_show(self):
        self.update_data(self.state)
