import math
import pygame
import random
import argparse
import os

# https://materialui.co/colors
# ---------- Config ----------
WIDTH, HEIGHT = 900, 900
BG = (22, 26, 30)
#BG = (255, 255, 255)
GRID = (36, 40, 45)
BLOCK_FILL = (43, 48, 54)
BLOCK_BORDER = (90, 100, 110)
ARROW_COLOR = (230, 235, 240)
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

MOTOR_AREA_COLOR = (171, 71, 188)

COGNITIVE_COLOR4 = (136, 14, 79)
COGNITIVE_COLOR3 = (194, 24, 91)
COGNITIVE_COLOR2 = (233, 30, 99)
COGNITIVE_COLOR1 = (240, 98, 146)

TEXT_COLOR = (235, 240, 245)
FPS = 120

CONTROL_PUSH_MAX = 320
CONTROL_PUSH_RATIO = 0.42  # fraction of start->end distance (clamped by max)

ARROW_HEAD_LEN = 14
ARROW_HEAD_ANGLE = math.radians(25)
CURVE_SAMPLES = 48  # segments when drawing the bezier


def parse_args():
    p = argparse.ArgumentParser(description="Mermaid-like blocks with curved arrows (offsets + sparks)")
    p.add_argument("-o", "--save-prefix", default=None,
                   help="If set, save frames as PREFIX000001.png, PREFIX000002.png, ...")
    p.add_argument("--frame-skip", type=int, default=1,
                   help="Save every N-th frame (default: 1 = every frame)")
    p.add_argument("--start-index", type=int, default=1,
                   help="Starting index for saved frames (default: 1)")
    p.add_argument("--max-frames", type=int, default=0,
                   help="Stop after saving this many frames (0 = unlimited)")
    return p.parse_args()

def draw_grid(surface, gap=24):
    w, h = surface.get_size()
    for x in range(0, w, gap):
        pygame.draw.line(surface, GRID, (x, 0), (x, h), 1)
    for y in range(0, h, gap):
        pygame.draw.line(surface, GRID, (0, y), (w, y), 1)


