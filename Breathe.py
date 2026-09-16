import time
from threading import Thread, Lock
import sys

lock = Lock()

def animate_text(text, delay=0.1):
    with lock:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

def sing_lyric (lyric, delay, speed):
    time.sleep (delay)
    animate_text (lyric, speed)

def sing_song():
    lyrics = [
        ("What's that supposed to be about, baby?", 0.05),
        ("Go free of your vibe, stop acting crazy", 0.06),
        ("You know I give you the good loving daily", 0.05),
        ("Try and pull that, got me actin' shady", 0.05),
        ("ohhhhhhhhhhh", 0.05),
    ]
    delays = [1.0, 2.0, 5.6, 8.6, 10.0]

    threads = []
    for i in range(len(lyrics)):
        lyric, speed = lyrics[i]
        t = Thread(target=sing_lyric, args=(lyric, delays[i], speed))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    sing_song()

