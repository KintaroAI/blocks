import pygame
import random
from blocks_lib import *

# https://materialui.co/colors
# ---------- Config ----------
WIDTH, HEIGHT = 900, 800

EAR_COLOR1 = (27, 94, 32)
EYE_COLOR1 = (1, 87, 155)
SKIN_COLOR1 = (245, 127, 23)

EAR_COLOR2 = (56, 142, 60)
EYE_COLOR2 = (2, 136, 209)
SKIN_COLOR2 = (251, 192, 45)

EAR_COLOR3 = (77, 182, 172)
EYE_COLOR3 = (3, 169, 244)

EYE_EAR_COLOR = (79, 195, 247)

EYE_COLOR4 = (100, 181, 246)

MOTOR_AREA_COLOR1 = (171, 71, 188)
MOTOR_AREA_COLOR2 = (186, 104, 200)

COGNITIVE_COLOR4 = (136, 14, 79)
COGNITIVE_COLOR3 = (194, 24, 91)
COGNITIVE_COLOR2 = (233, 30, 99)
COGNITIVE_COLOR1 = (240, 98, 146)


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Blocks
    a = Block(460, 50, 400, 200, "Thalamus")
    b = Block(330, 360, 100, 400, "Cortex")
    ear = Block(10, 50, 100, 100, "Ear")
    skin = Block(10, 200, 100, 100, "Skin")
    eye = Block(10, 350, 100, 100, "Eye")
    movement = Block(10, 500, 100, 100, "Movement")
    note_sorted = Block(560, 300, 200, 100, "Topographically sorted", 100)
    note_brain = Block(610, 690, 280, 100, "Data flow in the human brain", 100)
    blocks = [a, b, ear, eye, skin, movement]
    notes = [note_sorted, note_brain]
    
    # Connections: three lines A:right -> B:left with offsets, with animated sparks
    connections = []
    # sensory input
    for t in range(-4, 5, 4):
        connections.append(Connection((ear, "right", t/10), (a, "left", -0.5+random.random()), color=EAR_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))
        connections.append(Connection((eye, "right", t/10), (a, "left", -0.5+random.random()), color=EYE_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))
        connections.append(Connection((skin, "right", t/10), (a, "left", -0.5+random.random()), color=SKIN_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))
        connections.append(Connection((movement, "right", t/10), (a, "left", -0.5+random.random()), color=MOTOR_AREA_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))

    # cortex -> cortex
    for _ in range(5):
        connections.append(Connection((b, "left", -0.5+random.random()), (b, "right", -0.5+random.random()), color=ARROW_COLOR, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))

    connections_per_area = 1
    # eye1, eye2, eye3, eye4, ear_eye, ear3, ear2, ear1, skin1, skin2, motor_area, cognitive1, cognitive2, cognitive3, cognitive4
    # thalamus output: total 15 areas (as an example)
    # thalamus to cortex
    for area, color in enumerate([EYE_COLOR1, EYE_COLOR2, EYE_COLOR3, EYE_COLOR4, EYE_EAR_COLOR, EAR_COLOR3, EAR_COLOR2, EAR_COLOR1, SKIN_COLOR2, SKIN_COLOR1, MOTOR_AREA_COLOR1, COGNITIVE_COLOR1, COGNITIVE_COLOR2, COGNITIVE_COLOR3, COGNITIVE_COLOR4]):
        area = area / 15 + 0.05
        for t in range(connections_per_area):
            connections.append(Connection((a, "bottom", 0.5 - (area + t/30)), (b, "right", 0.5 - (area + t/30)), color=color, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))

    # eye2, eye3, eye4, ear_eye, ear3, ear2, skin2, motor_area, cognitive1, cognitive2, cognitive3, cognitive4
    # cortex output: total 12 areas
    # cortex to thalamus
    for area, color in enumerate([EYE_COLOR2, EYE_COLOR3, EYE_COLOR4, EYE_EAR_COLOR, EAR_COLOR3, EAR_COLOR2, SKIN_COLOR2, MOTOR_AREA_COLOR1, COGNITIVE_COLOR1, COGNITIVE_COLOR2, COGNITIVE_COLOR3, COGNITIVE_COLOR4]):
        area = area / 13
        for t in range(connections_per_area):
            connections.append(Connection((b, "left", 0.4 - (area + t/26)), (a, "left", -0.5+random.random()), color=color, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))
            if color == MOTOR_AREA_COLOR1:
                connections.append(Connection((b, "left", 0.4 - (area + t/26)), (movement, "bottom", -0.33), color=MOTOR_AREA_COLOR2, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))
                connections.append(Connection((b, "left", 0.4 - (area + t/26)), (movement, "bottom", 0.33), color=MOTOR_AREA_COLOR2, width=3, sparks=3, spark_speed=0.7 + random.random()/4, **create_conn_kwargs(args)))

    # Run the main loop
    run_main_loop(screen, blocks, connections, notes, args, "Mermaid-like Blocks with Curved Arrows (offsets + sparks)")


if __name__ == "__main__":
    main()