import pygame
import sys
import gui as gui
import threading

def startscreen():
    # Initialize pygame
    pygame.init()

    # Constants
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    FONT = pygame.font.SysFont("Teacher", 40)
    SMALL_FONT = pygame.font.SysFont("Teacher", 30)

    # Setup screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(WHITE)
    pygame.display.set_caption("Sudoku vs AI done by 8150-8197-8138")

    # Text title setup (replaces logo)
    title_text = "Sudoku"
    title_font_size = 150  # Adjust this to control how big the title appears
    TITLE_FONT = pygame.font.SysFont("Teacher", title_font_size)
    title_surface = TITLE_FONT.render(title_text, True, BLACK)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))  # Adjust y=120 to move up/down

    # Checkbox (now only one)
    checkbox_size = 20
    checkbox_rect = pygame.Rect((SCREEN_WIDTH - checkbox_size) // 2, 250, checkbox_size, checkbox_size)
    logging = False

    # Buttons
    button_texts = ["AI Solving Example puzzle", "Input your puzzle", "Generate Puzzle"]
    buttons = []
    button_width = 450
    button_height = 50
    button_spacing = 20
    br = 12
    start_y = 340

    for i, text in enumerate(button_texts):
        rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + i * (button_height + button_spacing),
            button_width,
            button_height
        )
        buttons.append((text, rect))

    selected_mode = None

    # Main menu loop
    running = True
    while running:
        screen.fill(WHITE)

        # Draw text logo
        screen.blit(title_surface, title_rect)

        # Checkbox and label
        pygame.draw.rect(screen, WHITE, checkbox_rect, border_radius=br)
        pygame.draw.rect(screen, BLACK, checkbox_rect, 2, border_radius=br)
        if logging:
            pygame.draw.line(screen, BLACK, (checkbox_rect.x, checkbox_rect.y), (checkbox_rect.x + checkbox_size, checkbox_rect.y + checkbox_size), 3)
            pygame.draw.line(screen, BLACK, (checkbox_rect.x + checkbox_size, checkbox_rect.y), (checkbox_rect.x, checkbox_rect.y + checkbox_size), 3)

        checkbox_label = SMALL_FONT.render("Logging", True, BLACK)
        checkbox_label_rect = checkbox_label.get_rect()
        checkbox_label_rect.midleft = (checkbox_rect.x + checkbox_size + 10, checkbox_rect.y + checkbox_size // 2)
        screen.blit(checkbox_label, checkbox_label_rect)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        for text, rect in buttons:
            pygame.draw.rect(screen, WHITE, rect, border_radius=br)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=br)

            label = SMALL_FONT.render(text, True, BLACK)
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if checkbox_rect.collidepoint(event.pos):
                    logging = not logging

                for mode, rect in buttons:
                    if rect.collidepoint(event.pos):
                        selected_mode = mode
                        running = False

        pygame.display.update()
    if selected_mode == "AI Solving Example puzzle":
        selected_mode = 0
    elif selected_mode == "Input your puzzle":
            selected_mode = 1
    else:
        selected_mode = 2
    

    print(f"Selected Mode: {selected_mode}")
    
    print(f"logging: {logging}")
    pygame.quit()
    return selected_mode, logging




