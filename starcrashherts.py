import math
import random
from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
SAVE_SLOTS_BACKGROUND_PATH = BASE_DIR / "assets" / "save_slots_background.png"
SAVE_SLOT_BUTTON_BACKGROUND_PATH = BASE_DIR / "задний фон кнопки в слотах.gif"
BACKGROUND_PATH = BASE_DIR / "задний фон меню.png"
TITLE_IMAGE_PATH = BASE_DIR / "New Piskel (18).gif"
START_BUTTON_PATH = BASE_DIR / "start.gif"
SETTINGS_BUTTON_PATH = BASE_DIR / "settings.gif"
EXIT_BUTTON_PATH = BASE_DIR / "exit.gif"
CURSOR_PATH = BASE_DIR / "курсор.gif"
PRESSED_CURSOR_PATH = BASE_DIR / "зажатый курсор.gif"
SLOTS_DIR = BASE_DIR / "slots"

WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "STAR CRASH"
MENU_ITEMS = ("START", "SETTINGS", "EXIT")
TITLE_IMAGE_WIDTH = 450
START_BUTTON_WIDTH = 280
SETTINGS_BUTTON_WIDTH = 280
EXIT_BUTTON_WIDTH = 280
CURSOR_WIDTH = 24
SAVE_SLOT_BUTTON_WIDTH = 330
SAVE_SLOT_LABEL_WIDTH = 180
SAVE_SLOT_COUNT = 4
FADE_DURATION_MS = 450
COSMIC_MOTE_COUNT = 18
SHOOTING_STAR_CYCLE_MS = 6500
SHOOTING_STAR_DURATION_MS = 950
BACKGROUND_STAR_POINTS = (
    (141, 55, 2),
    (497, 56, 2),
    (363, 78, 2),
    (654, 90, 2),
    (928, 90, 2),
    (1233, 95, 3),
    (204, 143, 1),
    (1148, 150, 2),
    (1594, 189, 1),
    (838, 195, 2),
    (82, 200, 2),
    (1050, 239, 3),
    (260, 256, 3),
    (428, 285, 2),
    (1320, 294, 2),
    (1565, 327, 2),
    (1192, 378, 1),
    (568, 419, 2),
    (941, 430, 1),
    (1315, 441, 2),
    (371, 471, 2),
    (1594, 470, 2),
)


def scale_to_fill(surface, size):
    target_width, target_height = size
    source_width, source_height = surface.get_size()
    scale = max(target_width / source_width, target_height / source_height)
    scaled_size = (int(source_width * scale), int(source_height * scale))
    scaled = pygame.transform.smoothscale(surface, scaled_size)
    x = (target_width - scaled_size[0]) // 2
    y = (target_height - scaled_size[1]) // 2
    return scaled, (x, y)


def draw_text(screen, text, font, color, center):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    screen.blit(rendered, rect)
    return rect


def load_gif_animation(path):
    try:
        raw_frames = pygame.image.load_animation(str(path))
    except (FileNotFoundError, pygame.error, AttributeError):
        try:
            return [(pygame.image.load(str(path)).convert_alpha(), 1000)]
        except (FileNotFoundError, pygame.error):
            return []

    frames = []
    for surface, duration in raw_frames:
        delay_ms = max(16, int(duration))
        frames.append((surface.convert_alpha(), delay_ms))

    return frames


def create_ambient_stars(background_source, screen_size, background_pos):
    """Map the stars painted in the artwork to their exact screen positions."""
    source_width, source_height = background_source.get_size()
    width, height = screen_size
    scale = max(width / source_width, height / source_height)
    rng = random.Random(827)
    stars = []
    for source_x, source_y, size in BACKGROUND_STAR_POINTS:
        brightest = max(
            (
                background_source.get_at((x, y))[:3]
                for x in range(max(0, source_x - 3), min(source_width, source_x + 4))
                for y in range(max(0, source_y - 3), min(source_height, source_y + 4))
            ),
            key=sum,
        )
        color = tuple(min(245, round(channel * 1.28 + 18)) for channel in brightest)
        stars.append(
            (
                round(source_x * scale + background_pos[0]),
                round(source_y * scale + background_pos[1]),
                size,
                rng.uniform(0.0, math.tau),
                rng.uniform(1.55, 2.35),
                color,
            )
        )
    return stars


