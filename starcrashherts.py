from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_PATH = BASE_DIR / "задний фон меню.png"
TITLE_IMAGE_PATH = BASE_DIR / "New Piskel (18).gif"
START_BUTTON_PATH = BASE_DIR / "start.gif"
SETTINGS_BUTTON_PATH = BASE_DIR / "settings.gif"
EXIT_BUTTON_PATH = BASE_DIR / "exit.gif"

WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "STAR CRASH"
MENU_ITEMS = ("START", "SETTINGS", "EXIT")
TITLE_IMAGE_WIDTH = 450
START_BUTTON_WIDTH = 280
SETTINGS_BUTTON_WIDTH = 280
EXIT_BUTTON_WIDTH = 280
SAVE_SLOT_COUNT = 4
FADE_DURATION_MS = 450


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

    if not frames:
        return []

    return frames


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

    bounds = frames[0][0].get_bounding_rect(min_alpha=1)
    for surface, _ in frames[1:]:
        bounds.union_ip(surface.get_bounding_rect(min_alpha=1))

    if bounds.width == 0 or bounds.height == 0:
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
    slot_width = 360
    slot_height = 130
    horizontal_gap = 36
    vertical_gap = 28
    grid_width = slot_width * 2 + horizontal_gap
    left = screen_rect.centerx - grid_width // 2
    top = 205

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
    heading_font,
    slot_font,
    info_font,
    selected_index,
    confirmed_index,
):
    screen.fill((0, 0, 0))
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
    hovered_index = selected_index
    for index, rect in enumerate(slot_rects):
        if rect.collidepoint(mouse_pos):
            hovered_index = index

    for index, rect in enumerate(slot_rects):
        active = index == hovered_index
        confirmed = index == confirmed_index
        fill = (17, 28, 31) if active else (7, 12, 14)
        border = (244, 139, 46) if active else (57, 91, 95)
        if confirmed:
            border = (85, 216, 177)

        card_rect = rect.inflate(10, 8) if active else rect
        pygame.draw.rect(screen, fill, card_rect, border_radius=10)
        pygame.draw.rect(screen, border, card_rect, width=3, border_radius=10)

        if active:
            glow_rect = card_rect.inflate(8, 8)
            pygame.draw.rect(
                screen,
                (244, 139, 46),
                glow_rect,
                width=1,
                border_radius=12,
            )

        draw_text(
            screen,
            f"SLOT {index + 1}",
            slot_font,
            (255, 230, 185) if active else (205, 220, 220),
            (card_rect.centerx, card_rect.centery - 18),
        )
        draw_text(
            screen,
            "SELECTED" if confirmed else "EMPTY",
            info_font,
            (85, 216, 177) if confirmed else (93, 145, 148),
            (card_rect.centerx, card_rect.centery + 28),
        )

    draw_text(
        screen,
        "ESC - BACK",
        info_font,
        (90, 105, 108),
        (screen_rect.centerx, 650),
    )
    return hovered_index, slot_rects


def draw_menu(
    screen,
    background,
    background_pos,
    title_font,
    item_font,
    selected_index,
    title_image,
    start_image,
    settings_image,
    exit_image,
):
    screen.blit(background, background_pos)

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 72))
    pygame.draw.rect(shade, (0, 0, 0, 120), (0, 0, screen.get_width(), screen.get_height()))
    screen.blit(shade, (0, 0))

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

    hovered_index = selected_index
    for index, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            hovered_index = index

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

    return hovered_index, button_rects


def run_menu():
    pygame.init()
    pygame.display.set_caption("Star Crash")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    background_source = pygame.image.load(BACKGROUND_PATH).convert()
    background, background_pos = scale_to_fill(background_source, screen.get_size())

    title_animation = scale_animation_frames(
        load_gif_animation(TITLE_IMAGE_PATH),
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

        button_rects = []
        slot_rects = []
        if current_scene == "menu":
            selected_index, button_rects = draw_menu(
                screen,
                background,
                background_pos,
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
                save_heading_font,
                save_slot_font,
                save_info_font,
                selected_slot_index,
                confirmed_slot_index,
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

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_menu()
