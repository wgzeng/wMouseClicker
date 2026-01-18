"""
wMouseClicker - Periodic Mouse Clicker for Windows
A simple tool to click on a screen position at regular intervals.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import keyboard
import random

# Disable pyautogui fail-safe for flexibility (be careful!)
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1


class MouseClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("wMouseClicker")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        # State
        self.clicking = False
        self.click_thread = None
        self.click_count = 0
        
        # Variables
        self.x_pos = tk.StringVar(value="0")
        self.y_pos = tk.StringVar(value="0")
        self.interval_min = tk.StringVar(value="5")
        self.interval_sec = tk.StringVar(value="0")
        self.random_enabled = tk.BooleanVar(value=False)
        self.interval_max_min = tk.StringVar(value="20")
        self.interval_max_sec = tk.StringVar(value="0")
        self.click_type = tk.StringVar(value="left")
        
        self.setup_styles()
        self.create_widgets()
        self.setup_hotkeys()
        self.update_mouse_position()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#eaf6ff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#1a1a2e", foreground="#00d9ff", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", background="#1a1a2e", foreground="#7f8c8d", font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground="#16213e", foreground="#eaf6ff", insertcolor="#eaf6ff")
        style.configure("TButton", background="#0f3460", foreground="#eaf6ff", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("TButton", background=[("active", "#e94560"), ("pressed", "#c73e54")])
        style.configure("Start.TButton", background="#00d9ff", foreground="#1a1a2e")
        style.map("Start.TButton", background=[("active", "#00b8d4")])
        style.configure("Stop.TButton", background="#e94560", foreground="#eaf6ff")
        style.map("Stop.TButton", background=[("active", "#c73e54")])
        style.configure("TRadiobutton", background="#1a1a2e", foreground="#eaf6ff", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#1a1a2e", foreground="#eaf6ff", font=("Segoe UI", 10))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="🖱️ wMouseClicker", style="Header.TLabel").pack(pady=(0, 10))
        
        # Position Frame
        pos_frame = ttk.Frame(main_frame)
        pos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pos_frame, text="Click Position:").pack(side=tk.LEFT)
        
        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=(15, 2))
        x_entry = ttk.Entry(pos_frame, textvariable=self.x_pos, width=8)
        x_entry.pack(side=tk.LEFT)
        
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 2))
        y_entry = ttk.Entry(pos_frame, textvariable=self.y_pos, width=8)
        y_entry.pack(side=tk.LEFT)
        
        # Capture button
        capture_btn = ttk.Button(main_frame, text="📍 Capture Position (F6)", command=self.capture_position)
        capture_btn.pack(fill=tk.X, pady=8)
        
        # Current mouse position display
        self.mouse_label = ttk.Label(main_frame, text="Current: (0, 0)", style="Status.TLabel")
        self.mouse_label.pack()
        
        # Interval Frame
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(interval_frame, text="Interval:").pack(side=tk.LEFT)
        
        ttk.Entry(interval_frame, textvariable=self.interval_min, width=5).pack(side=tk.LEFT, padx=(10, 2))
        ttk.Label(interval_frame, text="min").pack(side=tk.LEFT)
        
        ttk.Entry(interval_frame, textvariable=self.interval_sec, width=5).pack(side=tk.LEFT, padx=(15, 2))
        ttk.Label(interval_frame, text="sec").pack(side=tk.LEFT)
        
        # Random interval option
        random_frame = ttk.Frame(main_frame)
        random_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(random_frame, text="Random interval", variable=self.random_enabled, 
                        command=self.toggle_random).pack(side=tk.LEFT)
        
        ttk.Label(random_frame, text="Max:").pack(side=tk.LEFT, padx=(15, 2))
        self.max_min_entry = ttk.Entry(random_frame, textvariable=self.interval_max_min, width=5, state=tk.DISABLED)
        self.max_min_entry.pack(side=tk.LEFT, padx=(2, 2))
        self.max_min_label = ttk.Label(random_frame, text="min")
        self.max_min_label.pack(side=tk.LEFT)
        
        self.max_sec_entry = ttk.Entry(random_frame, textvariable=self.interval_max_sec, width=5, state=tk.DISABLED)
        self.max_sec_entry.pack(side=tk.LEFT, padx=(10, 2))
        self.max_sec_label = ttk.Label(random_frame, text="sec")
        self.max_sec_label.pack(side=tk.LEFT)
        
        # Click type
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Click Type:").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Left", variable=self.click_type, value="left").pack(side=tk.LEFT, padx=(15, 5))
        ttk.Radiobutton(type_frame, text="Right", variable=self.click_type, value="right").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Double", variable=self.click_type, value="double").pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="▶ Start (F7)", command=self.start_clicking, style="Start.TButton")
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop (F8)", command=self.stop_clicking, style="Stop.TButton", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Idle | Clicks: 0", style="Status.TLabel")
        self.status_label.pack(pady=(10, 10))
        
    def setup_hotkeys(self):
        keyboard.add_hotkey('F6', self.capture_position)
        keyboard.add_hotkey('F7', self.start_clicking)
        keyboard.add_hotkey('F8', self.stop_clicking)
        
    def update_mouse_position(self):
        """Update the current mouse position display"""
        if not self.clicking:
            x, y = pyautogui.position()
            self.mouse_label.config(text=f"Current: ({x}, {y})")
        self.root.after(100, self.update_mouse_position)
        
    def capture_position(self):
        """Capture the current mouse position"""
        x, y = pyautogui.position()
        self.x_pos.set(str(x))
        self.y_pos.set(str(y))
        self.status_label.config(text=f"Status: Position captured ({x}, {y})")
        
    def toggle_random(self):
        """Toggle random interval fields"""
        if self.random_enabled.get():
            self.max_min_entry.config(state=tk.NORMAL)
            self.max_sec_entry.config(state=tk.NORMAL)
        else:
            self.max_min_entry.config(state=tk.DISABLED)
            self.max_sec_entry.config(state=tk.DISABLED)
        
    def get_interval_seconds(self, use_max=False):
        """Get total interval in seconds"""
        try:
            if use_max:
                minutes = int(self.interval_max_min.get() or 0)
                seconds = int(self.interval_max_sec.get() or 0)
            else:
                minutes = int(self.interval_min.get() or 0)
                seconds = int(self.interval_sec.get() or 0)
            return minutes * 60 + seconds
        except ValueError:
            return 0
            
    def get_next_interval(self):
        """Get the next interval (random if enabled, otherwise fixed)"""
        min_interval = self.get_interval_seconds(use_max=False)
        if self.random_enabled.get():
            max_interval = self.get_interval_seconds(use_max=True)
            if max_interval > min_interval:
                return random.randint(min_interval, max_interval)
        return min_interval
            
    def start_clicking(self):
        """Start the periodic clicking"""
        if self.clicking:
            return
            
        try:
            x = int(self.x_pos.get())
            y = int(self.y_pos.get())
            min_interval = self.get_interval_seconds()
            
            if min_interval <= 0:
                messagebox.showerror("Error", "Please set an interval greater than 0")
                return
            
            # Validate random interval settings
            if self.random_enabled.get():
                max_interval = self.get_interval_seconds(use_max=True)
                if max_interval <= min_interval:
                    messagebox.showerror("Error", "Max interval must be greater than min interval")
                    return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for position and interval")
            return
            
        self.clicking = True
        self.click_count = 0
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.click_thread = threading.Thread(target=self.click_loop, args=(x, y), daemon=True)
        self.click_thread.start()
        
    def click_loop(self, x, y):
        """Main clicking loop"""
        while self.clicking:
            # Perform click
            self.perform_click(x, y)
            self.click_count += 1
            
            # Get next interval (random or fixed)
            interval = self.get_next_interval()
            is_random = self.random_enabled.get()
            
            # Countdown
            remaining = interval
            while remaining > 0 and self.clicking:
                mins, secs = divmod(remaining, 60)
                random_indicator = " (rnd)" if is_random else ""
                count = self.click_count
                self.root.after(0, lambda m=mins, s=secs, r=random_indicator, c=count: self.status_label.config(
                    text=f"Status: Running | Clicks: {c} | Next: {m:02d}:{s:02d}{r}"
                ))
                time.sleep(1)
                remaining -= 1
                
        self.root.after(0, lambda: self.status_label.config(text="Status: Stopped"))
        
    def perform_click(self, x, y):
        """Perform the actual click"""
        click_type = self.click_type.get()
        
        # Save current position
        original_x, original_y = pyautogui.position()
        
        # Move and click
        pyautogui.moveTo(x, y)
        
        if click_type == "left":
            pyautogui.click()
        elif click_type == "right":
            pyautogui.rightClick()
        elif click_type == "double":
            pyautogui.doubleClick()
            
        # Optionally move back (commented out - uncomment if needed)
        # pyautogui.moveTo(original_x, original_y)
        
    def stop_clicking(self):
        """Stop the periodic clicking"""
        self.clicking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"Status: Stopped | Clicks: {self.click_count}")
        
    def on_closing(self):
        """Handle window close"""
        self.clicking = False
        keyboard.unhook_all()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MouseClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