def create_cosmic_motes(size):
    """Create slow particles that rise only across the lower landscape."""
    width, height = size
    rng = random.Random(1409)
    colors = (
        (95, 155, 166),
        (172, 139, 91),
        (126, 155, 158),
    )
    motes = []
    for _ in range(COSMIC_MOTE_COUNT):
        motes.append(
            (
                rng.randrange(20, width - 20),
                rng.uniform(0.0, height * 0.35),
                rng.uniform(5.0, 12.0),
                rng.uniform(0.0, math.tau),
                rng.uniform(3.0, 9.0),
                rng.choice((1, 1, 1, 2)),
                rng.choice(colors),
            )
        )
    return motes


def draw_shooting_star(star_layer, elapsed_ms):
    """Draw one short pixel meteor followed by a long quiet pause."""
    cycle_index = elapsed_ms // SHOOTING_STAR_CYCLE_MS
    cycle_time = elapsed_ms % SHOOTING_STAR_CYCLE_MS
    if cycle_time >= SHOOTING_STAR_DURATION_MS:
        return

    progress = cycle_time / SHOOTING_STAR_DURATION_MS
    visibility = math.sin(progress * math.pi) ** 0.7
    width, _ = star_layer.get_size()
    direction = -1 if cycle_index % 2 else 1

    if direction > 0:
        head_x = round(-70 + progress * 540)
        head_y = round(82 + progress * 110)
        trail_direction = (-1, -0.22)
    else:
        head_x = round(width + 70 - progress * 500)
        head_y = round(118 + progress * 92)
        trail_direction = (1, -0.22)

    trail_length = 82
    tail_x = round(head_x + trail_direction[0] * trail_length)
    tail_y = round(head_y + trail_direction[1] * trail_length)
    alpha = round(150 * visibility)
    pygame.draw.line(
        star_layer,
        (166, 213, 220, round(alpha * 0.32)),
        (tail_x, tail_y),
        (head_x, head_y),
        1,
    )
    pygame.draw.line(
        star_layer,
        (224, 239, 228, alpha),
        (
            round(head_x + trail_direction[0] * 24),
            round(head_y + trail_direction[1] * 24),
        ),
        (head_x, head_y),
        2,
    )
    pygame.draw.rect(
        star_layer,
        (242, 213, 156, round(210 * visibility)),
        (head_x - 1, head_y - 1, 3, 3),
    )


def draw_animated_background(
    screen,
    background,
    background_pos,
    star_layer,
    ambient_stars,
    cosmic_motes,
    elapsed_ms,
):
    """Draw the untouched artwork plus restrained pixel-art ambience."""
    screen.blit(background, background_pos)
    star_layer.fill((0, 0, 0, 0))
    elapsed_seconds = elapsed_ms / 1000.0

    for x, y, size, phase, speed, color in ambient_stars:
        pulse = (math.sin(elapsed_seconds * speed + phase) + 1.0) / 2.0
        alpha = round(5 + 225 * pulse**2.4)
        if size == 3:
            ray = 4 + round(pulse * 7)
            ray_alpha = round(alpha * 0.72)
            pygame.draw.line(
                star_layer,
                (*color, ray_alpha),
                (x - ray, y),
                (x + ray, y),
            )
            pygame.draw.line(
                star_layer,
                (*color, ray_alpha),
                (x, y - ray),
                (x, y + ray),
            )
        elif pulse > 0.48:
            sparkle = (pulse - 0.48) / 0.52
            ray = 2 + round(sparkle * (3 if size == 2 else 2))
            ray_alpha = round(alpha * 0.62)
            pygame.draw.line(
                star_layer,
                (*color, ray_alpha),
                (x - ray, y),
                (x + ray, y),
            )
            pygame.draw.line(
                star_layer,
                (*color, ray_alpha),
                (x, y - ray),
                (x, y + ray),
            )
        center_size = max(2, size)
        pygame.draw.rect(
            star_layer,
            (*color, alpha),
            (
                x - center_size // 2,
                y - center_size // 2,
                center_size,
                center_size,
            ),
        )

    _, height = screen.get_size()
    mote_travel = height * 0.35
    for base_x, offset, speed, phase, drift, size, color in cosmic_motes:
        travelled = (offset + elapsed_seconds * speed) % mote_travel
        y = round(height - travelled)
        x = round(base_x + math.sin(elapsed_seconds * 0.45 + phase) * drift)
        fade = math.sin((travelled / mote_travel) * math.pi)
        alpha = round(55 * fade)
        pygame.draw.rect(star_layer, (*color, alpha), (x, y, size, size))

    draw_shooting_star(star_layer, elapsed_ms)


