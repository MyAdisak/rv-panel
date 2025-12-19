import tkinter as tk
from tkinter import Frame, Label, Button, Scale, HORIZONTAL

BG = "#0d0d0d"
CARD = "#1c1c1c"
TXT = "#eaeaea"
ACCENT = "#2B6DFF"
WARN = "#ffcc00"


class SettingsPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.state = controller.state
        self.pin_overlay = None

        self.light_vars = {}
        self.light_dirty = False

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
            text="SETTINGS",
            font=("SF Pro Display", 22, "bold"),
            bg=BG,
            fg=TXT,
        ).pack(side="left", padx=10)

        # ================= BODY =================
        body = Frame(self, bg=BG)
        body.pack(pady=20, fill="both", expand=True)

        # ---------- DISPLAY ----------
        self._section(body, "DISPLAY")

        Label(body, text="Screen Brightness", fg=TXT, bg=BG).pack(anchor="w", padx=20)

        self.brightness = Scale(
            body,
            from_=10,
            to=255,
            orient=HORIZONTAL,
            length=320,
            bg=BG,
            fg=TXT,
            troughcolor="#444444",
            highlightthickness=0,
            command=self._set_brightness,
        )
        self.brightness.pack(padx=20, pady=10)

        # ---------- LIGHTING DEFAULT ----------
        self._section(body, "LIGHTING DEFAULT (BOOT)")

        for key, label in [
            ("light_main_12v", "12V MAIN"),
            ("light_downlight", "Downlight"),
            ("light_hall", "Hall"),
            ("light_ambient", "Ambient"),
            ("light_outdoor", "Outdoor"),
        ]:
            var = tk.BooleanVar(value=self.state.light_defaults.get(key, False))
            self.light_vars[key] = var

            row = Frame(body, bg=BG)
            row.pack(anchor="w", padx=20, pady=4)

            tk.Checkbutton(
                row,
                text=label,
                variable=var,
                bg=BG,
                fg=TXT,
                selectcolor=BG,
                command=self._on_light_change,
            ).pack(side="left")

        self.lbl_light_warn = Label(body, text="", fg=WARN, bg=BG)
        self.lbl_light_warn.pack(anchor="w", padx=20)

        self.btn_apply_light = Button(
            body,
            text="APPLY DEFAULT",
            bg="#333333",
            fg=TXT,
            width=20,
            pady=6,
            command=self._apply_light_defaults,
            state="disabled",
        )
        self.btn_apply_light.pack(anchor="w", padx=20, pady=(0, 10))

        # ---------- COMMUNICATION ----------
        self._section(body, "COMMUNICATION")

        self.lbl_rs485 = Label(body, text="RS485: --", fg=TXT, bg=BG)
        self.lbl_rs485.pack(anchor="w", padx=20)

        self.lbl_rs485_err = Label(body, text="Errors: 0", fg="#888888", bg=BG)
        self.lbl_rs485_err.pack(anchor="w", padx=20)

        # ---------- SYSTEM ----------
        self._section(body, "SYSTEM (SAFE)")

        self.lbl_confirm = Label(body, text="", fg="#ff5555", bg=BG)
        self.lbl_confirm.pack(anchor="w", padx=20)

        Button(
            body,
            text="RESTART APP",
            bg="#333333",
            fg=TXT,
            width=22,
            pady=8,
            command=self._request_restart,
        ).pack(anchor="w", padx=20, pady=6)

        Button(
            body,
            text="REBOOT SYSTEM",
            bg="#332222",
            fg="#ff5555",
            width=22,
            pady=8,
            command=self._request_reboot,
        ).pack(anchor="w", padx=20, pady=6)

    # ================= HELPERS =================

    def _section(self, parent, title):
        Label(parent, text=title, fg=ACCENT, bg=BG,
              font=("SF Pro Display", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))

    def _set_brightness(self, value):
        try:
            self.state.screen_brightness = int(value)
        except Exception:
            pass

    # ================= LIGHT DEFAULT =================

    def _on_light_change(self):
        self.light_dirty = True
        self.lbl_light_warn.config(text="⚠ Changes apply on next reboot")
        self.btn_apply_light.config(state="normal")

    def _apply_light_defaults(self):
        for k, var in self.light_vars.items():
            self.state.light_defaults[k] = var.get()

        self.light_dirty = False
        self.lbl_light_warn.config(text="✔ Default saved (effective on next reboot)")
        self.btn_apply_light.config(state="disabled")

    # ================= SYSTEM =================

    def _request_restart(self):
        self.state.request = "restart_app"
        self.lbl_confirm.config(text="Press again to CONFIRM RESTART")

    def _request_reboot(self):
        self.state.request = "reboot"
        self.lbl_confirm.config(text="Press again to CONFIRM REBOOT")

    # ================= PIN LOCK =================

    def _show_pin_lock(self):
        if self.pin_overlay:
            return

        self.pin_overlay = Frame(self, bg="#000000")
        self.pin_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = Frame(self.pin_overlay, bg=CARD, padx=20, pady=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        Label(card, text="ENTER PIN", font=("SF Pro Display", 18, "bold"),
              bg=CARD, fg=TXT).pack(pady=(0, 10))

        self.pin_entry = tk.Entry(card, font=("SF Pro Display", 20),
                                  justify="center", show="*", width=6)
        self.pin_entry.pack(pady=10)
        self.pin_entry.focus()

        Button(
            card,
            text="UNLOCK",
            font=("SF Pro Display", 14, "bold"),
            bg=ACCENT,
            fg="#ffffff",
            bd=0,
            padx=20,
            pady=8,
            command=self._check_pin,
        ).pack(pady=(10, 0))

    def _check_pin(self):
        if self.pin_entry.get() == self.state.settings_pin:
            self.state.settings_unlocked = True
            self.pin_overlay.destroy()
            self.pin_overlay = None
        else:
            self.pin_entry.delete(0, tk.END)

    # ================= UPDATE =================

    def update_data(self, st):
        try:
            self.brightness.set(st.screen_brightness)
        except Exception:
            pass

        status = st.rs485_status
        color = "#00ff99" if status == "OK" else "#ffcc00" if status == "ERROR" else "#ff5555"

        self.lbl_rs485.config(text=f"RS485: {status}", fg=color)
        self.lbl_rs485_err.config(text=f"Errors: {st.rs485_error_count}")

        if getattr(st, "request", None) is None:
            self.lbl_confirm.config(text="")

    def on_show(self):
        if not self.state.settings_unlocked:
            self._show_pin_lock()
