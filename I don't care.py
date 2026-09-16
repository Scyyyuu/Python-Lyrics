import time

lyrics = [
    "'Cause I don't care when I'm with my baby, yeah",
    "All the bad things disappear",
    "And you're making me feel like maybe I am somebody",
    "I can deal with the bad nights",
    "When I'm with my baby, yeah"

]

line_delays = [1, 1, 1, 1, 1]  # seconds to pause AFTER each line — adjust these by ear

for line, delay in zip(lyrics, line_delays):
    for letter in line:
        print(letter, end="", flush=True)
        time.sleep(0.05)  # typing speed per letter — adjust to taste
    print()  # move to a new line after the line finishes typing
    time.sleep(delay)  # pause before the next line starts