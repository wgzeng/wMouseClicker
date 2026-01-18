"""
wMouseClicker - Periodic Mouse Clicker for Windows
A simple tool to click on a screen position at regular intervals.
With UI safety check - only clicks if the target UI hasn't changed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import keyboard
import random
from PIL import Image, ImageTk, ImageChops, ImageStat, ImageDraw

# Disable pyautogui fail-safe for flexibility (be careful!)
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1


class ScreenSelector:
    """Fullscreen overlay for selecting click position, monitoring region, and rest position"""
    
    def __init__(self, callback):
        self.callback = callback
        self.screenshot = None
        self.click_x = None
        self.click_y = None
        self.rest_x = None
        self.rest_y = None
        self.rect_start_x = None
        self.rect_start_y = None
        self.rect_id = None
        self.region_data = None  # Store region data temporarily
        self.step = 1  # Step 1: click position, Step 2: draw rectangle, Step 3: rest position
        
    def start_selection(self):
        """Show the selection overlay"""
        # Take a screenshot first (before showing overlay)
        self.screenshot = pyautogui.screenshot()
        
        # Create fullscreen window
        self.overlay = tk.Toplevel()
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(cursor="cross")
        
        # Get screen size
        self.screen_width = self.overlay.winfo_screenwidth()
        self.screen_height = self.overlay.winfo_screenheight()
        
        # Create canvas with screenshot as background
        self.canvas = tk.Canvas(self.overlay, width=self.screen_width, height=self.screen_height,
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Display screenshot with dark overlay
        self.bg_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # Add semi-transparent dark overlay
        self.canvas.create_rectangle(0, 0, self.screen_width, self.screen_height, 
                                      fill='black', stipple='gray50', tags='overlay')
        
        # Instructions text
        self.instruction_text = self.canvas.create_text(
            self.screen_width // 2, 30, 
            text="Step 1/3: Click on the position where you want to auto-click. Press ESC to cancel.",
            fill='#00d9ff', font=('Segoe UI', 14, 'bold'))
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.overlay.bind('<Escape>', self.on_cancel)
        
        # Focus the overlay
        self.overlay.focus_force()
        
    def on_click(self, event):
        """Handle mouse click"""
        if self.step == 1:
            # Step 1: Record click position
            self.click_x = event.x
            self.click_y = event.y
            
            # Draw a marker at click position
            self.canvas.create_oval(
                self.click_x - 8, self.click_y - 8,
                self.click_x + 8, self.click_y + 8,
                outline='#e94560', width=3, tags='clickmarker'
            )
            self.canvas.create_line(
                self.click_x - 12, self.click_y,
                self.click_x + 12, self.click_y,
                fill='#e94560', width=2, tags='clickmarker'
            )
            self.canvas.create_line(
                self.click_x, self.click_y - 12,
                self.click_x, self.click_y + 12,
                fill='#e94560', width=2, tags='clickmarker'
            )
            
            # Show click position
            self.canvas.create_text(
                self.click_x, self.click_y - 25,
                text=f"Click: ({self.click_x}, {self.click_y})",
                fill='#e94560', font=('Segoe UI', 10, 'bold'), tags='clickmarker'
            )
            
            # Move to step 2
            self.step = 2
            self.canvas.itemconfig(self.instruction_text, 
                text="Step 2/3: Click and drag to select the UI area to monitor. Press ESC to cancel.")
            
        elif self.step == 2:
            # Step 2: Start drawing rectangle
            self.rect_start_x = event.x
            self.rect_start_y = event.y
            self.rect_id = self.canvas.create_rectangle(
                self.rect_start_x, self.rect_start_y, 
                self.rect_start_x, self.rect_start_y,
                outline='#00d9ff', width=2, tags='selection'
            )
            
        elif self.step == 3:
            # Step 3: Record rest position (where to move mouse after clicking)
            self.rest_x = event.x
            self.rest_y = event.y
            
            # Draw a marker at rest position
            self.canvas.create_oval(
                self.rest_x - 6, self.rest_y - 6,
                self.rest_x + 6, self.rest_y + 6,
                outline='#00ff88', fill='#00ff88', tags='restmarker'
            )
            
            # Show rest position
            self.canvas.create_text(
                self.rest_x, self.rest_y - 20,
                text=f"Rest: ({self.rest_x}, {self.rest_y})",
                fill='#00ff88', font=('Segoe UI', 10, 'bold'), tags='restmarker'
            )
            
            # Complete - close overlay and call callback
            left, top, width, height, captured_image = self.region_data
            self.overlay.destroy()
            self.callback(self.click_x, self.click_y, left, top, width, height, 
                         captured_image, self.rest_x, self.rest_y)
        
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.step == 2 and self.rect_id:
            # Update rectangle
            self.canvas.coords(self.rect_id, 
                self.rect_start_x, self.rect_start_y, event.x, event.y)
            
            # Update size display
            width = abs(event.x - self.rect_start_x)
            height = abs(event.y - self.rect_start_y)
            
            # Delete old size text and create new
            self.canvas.delete('sizetext')
            center_x = (self.rect_start_x + event.x) // 2
            center_y = (self.rect_start_y + event.y) // 2
            self.canvas.create_text(center_x, center_y, 
                                    text=f"{width} x {height}",
                                    fill='#00d9ff', font=('Segoe UI', 12, 'bold'),
                                    tags='sizetext')
            
    def on_release(self, event):
        """Handle mouse button release"""
        if self.step != 2 or self.rect_start_x is None:
            return
            
        # Calculate region
        x1, y1 = self.rect_start_x, self.rect_start_y
        x2, y2 = event.x, event.y
        
        # Normalize coordinates
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        width = right - left
        height = bottom - top
        
        # Minimum size check
        if width < 10 or height < 10:
            # Reset rectangle for retry
            self.canvas.delete('selection')
            self.canvas.delete('sizetext')
            self.rect_id = None
            self.rect_start_x = None
            self.rect_start_y = None
            return
            
        # Crop the screenshot to get the captured region
        captured_image = self.screenshot.crop((left, top, right, bottom))
        
        # Store region data and move to step 3
        self.region_data = (left, top, width, height, captured_image)
        self.step = 3
        self.canvas.itemconfig(self.instruction_text, 
            text="Step 3/3: Click where to move mouse after clicking (rest position). Press ESC to cancel.")
        
    def on_cancel(self, event):
        """Handle ESC key or cancel"""
        self.overlay.destroy()


class MouseClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("wMouseClicker")
        self.root.geometry("420x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        # State
        self.clicking = False
        self.click_thread = None
        self.click_count = 0
        self.skipped_count = 0
        self.captured_image = None  # PIL Image of captured UI
        self.captured_photo = None  # PhotoImage for display
        self.capture_region = None  # (left, top, width, height)
        self.rest_position = None  # (x, y) where to move mouse after clicking
        
        # Variables
        self.x_pos = tk.StringVar(value="0")
        self.y_pos = tk.StringVar(value="0")
        self.rest_info = tk.StringVar(value="")
        self.region_info = tk.StringVar(value="No region selected")
        self.interval_min = tk.StringVar(value="5")
        self.interval_sec = tk.StringVar(value="0")
        self.random_enabled = tk.BooleanVar(value=False)
        self.interval_max_min = tk.StringVar(value="20")
        self.interval_max_sec = tk.StringVar(value="0")
        self.click_type = tk.StringVar(value="left")
        self.safety_enabled = tk.BooleanVar(value=True)
        self.similarity_threshold = tk.StringVar(value="100")
        
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
        
        # Capture button (prominent)
        capture_btn = ttk.Button(main_frame, text="📍 Select Region & Click Position (F6)", 
                                  command=self.start_capture)
        capture_btn.pack(fill=tk.X, pady=8)
        
        # Position and region info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Click Position:").pack(side=tk.LEFT)
        ttk.Label(info_frame, text="X:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(info_frame, textvariable=self.x_pos, width=6).pack(side=tk.LEFT)
        ttk.Label(info_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(info_frame, textvariable=self.y_pos, width=6).pack(side=tk.LEFT)
        
        # Current mouse position display
        self.mouse_label = ttk.Label(main_frame, text="Current: (0, 0)", style="Status.TLabel")
        self.mouse_label.pack()
        
        # Region info label
        self.region_label = ttk.Label(main_frame, textvariable=self.region_info, style="Status.TLabel")
        self.region_label.pack()
        
        # Rest position info label
        self.rest_label = ttk.Label(main_frame, textvariable=self.rest_info, style="Status.TLabel")
        self.rest_label.pack()
        
        # Captured UI preview frame
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(preview_frame, text="Captured UI:").pack(anchor=tk.W)
        
        # Canvas to display captured image with border
        self.preview_canvas = tk.Canvas(preview_frame, width=380, height=100, bg="#16213e", 
                                         highlightthickness=1, highlightbackground="#0f3460")
        self.preview_canvas.pack(pady=5)
        self.preview_canvas.create_text(190, 50, text="Press F6 to select region", 
                                         fill="#7f8c8d", font=("Segoe UI", 9))
        
        # Safety check option
        safety_frame = ttk.Frame(main_frame)
        safety_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(safety_frame, text="Safety check (skip if UI changed)", 
                        variable=self.safety_enabled).pack(side=tk.LEFT)
        ttk.Label(safety_frame, text="Threshold:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Entry(safety_frame, textvariable=self.similarity_threshold, width=4).pack(side=tk.LEFT)
        ttk.Label(safety_frame, text="%").pack(side=tk.LEFT)
        
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
        self.status_label = ttk.Label(main_frame, text="Status: Idle | Clicks: 0 | Skipped: 0", style="Status.TLabel")
        self.status_label.pack(pady=(10, 5))
        
        # Match info
        self.match_label = ttk.Label(main_frame, text="", style="Status.TLabel")
        self.match_label.pack()
        
    def setup_hotkeys(self):
        keyboard.add_hotkey('F6', self.start_capture)
        keyboard.add_hotkey('F7', self.start_clicking)
        keyboard.add_hotkey('F8', self.stop_clicking)
        
    def update_mouse_position(self):
        """Update the current mouse position display"""
        if not self.clicking:
            x, y = pyautogui.position()
            self.mouse_label.config(text=f"Current: ({x}, {y})")
        self.root.after(100, self.update_mouse_position)
        
    def start_capture(self):
        """Start the screen region selection"""
        if self.clicking:
            return
        # Hide main window during selection
        self.root.withdraw()
        # Small delay to ensure window is hidden
        self.root.after(100, self._do_capture)
        
    def _do_capture(self):
        """Actually start the capture after window is hidden"""
        selector = ScreenSelector(self.on_region_selected)
        selector.start_selection()
        
    def on_region_selected(self, click_x, click_y, left, top, width, height, captured_image, rest_x, rest_y):
        """Callback when region selection is complete"""
        # Show main window again
        self.root.deiconify()
        self.root.lift()
        
        # Store the capture info
        self.x_pos.set(str(click_x))
        self.y_pos.set(str(click_y))
        self.capture_region = (left, top, width, height)
        self.captured_image = captured_image
        self.rest_position = (rest_x, rest_y)
        
        # Update region info
        self.region_info.set(f"Region: ({left}, {top}) - {width}x{height} px")
        self.rest_info.set(f"Rest position: ({rest_x}, {rest_y})")
        
        # Update preview
        self.update_preview()
        
        # Update status
        self.status_label.config(text=f"Status: Captured click ({click_x}, {click_y}), rest ({rest_x}, {rest_y})")
        
    def update_preview(self):
        """Update the preview canvas with the captured image"""
        if self.captured_image is None or self.capture_region is None:
            return
            
        # Resize image to fit preview (max 380x100)
        img = self.captured_image.copy()
        orig_width, orig_height = img.size
        
        # Calculate scaling to fit within preview while maintaining aspect ratio
        max_width, max_height = 380, 100
        ratio = min(max_width / img.width, max_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Add a subtle border to the preview image
        bordered = Image.new('RGB', (img.width + 4, img.height + 4), '#0f3460')
        bordered.paste(img, (2, 2))
        
        # Convert to PhotoImage
        self.captured_photo = ImageTk.PhotoImage(bordered)
        
        # Clear canvas and display
        self.preview_canvas.delete("all")
        
        # Calculate image position on canvas
        canvas_center_x, canvas_center_y = 190, 50
        img_left = canvas_center_x - bordered.width // 2
        img_top = canvas_center_y - bordered.height // 2
        
        self.preview_canvas.create_image(canvas_center_x, canvas_center_y, 
                                          image=self.captured_photo, anchor=tk.CENTER)
        
        # Calculate click position relative to preview
        click_x = int(self.x_pos.get())
        click_y = int(self.y_pos.get())
        region_left, region_top, region_width, region_height = self.capture_region
        
        # Position relative to region (0,0 = top-left of region)
        rel_x = click_x - region_left
        rel_y = click_y - region_top
        
        # Scale to preview size and offset by image position
        preview_click_x = img_left + 2 + int(rel_x * ratio)  # +2 for border
        preview_click_y = img_top + 2 + int(rel_y * ratio)
        
        # Draw crosshair at click position
        self.preview_canvas.create_line(preview_click_x - 10, preview_click_y, 
                                         preview_click_x + 10, preview_click_y, 
                                         fill='#e94560', width=2)
        self.preview_canvas.create_line(preview_click_x, preview_click_y - 10, 
                                         preview_click_x, preview_click_y + 10, 
                                         fill='#e94560', width=2)
        self.preview_canvas.create_oval(preview_click_x - 5, preview_click_y - 5,
                                         preview_click_x + 5, preview_click_y + 5,
                                         outline='#e94560', width=2)
        
    def compare_images(self, img1, img2):
        """Compare two images and return similarity percentage (0-100)"""
        if img1 is None or img2 is None:
            return 0
            
        # Ensure same size
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
        # Convert to same mode
        img1 = img1.convert('RGB')
        img2 = img2.convert('RGB')
        
        # Calculate difference
        diff = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff)
        
        # Calculate similarity (inverse of mean difference)
        mean_diff = sum(stat.mean) / 3
        similarity = max(0, 100 - (mean_diff / 255 * 100))
        
        return similarity
        
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
            
            # Check if we have a captured image for safety check
            if self.safety_enabled.get() and self.captured_image is None:
                messagebox.showwarning("Warning", "Safety check enabled but no UI captured.\nPress F6 to select region or disable safety check.")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for position and interval")
            return
            
        self.clicking = True
        self.click_count = 0
        self.skipped_count = 0
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.click_thread = threading.Thread(target=self.click_loop, args=(x, y), daemon=True)
        self.click_thread.start()
        
    def click_loop(self, x, y):
        """Main clicking loop"""
        while self.clicking:
            # Check UI before clicking
            should_click = True
            similarity = 100
            
            if self.safety_enabled.get() and self.captured_image is not None and self.capture_region is not None:
                left, top, width, height = self.capture_region
                try:
                    current_image = pyautogui.screenshot(region=(left, top, width, height))
                    similarity = self.compare_images(self.captured_image, current_image)
                    threshold = float(self.similarity_threshold.get() or 95)
                    
                    if similarity < threshold:
                        should_click = False
                        self.skipped_count += 1
                except Exception:
                    pass  # If screenshot fails, proceed with click
            
            if should_click:
                self.perform_click(x, y)
                self.click_count += 1
            
            # Update status
            count = self.click_count
            skipped = self.skipped_count
            sim = similarity
            self.root.after(0, lambda c=count, s=skipped, m=sim, dc=should_click: self.update_status_display(c, s, m, dc))
            
            # Get next interval (random or fixed)
            interval = self.get_next_interval()
            is_random = self.random_enabled.get()
            
            # Countdown
            remaining = interval
            while remaining > 0 and self.clicking:
                mins, secs = divmod(remaining, 60)
                random_indicator = " (rnd)" if is_random else ""
                c, s = self.click_count, self.skipped_count
                self.root.after(0, lambda m=mins, sec=secs, r=random_indicator, ct=c, sk=s: self.status_label.config(
                    text=f"Running | Clicks: {ct} | Skipped: {sk} | Next: {m:02d}:{sec:02d}{r}"
                ))
                time.sleep(1)
                remaining -= 1
                
        self.root.after(0, lambda: self.status_label.config(text="Status: Stopped"))
        
    def update_status_display(self, clicks, skipped, similarity, did_click):
        """Update the status display after a click attempt"""
        action = "Clicked" if did_click else "Skipped"
        self.match_label.config(text=f"Last: {action} | UI Match: {similarity:.1f}%")
        
    def perform_click(self, x, y):
        """Perform the actual click"""
        click_type = self.click_type.get()
        
        # Move and click
        pyautogui.moveTo(x, y)
        
        if click_type == "left":
            pyautogui.click()
        elif click_type == "right":
            pyautogui.rightClick()
        elif click_type == "double":
            pyautogui.doubleClick()
        
        # Click at rest position (so cursor doesn't affect UI screenshot)
        if self.rest_position is not None:
            rest_x, rest_y = self.rest_position
            pyautogui.click(rest_x, rest_y)
        
    def stop_clicking(self):
        """Stop the periodic clicking"""
        self.clicking = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"Status: Stopped | Clicks: {self.click_count} | Skipped: {self.skipped_count}")
        
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
