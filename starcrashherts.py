from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_PATH = BASE_DIR / "assets" / "main_menu_background.png"
TITLE_IMAGE_PATH = BASE_DIR / "New Piskel (18).gif"

WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "STAR CRASH"
MENU_ITEMS = ("START", "SETTINGS", "EXIT")


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
        raw_frames = pygame.image.load_animation(path)
    except (FileNotFoundError, pygame.error):
        return []

    frames = []
    for surface, duration in raw_frames:
        delay_ms = max(16, int(duration))
        frames.append((surface.convert_alpha(), delay_ms))
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


def make_button_rects(screen_rect):
    button_width = 280
    button_height = 56
    gap = 16
    top = screen_rect.centery + 52

    return [
        pygame.Rect(
            screen_rect.centerx - button_width // 2,
            top + index * (button_height + gap),
            button_width,
            button_height,
        )
        for index, _ in enumerate(MENU_ITEMS)
    ]


def draw_menu(screen, background, background_pos, title_font, item_font, selected_index, title_image):
    screen.blit(background, background_pos)

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 72))
    pygame.draw.rect(shade, (0, 0, 0, 120), (0, 0, screen.get_width(), screen.get_height()))
    screen.blit(shade, (0, 0))

    screen_rect = screen.get_rect()
    if title_image is not None:
        image_rect = title_image.get_rect(center=(screen_rect.centerx, 170))
        screen.blit(title_image, image_rect)
    else:
        draw_text(screen, TITLE, title_font, (230, 245, 245), (screen_rect.centerx, 170))
    draw_text(
        screen,
        "SURVIVE THE CRASH",
        item_font,
        (119, 214, 203),
        (screen_rect.centerx, 236),
    )

    mouse_pos = pygame.mouse.get_pos()
    button_rects = make_button_rects(screen_rect)

    hovered_index = selected_index
    for index, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            hovered_index = index

    for index, (label, rect) in enumerate(zip(MENU_ITEMS, button_rects)):
        active = index == hovered_index
        fill = (15, 29, 33, 210) if active else (9, 17, 21, 170)
        border = (244, 139, 46) if active else (69, 110, 116)
        text_color = (255, 230, 185) if active else (202, 220, 220)

        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=6)
        draw_text(screen, label, item_font, text_color, rect.center)

    return hovered_index, button_rects


def run_menu():
    pygame.init()
    pygame.display.set_caption("Star Crash")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    background_source = pygame.image.load(BACKGROUND_PATH).convert()
    background, background_pos = scale_to_fill(background_source, screen.get_size())

    title_animation = load_gif_animation(TITLE_IMAGE_PATH)

    title_font = pygame.font.SysFont("consolas", 76, bold=True)
    item_font = pygame.font.SysFont("consolas", 28, bold=True)
    selected_index = 0
    running = True
    animation_started_at = pygame.time.get_ticks()

    while running:
        title_image = get_animation_frame(
            title_animation,
            pygame.time.get_ticks() - animation_started_at,
        )
        selected_index, button_rects = draw_menu(
            screen,
            background,
            background_pos,
            title_font,
            item_font,
            selected_index,
            title_image,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_index = (selected_index - 1) % len(MENU_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_index = (selected_index + 1) % len(MENU_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if MENU_ITEMS[selected_index] == "EXIT":
                        running = False
                    else:
                        print(f"{MENU_ITEMS[selected_index]} selected")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        if MENU_ITEMS[index] == "EXIT":
                            running = False
                        else:
                            print(f"{MENU_ITEMS[index]} selected")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_menu()
