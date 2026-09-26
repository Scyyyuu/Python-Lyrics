import tkinter as tk
import time
import os
import glob
import math
import pygame
from PIL import Image, ImageTk, ImageSequence

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(SCRIPT_DIR, "Totoong tayo.mp3")
IMAGE_FILE = os.path.join(SCRIPT_DIR, "cover.gif")  # change to your actual image/gif filename
GIF_BOX_W, GIF_BOX_H = 300, 300  # size of the standalone gif box
GIF_FALLBACK_FRAME_MS = 100  # used only if the gif doesn't specify its own frame speed
GIF_GAP_CM = 0.5  # real-world distance between the lyric box column and the gif

def resolve_image_path():
    """Use IMAGE_FILE if it exists; otherwise auto-detect any .gif sitting
    next to the script, so a filename typo can't silently break the gif."""
    if os.path.exists(IMAGE_FILE):
        return IMAGE_FILE
    candidates = glob.glob(os.path.join(SCRIPT_DIR, "*.gif"))
    if candidates:
        print(f"IMAGE_FILE ('{IMAGE_FILE}') not found — auto-using '{candidates[0]}' instead")
        return candidates[0]
    print(f"No gif found: checked '{IMAGE_FILE}' and no *.gif files exist in {SCRIPT_DIR}")
    return None


# ---------------------------------------------------------------------------
# Fill in the actual lyric lines from "Totoong Tayo" (JIN) below.
# Each tuple is (seconds_into_song, line_text).
# The timestamps are spaced out as a rough placeholder verse/chorus rhythm —
# adjust them to match where each line actually lands in the track.
# ---------------------------------------------------------------------------
LYRICS = [
    (0,   "Kitang kita na sa kilos mong kakaiba"),
    (7,   "Ooh, ako pa ba? ohhhhhhh"),
    (14,  "Ikaw at ako"),
    (16,  "(Ikaw at ako)"),
    (18,  "Ang magkasama"),
    (22,  "Sa mga alaala"),
    (25,  "Pwede bang?"),
    (30,  "Kalimutan muna natin ang mundo"),
    (36,  "At hawakan mo ang kamay ko"),
    (41,  "Magmahalan"),
    (45,  "Na walang iniisip na kung ano"),
    (51,  "Ipakita lang ang totoong tayo"),
]

BOX_W, BOX_H = 325, 300
FONT = ("Bebas Neue", 25, "bold")
BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
RISE_SPEED = 100
BOTTOM_SPAWN_OFFSET = 200
FLASH_PERIOD_MS = 1000  # how long one full smooth pulse cycle takes (ms)

class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        # White card needs a visible border since it blends into most desktops
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
                return  # card is gone (floated off / destroyed) — stop flashing
        except tk.TclError:
            return

        elapsed = time.time() - self.flash_start
        # smooth 0..1..0 pulse via sine, instead of a hard on/off toggle
        phase = (math.sin(2 * math.pi * elapsed / (FLASH_PERIOD_MS / 1000)) + 1) / 2

        bg = self._lerp_color(BG_COLOR, "#000000", phase)
        fg = self._lerp_color(FG_COLOR, "#FFFFFF", phase)
        self._set_colors(bg, fg)

        self.win.after(16, self.flash)  # ~60fps, matches the rise animation's smoothness

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
            pass  # window may have already been destroyed mid-flash

class GifBox:
    """A single, persistent animated gif shown directly on screen (no card/
    border around it). Created once, loops forever, and does not disappear
    until the caller explicitly closes it (see close())."""

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
            pass  # window was closed mid-frame

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

        # One persistent gif box, created once, placed just left of where the
        # left-side lyric boxes spawn — it stays up the whole time and is
        # only closed once every lyric has finished (see tick()).
        center_x = self.screen_w // 2
        left_box_left_edge = center_x - (BOX_W + 60)
        gap_px = int(self.root.winfo_fpixels(f"{GIF_GAP_CM}c"))

        gif_x = left_box_left_edge - GIF_BOX_W - gap_px
        gif_x = max(gif_x, 10)  # never let it spawn off the left edge

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
            # every lyric has appeared and floated away — lyrics are over,
            # so this is the moment the gif box is allowed to close
            self.gif_box.close()
            # comment the next line back in if you also want the song to
            # cut off at this exact moment instead of playing to the end
            # pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()