import tkinter as tk
from tkinter import Frame, Label, Button

BG = "#0d0d0d"
CARD = "#1a1a1a"
TXT = "#ffffff"
MUTED = "#888888"
ACCENT_48 = "#00ff99"
ORANGE = "#ff9933"
BLUE = "#4da6ff"


class MainPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # =================================================
        # CONTENT AREA (TOP – เดิมทั้งหมด)
        # =================================================
        content = Frame(self, bg=BG)
        content.pack(fill="both", expand=True)

        # ---------- 48V BATTERY (HERO CARD) ----------
        batt48 = Frame(content, bg=CARD, padx=20, pady=15)
        batt48.pack(fill="x", padx=20, pady=(20, 10))

        Label(
            batt48,
            text="48V BATTERY",
            fg=ACCENT_48,
            bg=CARD,
            font=("SF Pro Display", 18, "bold")
        ).pack(anchor="w")

        self.lbl_48_soc = Label(
            batt48,
            text="-- %",
            fg=ACCENT_48,
            bg=CARD,
            font=("SF Pro Display", 42, "bold")
        )
        self.lbl_48_soc.pack()

        self.lbl_48_vals = Label(
            batt48,
            text="-- V   -- A   -- W",
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 16)
        )
        self.lbl_48_vals.pack()

        self.lbl_48_state = Label(
            batt48,
            text="--",
            fg=MUTED,
            bg=CARD,
            font=("SF Pro Display", 14)
        )
        self.lbl_48_state.pack(pady=(5, 0))

        # ---------- 12V / 24V ----------
        row = Frame(content, bg=BG)
        row.pack(fill="x", padx=20, pady=10)

        self.card12 = self._small_batt_card(row, "12V")
        self.card12.pack(side="left", expand=True, fill="both", padx=(0, 10))

        self.card24 = self._small_batt_card(row, "24V")
        self.card24.pack(side="left", expand=True, fill="both")

        # ---------- SOLAR / AC ----------
        row2 = Frame(content, bg=BG)
        row2.pack(fill="x", padx=20, pady=10)

        self.lbl_solar = self._info_card(row2, "SOLAR", BLUE)
        self.lbl_solar.pack(side="left", expand=True, fill="both", padx=(0, 10))

        self.lbl_ac = self._info_card(row2, "AC INPUT", ORANGE)
        self.lbl_ac.pack(side="left", expand=True, fill="both")

        # =================================================
        # BOTTOM ROW (INVERTER + MENU)  ← แถวเดิม แบ่งครึ่ง
        # =================================================
        bottom = Frame(content, bg=BG)
        bottom.pack(fill="x", padx=20, pady=10)

        # ---------- INVERTER (ซ้าย) ----------
        inv = Frame(bottom, bg=CARD, padx=20, pady=10)
        inv.pack(side="left", fill="both", expand=True, padx=(0, 10))

        Label(
            inv,
            text="INVERTER",
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 16, "bold")
        ).pack(anchor="w")

        self.lbl_inv_val = Label(
            inv,
            text="--",
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 14)
        )
        self.lbl_inv_val.pack(anchor="w", pady=(8, 0))

        # ---------- MENU (ขวา) ----------
        menu = Frame(bottom, bg=CARD, padx=20, pady=10)
        menu.pack(side="left", fill="both", expand=True)

        Button(
            menu,
            text="☰  MENU",
            command=lambda: controller.show_frame("MenuPage"),
            font=("SF Pro Display", 16, "bold"),
            bg="#222222",
            fg=TXT,
            bd=0,
            padx=32,
            pady=18
        ).pack(fill="both", expand=True)

    # =================================================
    # HELPER WIDGETS
    # =================================================
    def _small_batt_card(self, parent, title):
        f = Frame(parent, bg=CARD, padx=10, pady=10)
        Label(
            f,
            text=title,
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 14, "bold")
        ).pack()
        lbl = Label(
            f,
            text="--",
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 18)
        )
        lbl.pack()
        f.value = lbl
        return f

    def _info_card(self, parent, title, color):
        f = Frame(parent, bg=CARD, padx=10, pady=10)
        Label(
            f,
            text=title,
            fg=color,
            bg=CARD,
            font=("SF Pro Display", 14, "bold")
        ).pack()
        lbl = Label(
            f,
            text="--",
            fg=TXT,
            bg=CARD,
            font=("SF Pro Display", 16)
        )
        lbl.pack()
        return lbl

    # =================================================
    # DATA UPDATE
    # =================================================
    def update_data(self, st):
        v48 = float(getattr(st, "batt48_volt", 0.0) or 0.0)
        i48 = float(getattr(st, "batt48_curr", 0.0) or 0.0)
        power48 = v48 * i48
        state = (
            "CHARGING" if  i48 > 0.5
            else "DISCHARGING" if i48 < -0.5
            else "IDLE"
        )
        color = ACCENT_48 if state == "CHARGING" else ORANGE

        self.lbl_48_soc.config(text=f"{int(st.batt48_soc)} %", fg=color)
        self.lbl_48_vals.config(
            text=f"{v48:.1f} V   {i48:.1f} A   {power48:.0f} W"
        )
        self.lbl_48_state.config(text=state, fg=color)

        self.card12.value.config(
            text=f"{st.batt12_soc:.0f}%  {st.batt12_volt:.1f}V"
        )
        self.card24.value.config(
            text=f"{st.batt24_soc:.0f}%  {st.batt24_volt:.1f}V"
        )

        self.lbl_solar.config(
            text=f"{st.solar_volt:.1f}V  {st.solar_curr:.1f}A  {st.solar_volt * st.solar_curr:.0f}W"
        )
        self.lbl_ac.config(
            text=f"{st.ac_in_volt:.0f}V  {st.ac_in_freq:.1f}Hz"
        )

        self.lbl_inv_val.config(
            text=f"MODE: {st.inv_mode}   {st.inv_out_volt:.0f}V"
        )