class Block:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.dragging = False
        self.drag_offset = (0, 0)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def start_drag(self, pos):
        self.dragging = True
        self.drag_offset = (pos[0] - self.rect.x, pos[1] - self.rect.y)

    def drag(self, pos):
        if self.dragging:
            self.rect.x = pos[0] - self.drag_offset[0]
            self.rect.y = pos[1] - self.drag_offset[1]

    def stop_drag(self):
        self.dragging = False

    def draw(self, surface, font):
        pygame.draw.rect(surface, BLOCK_FILL, self.rect, border_radius=14)
        pygame.draw.rect(surface, BLOCK_BORDER, self.rect, width=2, border_radius=14)
        text = font.render(self.label, True, TEXT_COLOR)
        tw, th = text.get_size()
        surface.blit(text, (self.rect.centerx - tw // 2, self.rect.centery - th // 2))

    def edge_dir(self, edge_name):
        if edge_name == "top":    return pygame.Vector2(0, -1)
        if edge_name == "right":  return pygame.Vector2(1, 0)
        if edge_name == "bottom": return pygame.Vector2(0, 1)
        if edge_name == "left":   return pygame.Vector2(-1, 0)
        raise ValueError("Invalid edge name")

    def anchor_point_with_offset(self, edge_name, t):
        """
        Return a point on the given edge, offset by t in [-0.5, 0.5] from the center
        along the edge direction (t=0 center; +/-0.5 near corners).
        """
        t = max(-0.5, min(0.5, float(t)))  # clamp
        r = self.rect
        if edge_name in ("top", "bottom"):
            x = r.centerx + r.w * t
            y = r.top if edge_name == "top" else r.bottom
            return pygame.Vector2(x, y)
        elif edge_name in ("left", "right"):
            x = r.left if edge_name == "left" else r.right
            y = r.centery + r.h * t
            return pygame.Vector2(x, y)
        else:
            raise ValueError("Invalid edge name")


def cubic_bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3) * p0 + 3 * (u**2) * t * p1 + 3 * u * (t**2) * p2 + (t**3) * p3


def cubic_bezier_tangent(p0, p1, p2, p3, t):
    u = 1 - t
    return 3 * ((p1 - p0) * (u**2) + 2 * (p2 - p1) * u * t + (p3 - p2) * (t**2))


def draw_bezier(surface, p0, p1, p2, p3, color, width=3, samples=CURVE_SAMPLES):
    prev = p0
    for i in range(1, samples + 1):
        t = i / samples
        pt = cubic_bezier(p0, p1, p2, p3, t)
        pygame.draw.line(surface, color, prev, pt, width)
        prev = pt


def draw_arrowhead(surface, tip, direction, color):
    if direction.length() == 0:
        return
    d = direction.normalize()
    left = pygame.Vector2(
        d.x * math.cos(ARROW_HEAD_ANGLE) - d.y * math.sin(ARROW_HEAD_ANGLE),
        d.x * math.sin(ARROW_HEAD_ANGLE) + d.y * math.cos(ARROW_HEAD_ANGLE),
    )
    right = pygame.Vector2(
        d.x * math.cos(-ARROW_HEAD_ANGLE) - d.y * math.sin(-ARROW_HEAD_ANGLE),
        d.x * math.sin(-ARROW_HEAD_ANGLE) + d.y * math.cos(-ARROW_HEAD_ANGLE),
    )
    p1 = tip
    p2 = tip - left * ARROW_HEAD_LEN
    p3 = tip - right * ARROW_HEAD_LEN
    pygame.draw.polygon(surface, color, (p1, p2, p3))


def nice_controls(p_start, dir_start, p_end, dir_end):
    span = (p_end - p_start).length()
    push = min(CONTROL_PUSH_MAX, span * CONTROL_PUSH_RATIO)
    c1 = p_start + dir_start * push
    c2 = p_end - dir_end * push  # dir_end should be INTO the end block
    return c1, c2


def brighten(rgb, delta=25):
    r = min(255, rgb[0] + delta)
    g = min(255, rgb[1] + delta)
    b = min(255, rgb[2] + delta)
    return (r, g, b)


class Connection:
    """
    Curved arrow with optional animated 'sparks' moving from start -> end.
    - start: (block, edge, offset [-0.5..0.5])
    - end:   (block, edge, offset [-0.5..0.5])
    - color: line color
    - width: line width in px
    - sparks: int, number of moving dots (0 disables)
    - spark_speed: float, units of t per second (0..1 loops)
    - spark_color: optional color; default is slightly brighter than 'color'
    """
    def __init__(
        self,
        start,
        end,
        color=ARROW_COLOR,
        width=3,
        sparks=0,
        spark_speed=0.6,
        spark_color=None,
    ):
        self.start_block, self.start_edge, self.start_t = start
        self.end_block, self.end_edge, self.end_t = end
        self.color = color
        self.width = width
        self.sparks = int(max(0, sparks))
        self.spark_speed = float(max(0.0, spark_speed))
        self.spark_color = spark_color if spark_color else brighten(color, 30)
        # Phase offsets for each spark so they are spaced evenly
        self._spark_phase = [i / max(1, self.sparks) for i in range(self.sparks)]

    def endpoints(self):
        p0 = self.start_block.anchor_point_with_offset(self.start_edge, self.start_t)
        d0 = self.start_block.edge_dir(self.start_edge)
        p3 = self.end_block.anchor_point_with_offset(self.end_edge, self.end_t)
        d3 = -self.end_block.edge_dir(self.end_edge)  # into the block
        return p0, d0, p3, d3

    def controls(self, p0, d0, p3, d3):
        return nice_controls(p0, d0, p3, d3)

    def draw(self, surface):
        p0, d0, p3, d3 = self.endpoints()
        c1, c2 = self.controls(p0, d0, p3, d3)

        # Curve (shadow + stroke)
        draw_bezier(surface, p0, c1, c2, p3, (0, 0, 0), width=self.width + 2)
        draw_bezier(surface, p0, c1, c2, p3, self.color, width=self.width)

        # Arrowhead points toward the end block
        tangent = cubic_bezier_tangent(p0, c1, c2, p3, 1.0)
        draw_arrowhead(surface, p3, tangent, self.color)

        return (p0, c1, c2, p3)  # return curve for sparks

    def draw_sparks(self, surface, curve_points, elapsed_time):
        if self.sparks <= 0 or self.spark_speed <= 0:
            return
        p0, c1, c2, p3 = curve_points

        # Spark dot size: 1px bigger than connection width
        # We'll render a circle whose DIAMETER = width + 1
        radius = max(1, (self.width + 5) // 2)

        for phase in self._spark_phase:
            # t progresses with time; wrap around [0,1)
            t = (phase + elapsed_time * self.spark_speed) % 1.0
            pt = cubic_bezier(p0, c1, c2, p3, t)
            pygame.draw.circle(surface, self.spark_color, (int(pt.x), int(pt.y)), radius)


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mermaid-like Blocks with Curved Arrows (offsets + sparks)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    # Blocks
    a = Block(460, 50, 100, 400, "Thalamus")
    b = Block(460, 460, 100, 400, "Cortex")
    ear = Block(10, 50, 100, 100, "Ear")
    skin = Block(10, 200, 100, 100, "Skin")
    eye = Block(10, 350, 100, 100, "Eye")
    blocks = [a, b, ear, eye, skin]

    # Connections: three lines A:right -> B:left with offsets, with animated sparks
    connections = []
    for t in range(-5, 5, 1):
        connections.append(Connection((ear, "right", t/10), (a, "left", -0.5+random.random()), color=EAR_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4))
        connections.append(Connection((eye, "right", t/10), (a, "left", -0.5+random.random()), color=EYE_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4))
        connections.append(Connection((skin, "right", t/10), (a, "left", -0.5+random.random()), color=SKIN_COLOR1, width=3, sparks=3, spark_speed=0.7 + random.random()/4))

    for _ in range(5):
        connections.append(Connection((b, "bottom", -0.5+random.random()), (b, "right", -0.5+random.random()), color=ARROW_COLOR, width=3, sparks=3, spark_speed=0.7 + random.random()/4))

    connections_per_area = 2
    # eye1, eye2, eye3, eye4, ear_eye, ear3, ear2, ear1, skin1, skin2, motor_area, cognitive1, cognitive2, cognitive3, cognitive4
    # thalamus output: total 15 areas (as an example)
    for area, color in enumerate([EYE_COLOR1, EYE_COLOR2, EYE_COLOR3, EYE_COLOR4, EYE_EAR_COLOR, EAR_COLOR3, EAR_COLOR2, EAR_COLOR1, SKIN_COLOR2, SKIN_COLOR1, MOTOR_AREA_COLOR, COGNITIVE_COLOR1, COGNITIVE_COLOR2, COGNITIVE_COLOR3, COGNITIVE_COLOR4]):
        area = area / 15
        for t in range(connections_per_area):
            connections.append(Connection((a, "right", 0.5 - (area + t/30)), (b, "right", -0.5+area + t/30), color=color, width=3, sparks=3, spark_speed=0.7 + random.random()/4))

    # eye2, eye3, eye4, ear_eye, ear3, ear2, skin2, motor_area, cognitive1, cognitive2, cognitive3, cognitive4
    # cortex output: total 12 areas
    for area, color in enumerate([EYE_COLOR2, EYE_COLOR3, EYE_COLOR4, EYE_EAR_COLOR, EAR_COLOR3, EAR_COLOR2, SKIN_COLOR2, MOTOR_AREA_COLOR, COGNITIVE_COLOR1, COGNITIVE_COLOR2, COGNITIVE_COLOR3, COGNITIVE_COLOR4]):
        area = area / 13
        for t in range(connections_per_area):
            connections.append(Connection((b, "left", - 0.5 + (area + t/26)), (a, "left", -0.5+random.random()), color=color, width=3, sparks=3, spark_speed=0.7 + random.random()/4))




    dragging_target = None
    running = True
    elapsed = 0.0  # seconds since start
    # --- Export init ---
    save_prefix = args.save_prefix
    frame_skip = max(1, int(args.frame_skip))
    start_idx = max(0, int(args.start_index))
    max_frames = max(0, int(args.max_frames))
    frames_saved = 0
    frame_index = start_idx
    frame_counter = 0
    if save_prefix:
        outdir = os.path.dirname(save_prefix)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

    while running:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for block in blocks:
                    if block.contains(event.pos):
                        dragging_target = block; block.start_drag(event.pos)
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_target:
                    dragging_target.stop_drag()
                    dragging_target = None
            elif event.type == pygame.MOUSEMOTION and dragging_target:
                dragging_target.drag(event.pos)

        # ---- Draw ----
        screen.fill(BG)
        draw_grid(screen)
        for block in blocks:
            block.draw(screen, font)

        # Draw all connections & their sparks
        for conn in connections:
            curve = conn.draw(screen)
            conn.draw_sparks(screen, curve, elapsed)

        hud = font.render(
            "Drag blocks. Offsets: -0.5..0.5 along edges from center. Sparks per-connection.",
            True, (180, 190, 200),
        )
        #screen.blit(hud, (16, 16))

        # --- Save frame if requested ---
        frame_counter += 1
        if save_prefix and (frame_counter % frame_skip == 0):
            filename = f"{save_prefix}{frame_index:06d}.png"
            pygame.image.save(screen, filename)
            frame_index += 1
            frames_saved += 1
            if max_frames and frames_saved >= max_frames:
                running = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
