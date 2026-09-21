import tkinter as tk
import time
import os
import pygame

Script = os.path.dirname(os.path.abspath(__file__))
Audio_File = os.path.join (Script, "DADDY! DADDY! DO!.mp3")


LYRICS = [
    (0,   "Oikakecha dame na no wa"),
    (7,   "wakatteru demo murisa"),
    (14,  "Ichido fumidaseba modorenakute"),
    (16,  "kamen wa nugisutete"),
    (18,  "Ikenai koto made"),
    (22,  "Daddy, daddy, do Hoshii nosa"),
    (25,  "anata no subete ga"),
    (30,  "Damasaretara sore demo ii"),
    (36,  "motto furuwasete"),
    (41,  "Misetekure boku dake ni"),
    (45,  "egao no ura made"),
    (51,  "Ai ni dakare giragira"),
    (55,  "moete shimaitai")
]