def get_animation_frame(frames, elapsed_ms):
    if not frames:
        return None

    total_duration = sum(duration for _, duration in frames)
    if total_duration <= 0:
        return frames[0][0]

    frame_time = elapsed_ms % total_duration
    for surface, duration in frames:
        if frame_time < duration:
            return surface
        frame_time -= duration

    return frames[-1][0]


def scale_animation_frames(frames, target_width):
    if not frames:
        return []

    source_width, source_height = frames[0][0].get_size()
    scale = target_width / source_width
    target_size = (target_width, round(source_height * scale))
    return [
        (pygame.transform.scale(surface, target_size), duration)
        for surface, duration in frames
    ]


def trim_animation_frames(frames):
    """Remove transparent margins while keeping every frame aligned."""
    if not frames:
        return []

    bounds = get_animation_bounds(frames)
    return crop_animation_frames(frames, bounds)


def get_animation_bounds(frames):
    """Return shared visible bounds so related sprites keep their alignment."""
    if not frames:
        return pygame.Rect(0, 0, 0, 0)

    bounds = frames[0][0].get_bounding_rect(min_alpha=1)
    for surface, _ in frames[1:]:
        bounds.union_ip(surface.get_bounding_rect(min_alpha=1))
    return bounds


def crop_animation_frames(frames, bounds):
    """Crop animation frames to precomputed shared bounds."""
    if not frames or bounds.width == 0 or bounds.height == 0:
        return frames

    return [
        (surface.subsurface(bounds).copy(), duration)
        for surface, duration in frames
    ]


def make_button_rects(screen_rect):
    button_width = 280
    button_height = 56
    gap = 16
    top = screen_rect.centery + 7

    return [
        pygame.Rect(
            screen_rect.centerx - button_width // 2,
            top + index * (button_height + gap),
            button_width,
            button_height,
        )
        for index, _ in enumerate(MENU_ITEMS)
    ]


