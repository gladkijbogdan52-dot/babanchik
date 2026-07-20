from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_PATH = BASE_DIR / "assets" / "main_menu_background.png"

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


def make_button_rects(screen_rect):
    button_width = 280
    button_height = 56
    gap = 16
    total_height = len(MENU_ITEMS) * button_height + (len(MENU_ITEMS) - 1) * gap
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


def draw_menu(screen, background, background_pos, title_font, item_font, selected_index):
    screen.blit(background, background_pos)

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 72))
    pygame.draw.rect(shade, (0, 0, 0, 120), (0, 0, screen.get_width(), screen.get_height()))
    screen.blit(shade, (0, 0))

    screen_rect = screen.get_rect()
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

    title_font = pygame.font.SysFont("consolas", 76, bold=True)
    item_font = pygame.font.SysFont("consolas", 28, bold=True)
    selected_index = 0
    running = True

    while running:
        selected_index, button_rects = draw_menu(
            screen,
            background,
            background_pos,
            title_font,
            item_font,
            selected_index,
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
