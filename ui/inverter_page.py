import tkinter as tk
from tkinter import Frame, Label, Button

BG = "#0d0d0d"
CARD = "#1a1a1a"
TXT = "#ffffff"
MUTED = "#888888"
ACCENT = "#ff9933"
GREEN = "#00ff99"
YELLOW = "#ffcc00"
RED = "#ff5555"


class InverterPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ================= HEADER =================
        header = Frame(self, bg=BG)
        header.pack(fill="x", pady=10)

        Button(
            header,
            text="← Back",
            command=lambda: controller.show_frame("MainPage"),
            font=("SF Pro Display", 12),
            bg="#1b1b1b",
            fg=TXT,
            bd=0,
            padx=10,
            pady=5,
        ).pack(side="left", padx=10)

        Label(
            header,
            text="INVERTER",
            font=("SF Pro Display", 22, "bold"),
            bg=BG,
            fg=TXT,
        ).pack(side="left", padx=10)

        # ================= BODY =================
        body = Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------- STATUS ----------
        status = Frame(body, bg=CARD, padx=20, pady=20)
        status.pack(fill="x", pady=(0, 10))

        Label(status, text="STATUS", fg=ACCENT, bg=CARD,
              font=("SF Pro Display", 16, "bold")).pack(anchor="w")

        self.lbl_mode = Label(status, text="MODE: --", fg=GREEN, bg=CARD,
                              font=("SF Pro Display", 18, "bold"))
        self.lbl_mode.pack(anchor="w", pady=(10, 0))

        # ---------- AC INPUT ----------
        ac = Frame(body, bg=CARD, padx=20, pady=20)
        ac.pack(fill="x", pady=(0, 10))

        Label(ac, text="AC INPUT", fg=ACCENT, bg=CARD,
              font=("SF Pro Display", 16, "bold")).pack(anchor="w")

        self.lbl_ac = Label(ac, text="-- V   -- Hz", fg=TXT, bg=CARD,
                            font=("SF Pro Display", 16))
        self.lbl_ac.pack(anchor="w", pady=(10, 0))

        # ---------- OUTPUT ----------
        out = Frame(body, bg=CARD, padx=20, pady=20)
        out.pack(fill="x", pady=(0, 10))

        Label(out, text="OUTPUT", fg=ACCENT, bg=CARD,
              font=("SF Pro Display", 16, "bold")).pack(anchor="w")

        self.lbl_out = Label(out, text="-- V   -- Hz", fg=TXT, bg=CARD,
                             font=("SF Pro Display", 16))
        self.lbl_out.pack(anchor="w", pady=(10, 0))

        self.lbl_power = Label(out, text="LOAD: -- W", fg=TXT, bg=CARD,
                               font=("SF Pro Display", 16))
        self.lbl_power.pack(anchor="w", pady=(5, 0))

        # ---------- ALARM / FAULT ----------
        alarm = Frame(body, bg=CARD, padx=20, pady=20)
        alarm.pack(fill="x")

        Label(alarm, text="ALARM / FAULT", fg=ACCENT, bg=CARD,
              font=("SF Pro Display", 16, "bold")).pack(anchor="w")

        self.lbl_alarm_level = Label(
            alarm, text="STATUS: --", fg=GREEN, bg=CARD,
            font=("SF Pro Display", 18, "bold")
        )
        self.lbl_alarm_level.pack(anchor="w", pady=(10, 0))

        self.lbl_fault_code = Label(
            alarm, text="CODE: --", fg=TXT, bg=CARD,
            font=("SF Pro Display", 14)
        )
        self.lbl_fault_code.pack(anchor="w", pady=(5, 0))

        self.lbl_fault_msg = Label(
            alarm, text="MESSAGE: --", fg=TXT, bg=CARD,
            font=("SF Pro Display", 14)
        )
        self.lbl_fault_msg.pack(anchor="w", pady=(5, 0))

        Label(alarm, text="(Read-only)", fg=MUTED, bg=CARD,
              font=("SF Pro Display", 12)).pack(anchor="w", pady=(10, 0))

    # ================= UPDATE =================
    def update_data(self, st):
        # Mode
        self.lbl_mode.config(text=f"MODE: {st.inv_mode}")

        # AC / Output
        self.lbl_ac.config(
            text=f"{st.ac_in_volt:.0f} V   {st.ac_in_freq:.1f} Hz"
        )
        self.lbl_out.config(
            text=f"{st.inv_out_volt:.0f} V   {st.inv_out_freq:.1f} Hz"
        )

        power_w = st.inv_out_volt * st.inv_out_curr
        self.lbl_power.config(text=f"LOAD: {power_w:.0f} W")

        # Alarm
        level = st.inv_alarm_level
        color = GREEN if level == "NORMAL" else YELLOW if level == "WARNING" else RED

        self.lbl_alarm_level.config(text=f"STATUS: {level}", fg=color)
        self.lbl_fault_code.config(text=f"CODE: {st.inv_fault_code}")
        self.lbl_fault_msg.config(text=f"MESSAGE: {st.inv_fault_msg}")

    def on_show(self):
        pass
