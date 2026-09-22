import tkinter as tk
import time
import os
import pygame

SCRIPT = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join (SCRIPT, "DADDY! DADDY! DO!.mp3")


LYRICS = [
    (0,   "Oikakecha dame na no wa"),
    (4,   "wakatteru demo murisa"),
    (7.5,   "Ichido fumidaseba modorenakute"),
    (11,  "kamen wa nugisutete"),
    (15,  "Ikenai koto made"),
    (18,  "asobi ga maji ni naru"),
    (23,  "Daddy, daddy, do Hoshii nosa"),
    (27,  "anata no subete ga"),
    (30,  "Damasaretara sore demo ii"),
    (34,  "motto furuwasete"),
    (37,  "Misetekure boku dake ni"),
    (41,  "egao no ura made"),
    (44,  "Ai ni dakare giragira"),
    (47,  "moete shimaitai")
]

BOX_A, BOX_B = 350, 300
FONT = ("Bebas Neue", 25, "italic")
BG_COLOR = "#FFFFFF"
FG_COLOR = "#000000"
RISE_SPEED = 100
BOTTOM_SPAWN_OFFSET = 200

class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{BOX_A}x{BOX_B}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        # White card needs a visible border since it blends into most desktops
        border = tk.Frame(self.win, bg="#CCCCCC", bd=0)
        border.pack(expand=True, fill="both", padx=1, pady=1)
        inner = tk.Frame(border, bg=BG_COLOR)
        inner.pack(expand=True, fill="both", padx=1, pady=1)

        self.full_text = text

        self.label = tk.Label(
            inner, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            wraplength=BOX_A - 25, justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        self.typewriter_index = 0
        self.typewriter()

        self.x = x
        self.y = float(y)

    def rise(self, dy):
        self.y -= dy
        self.win.geometry(f"{BOX_A}x{BOX_B}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_B < -50

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(110, self.typewriter)

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
        spacing = BOX_B + 60
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
            y = self.screen_h - BOX_B - BOTTOM_SPAWN_OFFSET
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
            # animation done — leave the song playing to the end;
            # comment the next line back in if you want it to cut off here instead
            # pygame.mixer.music.stop()
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()