def make_save_slot_rects(screen_rect):
    slot_width = 330
    slot_height = 108
    horizontal_gap = 54
    vertical_gap = 26
    grid_width = slot_width * 2 + horizontal_gap
    left = screen_rect.centerx - grid_width // 2
    top = 215

    return [
        pygame.Rect(
            left + (index % 2) * (slot_width + horizontal_gap),
            top + (index // 2) * (slot_height + vertical_gap),
            slot_width,
            slot_height,
        )
        for index in range(SAVE_SLOT_COUNT)
    ]


def draw_save_slots(
    screen,
    background,
    background_pos,
    slot_button_background,
    heading_font,
    slot_font,
    info_font,
    selected_index,
    confirmed_index,
    slot_images,
):
    screen.blit(background, background_pos)
    screen_rect = screen.get_rect()

    draw_text(
        screen,
        "SELECT SAVE SLOT",
        heading_font,
        (235, 242, 242),
        (screen_rect.centerx, 108),
    )
    draw_text(
        screen,
        "CHOOSE A SLOT TO START",
        info_font,
        (93, 145, 148),
        (screen_rect.centerx, 153),
    )

    mouse_pos = pygame.mouse.get_pos()
    slot_rects = make_save_slot_rects(screen_rect)
    # Hover is temporary and must not become the persistent slot selection.
    hovered_index = None
    for index, rect in enumerate(slot_rects):
        if rect.collidepoint(mouse_pos):
            hovered_index = index
            break

    for index, rect in enumerate(slot_rects):
        active = index == hovered_index
        confirmed = index == confirmed_index
        button_center = (rect.centerx, rect.top + 44)
        button_image = slot_button_background
        if button_image is not None:
            if active:
                width, height = button_image.get_size()
                button_image = pygame.transform.scale(
                    button_image,
                    (round(width * 1.05), round(height * 1.05)),
                )
            button_rect = button_image.get_rect(center=button_center)
            screen.blit(button_image, button_rect)
        else:
            button_rect = pygame.Rect(0, 0, SAVE_SLOT_BUTTON_WIDTH, 66)
            button_rect.center = button_center
            pygame.draw.rect(
                screen,
                (7, 12, 14),
                button_rect,
                border_radius=12,
            )
            pygame.draw.rect(
                screen,
                (225, 235, 232),
                button_rect,
                width=2,
                border_radius=12,
            )

        slot_image = slot_images[index] if index < len(slot_images) else None
        if slot_image is not None:
            if active:
                width, height = slot_image.get_size()
                slot_image = pygame.transform.scale(
                    slot_image,
                    (round(width * 1.04), round(height * 1.04)),
                )
            image_rect = slot_image.get_rect(
                center=button_center,
            )
            screen.blit(slot_image, image_rect)
        else:
            draw_text(
                screen,
                f"SLOT {index + 1}",
                slot_font,
                (255, 230, 185) if active else (205, 220, 220),
                button_center,
            )

        status_color = (85, 216, 177) if confirmed else (93, 145, 148)
        if active and not confirmed:
            status_color = (244, 166, 91)
        draw_text(
            screen,
            "SELECTED" if confirmed else "EMPTY",
            info_font,
            status_color,
            (rect.centerx, rect.bottom - 9),
        )

        if confirmed:
            marker_y = rect.bottom - 9
            pygame.draw.rect(
                screen,
                (85, 216, 177),
                (rect.centerx - 61, marker_y - 2, 4, 4),
            )
            pygame.draw.rect(
                screen,
                (85, 216, 177),
                (rect.centerx + 57, marker_y - 2, 4, 4),
            )

    draw_text(
        screen,
        "ESC - BACK",
        info_font,
        (90, 105, 108),
        (screen_rect.centerx, 650),
    )
    return selected_index, slot_rects


def draw_menu(
    screen,
    background,
    background_pos,
    star_layer,
    ambient_stars,
    cosmic_motes,
    elapsed_ms,
    title_font,
    item_font,
    selected_index,
    title_image,
    start_image,
    settings_image,
    exit_image,
):
    draw_animated_background(
        screen,
        background,
        background_pos,
        star_layer,
        ambient_stars,
        cosmic_motes,
        elapsed_ms,
    )

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 72))
    pygame.draw.rect(shade, (0, 0, 0, 120), (0, 0, screen.get_width(), screen.get_height()))
    screen.blit(shade, (0, 0))
    screen.blit(star_layer, (0, 0))

    screen_rect = screen.get_rect()
    if title_image is not None:
        image_rect = title_image.get_rect(center=(screen_rect.centerx, 165))
        screen.blit(title_image, image_rect)
    else:
        draw_text(screen, TITLE, title_font, (230, 245, 245), (screen_rect.centerx, 170))

    mouse_pos = pygame.mouse.get_pos()
    button_rects = make_button_rects(screen_rect)
    custom_button_images = {
        "START": start_image,
        "SETTINGS": settings_image,
        "EXIT": exit_image,
    }
    custom_button_offsets = {
        "START": -20,
        "SETTINGS": 4,
        "EXIT": 32,
    }
    for label, button_image in custom_button_images.items():
        if button_image is None:
            continue
        index = MENU_ITEMS.index(label)
        original_rect = button_rects[index]
        button_rects[index] = button_image.get_rect(
            center=(
                original_rect.centerx,
                original_rect.centery + custom_button_offsets[label],
            ),
        )

    # Hover is temporary. It must not overwrite the keyboard selection,
    # otherwise the last hovered button stays visually pressed.
    hovered_index = None
    for index, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            hovered_index = index
            break

    for index, (label, rect) in enumerate(zip(MENU_ITEMS, button_rects)):
        active = index == hovered_index

        button_image = custom_button_images.get(label)
        if button_image is not None:
            if active:
                width, height = button_image.get_size()
                button_image = pygame.transform.scale(
                    button_image,
                    (round(width * 1.06), round(height * 1.06)),
                )
            image_rect = button_image.get_rect(center=rect.center)
            screen.blit(button_image, image_rect)
            continue

        fill = (15, 29, 33, 210) if active else (9, 17, 21, 170)
        border = (244, 139, 46) if active else (69, 110, 116)
        text_color = (255, 230, 185) if active else (202, 220, 220)
        button_rect = rect.inflate(18, 10) if active else rect.copy()
        if active:
            button_rect.move_ip(0, -4)

        shadow_offset = 9 if active else 4
        shadow_rect = button_rect.move(0, shadow_offset)
        pygame.draw.rect(screen, (0, 0, 0, 170), shadow_rect, border_radius=7)

        if active:
            glow_rect = button_rect.inflate(8, 6)
            pygame.draw.rect(screen, (244, 139, 46), glow_rect, width=1, border_radius=8)

        pygame.draw.rect(screen, fill, button_rect, border_radius=6)
        pygame.draw.rect(screen, border, button_rect, width=2, border_radius=6)
        if active:
            pygame.draw.line(
                screen,
                (255, 226, 152),
                (button_rect.left + 14, button_rect.top + 5),
                (button_rect.right - 14, button_rect.top + 5),
                2,
            )
        draw_text(screen, label, item_font, text_color, button_rect.center)

    return selected_index, button_rects


