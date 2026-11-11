import tkinter as tk
import time
import os
import glob
import math
import pygame
from PIL import Image, ImageTk, ImageSequence

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(SCRIPT_DIR, "Na Para Bang.mp3")
IMAGE_FILE = os.path.join(SCRIPT_DIR, "sad.gif") 
GIF_BOX_W, GIF_BOX_H = 300, 300  
GIF_FALLBACK_FRAME_MS = 100  
GIF_GAP_CM = 0.5  

def resolve_image_path():
    if os.path.exists(IMAGE_FILE):
        return IMAGE_FILE
    candidates = glob.glob(os.path.join(SCRIPT_DIR, "*.gif"))
    if candidates:
        print(f"IMAGE_FILE ('{IMAGE_FILE}') not found — auto-using '{candidates[0]}' instead")
        return candidates[0]
    print(f"No gif found: checked '{IMAGE_FILE}' and no *.gif files exist in {SCRIPT_DIR}")
    return None


LYRICS = [
    (0,   "Na para bang, para bang"),
    (7,   "Sabi ko sa sarili ko, 'Wala lang 'to'"),
    (14,  "Pero ba't sa 'yo na'ng aking sabado?"),
    (16,  "Ang sabi sa sarili ko, 'Wala lang 'to'"),
    (18,  "'Wala lang 'to, wala lang 'to'"),
    (22,  "Sabi ko sa sarili ko, 'Wala lang 'to'"),
    (25,  "Pero ba't sa 'yo na'ng aking sabado?"),
    (30,  "Ang sabi sa sarili ko, 'Wala lang 'to'"),
    (36,  "'Wala lang 'to, wala lang 'to'"),
]

BOX_W, BOX_H = 325, 300
FONT = ("Bebas Neue", 25, "bold")
BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
RISE_SPEED = 100
BOTTOM_SPAWN_OFFSET = 200
FLASH_PERIOD_MS = 1000  

class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

    
        self.border = tk.Frame(self.win, bg="#CCCCCC", bd=0)
        self.border.pack(expand=True, fill="both", padx=1, pady=1)
        self.inner = tk.Frame(self.border, bg=BG_COLOR)
        self.inner.pack(expand=True, fill="both", padx=1, pady=1)

        self.content = tk.Frame(self.inner, bg=BG_COLOR)
        self.content.pack(expand=True, fill="both", padx=10, pady=10)

        self.full_text = text

        self.label = tk.Label(
            self.content, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            wraplength=BOX_W - 25, justify="center"
        )
        self.label.pack(expand=True, fill="both")

        self.typewriter_index = 0
        self.typewriter()
        self.flash_start = time.time()
        self.flash()

        self.x = x
        self.y = float(y)

    def rise(self, dy):
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(145, self.typewriter)

    def flash(self):
        try:
            if not self.win.winfo_exists():
                return  
        except tk.TclError:
            return

        elapsed = time.time() - self.flash_start
 
        phase = (math.sin(2 * math.pi * elapsed / (FLASH_PERIOD_MS / 1000)) + 1) / 2

        bg = self._lerp_color(BG_COLOR, "#000000", phase)
        fg = self._lerp_color(FG_COLOR, "#FFFFFF", phase)
        self._set_colors(bg, fg)

        self.win.after(16, self.flash)  

    @staticmethod
    def _lerp_color(c1, c2, t):
        """Blend two '#RRGGBB' colors together; t=0 -> c1, t=1 -> c2."""
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _set_colors(self, bg, fg):
        try:
            self.win.configure(bg=bg)
            self.inner.configure(bg=bg)
            self.content.configure(bg=bg)
            self.label.configure(bg=bg, fg=fg)
        except tk.TclError:
            pass  

class GifBox:

    def __init__(self, parent, x, y, w, h):
        self.w, self.h = w, h
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        self.label = tk.Label(self.win, bg=BG_COLOR)
        self.label.pack(expand=True, fill="both")

        self.gif_frames = []
        self.gif_index = 0
        self.closed = False

        image_path = resolve_image_path()
        if image_path:
            try:
                src = Image.open(image_path)
                for frame in ImageSequence.Iterator(src):
                    duration = frame.info.get("duration", GIF_FALLBACK_FRAME_MS)
                    resized = frame.convert("RGBA").resize((w, h))
                    self.gif_frames.append((ImageTk.PhotoImage(resized), duration))

                if self.gif_frames:
                    self.label.configure(image=self.gif_frames[0][0])
                    self.animate()
            except Exception as e:
                print(f"Could not load image: {e}")
                self.gif_frames = []

    def animate(self):
        if not self.gif_frames or self.closed:
            return
        try:
            photo, duration = self.gif_frames[self.gif_index]
            self.label.configure(image=photo)
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.win.after(duration, self.animate)
        except tk.TclError:
            pass  

    def close(self):
        self.closed = True
        try:
            self.win.destroy()
        except tk.TclError:
            pass

class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"

        self.start()

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing = BOX_W + 60
        left_x = center_x - spacing
        right_x = center_x + 60

        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        else:
            self.current_side = "left"
            return right_x

    def start(self):
        self.root.iconify()
        center_x = self.screen_w // 2
        left_box_left_edge = center_x - (BOX_W + 60)
        gap_px = int(self.root.winfo_fpixels(f"{GIF_GAP_CM}c"))

        gif_x = left_box_left_edge - GIF_BOX_W - gap_px
        gif_x = max(gif_x, 10)  

        gif_y = self.screen_h - GIF_BOX_H - BOTTOM_SPAWN_OFFSET
        self.gif_box = GifBox(self.root, gif_x, gif_y, GIF_BOX_W, GIF_BOX_H)
        print(f"Gif box placed at ({gif_x}, {gif_y}), {len(self.gif_box.gif_frames)} frames loaded")

        if os.path.exists(AUDIO_FILE):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(AUDIO_FILE)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Could not play audio: {e}")
        else:
            print(f"Audio file not found: {AUDIO_FILE} (animation will still run)")

        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.tick()

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        while (self.next_lyric_idx < len(LYRICS)
               and LYRICS[self.next_lyric_idx][0] <= elapsed):
            t, text = LYRICS[self.next_lyric_idx]
            x = self.random_safe_x()
            y = self.screen_h - BOX_H - BOTTOM_SPAWN_OFFSET
            box = LyricCard(self.root, text, x, y)
            self.boxes.append(box)
            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy)

        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)
        else:
            self.gif_box.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
