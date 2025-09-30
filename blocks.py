import math
import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 900, 560
BG = (22, 26, 30)
GRID = (36, 40, 45)
BLOCK_FILL = (43, 48, 54)
BLOCK_BORDER = (90, 100, 110)
ARROW_COLOR = (230, 235, 240)
TEXT_COLOR = (235, 240, 245)
FPS = 120
EDGE_NAMES = ["top", "right", "bottom", "left"]

# Distance used to push control points outward along edge directions
CONTROL_PUSH_MAX = 220
CONTROL_PUSH_RATIO = 0.42  # fraction of start->end distance (clamped by max)

# Arrowhead config
ARROW_HEAD_LEN = 14
ARROW_HEAD_ANGLE = math.radians(25)
CURVE_SAMPLES = 48  # segments when drawing the bezier


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
        # label
        text = font.render(self.label, True, TEXT_COLOR)
        tw, th = text.get_size()
        surface.blit(text, (self.rect.centerx - tw // 2, self.rect.centery - th // 2))

    def anchor_point(self, edge_name):
        r = self.rect
        if edge_name == "top":
            return pygame.Vector2(r.centerx, r.top)
        if edge_name == "right":
            return pygame.Vector2(r.right, r.centery)
        if edge_name == "bottom":
            return pygame.Vector2(r.centerx, r.bottom)
        if edge_name == "left":
            return pygame.Vector2(r.left, r.centery)
        raise ValueError("Invalid edge name")

    def edge_dir(self, edge_name):
        if edge_name == "top":
            return pygame.Vector2(0, -1)
        if edge_name == "right":
            return pygame.Vector2(1, 0)
        if edge_name == "bottom":
            return pygame.Vector2(0, 1)
        if edge_name == "left":
            return pygame.Vector2(-1, 0)
        raise ValueError("Invalid edge name")


def cubic_bezier(p0, p1, p2, p3, t):
    """Return point on cubic bezier at t in [0,1]."""
    u = 1 - t
    return (u**3) * p0 + 3 * (u**2) * t * p1 + 3 * u * (t**2) * p2 + (t**3) * p3


def cubic_bezier_tangent(p0, p1, p2, p3, t):
    """First derivative of cubic bezier at t in [0,1]."""
    u = 1 - t
    # 3*( -u^2*p0 + (u^2 - 2u t)*p1 + (2u t - t^2)*p2 + t^2*p3 ) is another form,
    # but this common expanded form is simple:
    return 3 * ( (p1 - p0) * (u**2) + 2 * (p2 - p1) * u * t + (p3 - p2) * (t**2) )


def draw_bezier(surface, p0, p1, p2, p3, color, width=3, samples=CURVE_SAMPLES):
    prev = p0
    for i in range(1, samples + 1):
        t = i / samples
        pt = cubic_bezier(p0, p1, p2, p3, t)
        pygame.draw.line(surface, color, prev, pt, width)
        prev = pt


def draw_arrowhead(surface, tip, direction, color):
    """Draw a triangular arrowhead at 'tip' with pointing vector 'direction'."""
    if direction.length() == 0:
        return
    d = direction.normalize()
    # Rotate direction by +/- ARROW_HEAD_ANGLE
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
    """Compute control points so the curve leaves/enters along the chosen edges nicely."""
    span = (p_end - p_start).length()
    push = min(CONTROL_PUSH_MAX, span * CONTROL_PUSH_RATIO)

    c1 = p_start + dir_start * push
    # For the end control, pull back from the end along the end-edge direction
    c2 = p_end - dir_end * push
    return c1, c2


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mermaid-like Blocks with Curved Arrow (Pygame)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    # Blocks
    a = Block(160, 180, 180, 90, "Block A")
    b = Block(560, 280, 180, 90, "Block B")

    # Which edges the arrow should attach to:
    start_edge = "right"   # change via keys 1-4
    end_edge = "left"      # change via keys 5-8

    running = True
    dragging_target = None

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if a.contains(event.pos):
                    dragging_target = a
                    a.start_drag(event.pos)
                elif b.contains(event.pos):
                    dragging_target = b
                    b.start_drag(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_target:
                    dragging_target.stop_drag()
                    dragging_target = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_target:
                    dragging_target.drag(event.pos)

            elif event.type == pygame.KEYDOWN:
                # Start edge
                if event.key == pygame.K_1: start_edge = "top"
                if event.key == pygame.K_2: start_edge = "right"
                if event.key == pygame.K_3: start_edge = "bottom"
                if event.key == pygame.K_4: start_edge = "left"
                # End edge
                if event.key == pygame.K_5: end_edge = "top"
                if event.key == pygame.K_6: end_edge = "right"
                if event.key == pygame.K_7: end_edge = "bottom"
                if event.key == pygame.K_8: end_edge = "left"

        # ---- Draw ----
        screen.fill(BG)
        draw_grid(screen)

        a.draw(screen, font)
        b.draw(screen, font)

        # Compute anchors and dirs
        p0 = a.anchor_point(start_edge)
        d0 = a.edge_dir(start_edge)
        p3 = b.anchor_point(end_edge)
        d3 = -b.edge_dir(end_edge)

        # Compute control points
        c1, c2 = nice_controls(p0, d0, p3, d3)

        # Draw the curve (slightly thicker underlay for anti-alias look)
        draw_bezier(screen, p0, c1, c2, p3, (0, 0, 0), width=5)
        draw_bezier(screen, p0, c1, c2, p3, ARROW_COLOR, width=3)

        # Arrowhead using tangent at t=1
        tangent = cubic_bezier_tangent(p0, c1, c2, p3, 1.0)
        draw_arrowhead(screen, p3, tangent, ARROW_COLOR)

        # HUD text
        hud = font.render(
            f"Start edge: {start_edge.upper()} (1-4)   End edge: {end_edge.upper()} (5-8)   Drag blocks with mouse",
            True, (180, 190, 200),
        )
        screen.blit(hud, (16, 16))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