def run_menu():
    pygame.init()
    pygame.display.set_caption("Star Crash")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    background_source = pygame.image.load(BACKGROUND_PATH).convert()
    background, background_pos = scale_to_fill(background_source, screen.get_size())
    star_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    ambient_stars = create_ambient_stars(
        background_source,
        screen.get_size(),
        background_pos,
    )
    cosmic_motes = create_cosmic_motes(screen.get_size())
    save_slots_background_source = pygame.image.load(SAVE_SLOTS_BACKGROUND_PATH).convert()
    save_slots_background, save_slots_background_pos = scale_to_fill(
        save_slots_background_source,
        screen.get_size(),
    )
    save_slot_button_animation = scale_animation_frames(
        trim_animation_frames(
            load_gif_animation(SAVE_SLOT_BUTTON_BACKGROUND_PATH)
        ),
        SAVE_SLOT_BUTTON_WIDTH,
    )

    title_animation = scale_animation_frames(
        trim_animation_frames(load_gif_animation(TITLE_IMAGE_PATH)),
        TITLE_IMAGE_WIDTH,
    )
    start_animation = scale_animation_frames(
        trim_animation_frames(load_gif_animation(START_BUTTON_PATH)),
        START_BUTTON_WIDTH,
    )
    settings_animation = scale_animation_frames(
        trim_animation_frames(load_gif_animation(SETTINGS_BUTTON_PATH)),
        SETTINGS_BUTTON_WIDTH,
    )
    exit_animation = scale_animation_frames(
        trim_animation_frames(load_gif_animation(EXIT_BUTTON_PATH)),
        EXIT_BUTTON_WIDTH,
    )
    cursor_source_animation = load_gif_animation(CURSOR_PATH)
    pressed_cursor_source_animation = load_gif_animation(PRESSED_CURSOR_PATH)
    cursor_bounds = get_animation_bounds(
        cursor_source_animation + pressed_cursor_source_animation
    )
    cursor_animation = scale_animation_frames(
        crop_animation_frames(cursor_source_animation, cursor_bounds),
        CURSOR_WIDTH,
    )
    pressed_cursor_animation = scale_animation_frames(
        crop_animation_frames(pressed_cursor_source_animation, cursor_bounds),
        CURSOR_WIDTH,
    )
    slot_label_animations = [
        scale_animation_frames(
            trim_animation_frames(load_gif_animation(SLOTS_DIR / f"{index}.gif")),
            SAVE_SLOT_LABEL_WIDTH,
        )
        for index in range(1, SAVE_SLOT_COUNT + 1)
    ]

    title_font = pygame.font.SysFont("consolas", 76, bold=True)
    item_font = pygame.font.SysFont("consolas", 28, bold=True)
    save_heading_font = pygame.font.SysFont("consolas", 48, bold=True)
    save_slot_font = pygame.font.SysFont("consolas", 34, bold=True)
    save_info_font = pygame.font.SysFont("consolas", 19, bold=True)

    selected_index = 0
    selected_slot_index = 0
    confirmed_slot_index = None
    current_scene = "menu"
    transition_target = None
    transition_phase = None
    transition_started_at = 0
    running = True
    animation_started_at = pygame.time.get_ticks()
    fade_overlay = pygame.Surface(screen.get_size()).convert()
    fade_overlay.fill((0, 0, 0))

    while running:
        now = pygame.time.get_ticks()
        title_image = get_animation_frame(
            title_animation,
            now - animation_started_at,
        )
        start_image = get_animation_frame(
            start_animation,
            now - animation_started_at,
        )
        settings_image = get_animation_frame(
            settings_animation,
            now - animation_started_at,
        )
        exit_image = get_animation_frame(
            exit_animation,
            now - animation_started_at,
        )
        slot_images = [
            get_animation_frame(animation, now - animation_started_at)
            for animation in slot_label_animations
        ]
        slot_button_background = get_animation_frame(
            save_slot_button_animation,
            now - animation_started_at,
        )

        button_rects = []
        slot_rects = []
        if current_scene == "menu":
            selected_index, button_rects = draw_menu(
                screen,
                background,
                background_pos,
                star_layer,
                ambient_stars,
                cosmic_motes,
                now - animation_started_at,
                title_font,
                item_font,
                selected_index,
                title_image,
                start_image,
                settings_image,
                exit_image,
            )
        else:
            selected_slot_index, slot_rects = draw_save_slots(
                screen,
                save_slots_background,
                save_slots_background_pos,
                slot_button_background,
                save_heading_font,
                save_slot_font,
                save_info_font,
                selected_slot_index,
                confirmed_slot_index,
                slot_images,
            )

        if transition_phase is not None:
            transition_progress = min(
                1.0,
                (now - transition_started_at) / FADE_DURATION_MS,
            )
            if transition_phase == "out":
                fade_alpha = round(255 * transition_progress)
            else:
                fade_alpha = round(255 * (1.0 - transition_progress))
            fade_overlay.set_alpha(fade_alpha)
            screen.blit(fade_overlay, (0, 0))

            if transition_progress >= 1.0:
                if transition_phase == "out":
                    current_scene = transition_target
                    transition_phase = "in"
                    transition_started_at = now
                else:
                    transition_phase = None
                    transition_target = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif transition_phase is not None:
                continue
            elif current_scene == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        selected_index = (selected_index - 1) % len(MENU_ITEMS)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_index = (selected_index + 1) % len(MENU_ITEMS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        selected_item = MENU_ITEMS[selected_index]
                        if selected_item == "START":
                            transition_target = "save_slots"
                            transition_phase = "out"
                            transition_started_at = now
                        elif selected_item == "EXIT":
                            running = False
                        else:
                            print(f"{selected_item} selected")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for index, rect in enumerate(button_rects):
                        if not rect.collidepoint(event.pos):
                            continue
                        selected_index = index
                        selected_item = MENU_ITEMS[index]
                        if selected_item == "START":
                            transition_target = "save_slots"
                            transition_phase = "out"
                            transition_started_at = now
                        elif selected_item == "EXIT":
                            running = False
                        else:
                            print(f"{selected_item} selected")
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    transition_target = "menu"
                    transition_phase = "out"
                    transition_started_at = now
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    selected_slot_index = (selected_slot_index - 1) % SAVE_SLOT_COUNT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_slot_index = (selected_slot_index + 1) % SAVE_SLOT_COUNT
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_slot_index = (selected_slot_index - 2) % SAVE_SLOT_COUNT
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_slot_index = (selected_slot_index + 2) % SAVE_SLOT_COUNT
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    confirmed_slot_index = selected_slot_index
                    print(f"SAVE SLOT {confirmed_slot_index + 1} selected")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos):
                        selected_slot_index = index
                        confirmed_slot_index = index
                        print(f"SAVE SLOT {index + 1} selected")
                        break

        if pygame.mouse.get_focused():
            cursor_frames = (
                pressed_cursor_animation
                if pygame.mouse.get_pressed()[0]
                else cursor_animation
            )
            cursor_image = get_animation_frame(
                cursor_frames,
                now - animation_started_at,
            )
            if cursor_image is not None:
                screen.blit(cursor_image, pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_menu()
