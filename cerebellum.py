import pygame
from blocks_lib import *

# ---------- Config ----------
WIDTH, HEIGHT = 1000, 720

# Palette buckets (reuse your tones)
MOTOR_1 = (171, 71, 188)
MOTOR_2 = (186, 104, 200)
SENSORY_1 = (77, 182, 172)
SENSORY_2 = (3, 169, 244)
CEREBELLUM = (240, 98, 146)
BASAL = (245, 127, 23)
THALAMUS = (1, 87, 155)
OLFACT = (56, 142, 60)


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # --- Blocks (positions chosen to mirror TD flow) ---
    A = Block(390, 30, 220, 80, "Motor Cortex")
    B = Block(390, 130, 220, 80, "Corticospinal Tract")
    C = Block(360, 230, 280, 80, "Spinal Cord<br/>Lower Motor Neurons")
    D = Block(390, 330, 220, 80, "Peripheral Nerves")
    E = Block(390, 430, 220, 80, "Muscles")

    F = Block(340, 540, 320, 80, "Movement & Sensory Feedback")
    G = Block(70, 540, 260, 80, "Spinal Cord Feedback")
    H = Block(720, 280, 220, 110, "Thalamus")

    I = Block(70, 130, 200, 80, "Pons")
    J = Block(70, 230, 200, 80, "Cerebellum")

    K = Block(720, 70, 220, 80, "Basal Ganglia")
    L = Block(720, 430, 220, 80, "Olfactory Input")

    blocks = [A, B, C, D, E, F, G, H, I, J, K, L]

    connections = []

    # Cortex loop (A -> B -> C -> D -> E)
    chain_color = MOTOR_1
    for (s, e) in [(A, B), (B, C), (C, D), (D, E)]:
        connections.append(Connection((s, "bottom", 0.0), (e, "top", 0.0),
                                      color=chain_color, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))

    # Sensory feedback (E -> F), then F -> G and F -> H
    connections.append(Connection((E, "bottom", 0.0), (F, "top", 0.0),
                                  color=SENSORY_1, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))
    connections.append(Connection((F, "left", 0.0), (G, "right", 0.0),
                                  color=SENSORY_2, width=3, sparks=2, spark_speed=0.7, **create_conn_kwargs(args)))
    connections.append(Connection((F, "right", 0.0), (H, "bottom", 0.0),
                                  color=SENSORY_2, width=3, sparks=2, spark_speed=0.7, **create_conn_kwargs(args)))

    # Cerebellum loop (A -> I -> J -> H)
    connections.append(Connection((A, "left", -0.2), (I, "right", -0.2),
                                  color=CEREBELLUM, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))
    connections.append(Connection((I, "bottom", 0.0), (J, "top", 0.0),
                                  color=CEREBELLUM, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))
    connections.append(Connection((J, "right", 0.0), (H, "left", -0.1),
                                  color=CEREBELLUM, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))

    # Basal ganglia (K -> H)
    connections.append(Connection((K, "bottom", 0.0), (H, "top", 0.0),
                                  color=BASAL, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))

    # Thalamus hub (H -> A)
    connections.append(Connection((H, "right", 0.0), (A, "right", 0.0),
                                  color=THALAMUS, width=3, sparks=4, spark_speed=0.9, **create_conn_kwargs(args)))

    # Exception: Olfactory (L -> A)
    connections.append(Connection((L, "left", 0.0), (A, "bottom", 0.3),
                                  color=OLFACT, width=3, sparks=3, spark_speed=0.8, **create_conn_kwargs(args)))

    # Run the main loop
    run_main_loop(screen, blocks, connections, None, args, "Neuro Flow: Motor/Sensory/Cerebellum/Basal/Thalamus")


if __name__ == "__main__":
    main()