import pygame
import time

pygame.mixer.init()
pygame.mixer.music.load("Totoong tayo.mp3")
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play()

print("Playing... waiting 10 seconds")
time.sleep(10)
print("Busy:", pygame.mixer.music.get_busy())