import time

lyrics = [
    "line one",
    "line two",
    "line three"
]

for line in lyrics:
    for letter in line:
        print (letter, end="", flush=True)#
        ...
    time.sleep(1.5)