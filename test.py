import pygame
import random
import sys
import math

# --- CONSTANTS & CONFIG ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (Hex-inspired RGB)
BG_COLOR = (10, 10, 18)
PLAYER_COLOR = (0, 255, 204)    # Neon Cyan
ASTEROID_COLOR = (240, 80, 80) # Soft Red
STAR_COLOR = (255, 215, 0)     # Gold
PARTICLE_COLOR = (255, 165, 0) # Orange
TEXT_COLOR = (240, 240, 255)

# --- CLASS DEFINITIONS ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a triangular ship pointing up
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, PLAYER_COLOR, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30
        self.speed = 7

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Keep player within screen boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))


class FallingObject(pygame.sprite.Sprite):
    def __init__(self, obj_type):
        super().__init__()
        self.type = obj_type  # "asteroid" or "star"
        
        if self.type == "asteroid":
            self.radius = random.randint(15, 30)
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ASTEROID_COLOR, (self.radius, self.radius), self.radius)
            self.score_value = 0
        else: # Star
            self.radius = 12
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, STAR_COLOR, (self.radius, self.radius), self.radius)
            self.score_value = 50

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.uniform(3, 7)

    def update(self, speed_multiplier):
        # Apply difficulty multiplier to speed
        self.rect.y += self.speed_y * speed_multiplier
        
        # Kill sprite if it goes off the bottom
        if self.rect.top > HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(3, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Random velocity vector
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


# --- MAIN GAME FUNCTION ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cosmic Dodger")
    clock = pygame.time.Clock()

    # Fonts
    try:
        font_large = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 36)
    except:
        font_large = pygame.font.SysFont('arial', 64)
        font_small = pygame.font.SysFont('arial', 36)

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Ambient Background Stars (Visual only)
    bg_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(50)]

    # Custom spawn events
    SPAWN_ASTEROID = pygame.USEREVENT + 1
    SPAWN_STAR = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWN_ASTEROID, 600) # Spawn every 600ms
    pygame.time.set_timer(SPAWN_STAR, 2000)     # Spawn every 2 seconds

    # Game States & Variables
    score = 0
    high_score = 0
    game_over = False
    difficulty_multiplier = 1.0

    # --- MAIN LOOP ---
    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over:
                if event.type == SPAWN_ASTEROID:
                    obs = FallingObject("asteroid")
                    asteroids.add(obs)
                    all_sprites.add(obs)
                elif event.type == SPAWN_STAR:
                    star = FallingObject("star")
                    stars.add(star)
                    all_sprites.add(star)
            else:
                # Restart game on SPACE press if Game Over
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset everything
                    all_sprites.empty()
                    asteroids.empty()
                    stars.empty()
                    particles.empty()
                    
                    player = Player()
                    all_sprites.add(player)
                    
                    score = 0
                    difficulty_multiplier = 1.0
                    game_over = False

        # 2. Game Update Logic
        if not game_over:
            # Gradually increase difficulty over time
            difficulty_multiplier += 0.0002
            
            # Update all gameplay mechanics
            player.update()
            asteroids.update(difficulty_multiplier)
            stars.update(difficulty_multiplier)
            particles.update()

            # Passive scoring just for surviving
            score += 1

            # Check Collisions: Player vs Stars (Collection)
            star_hits = pygame.sprite.spritecollide(player, stars, True, pygame.sprite.collide_circle)
            for hit in star_hits:
                score += hit.score_value
                # Spawn "collect" particles
                for _ in range(10):
                    p = Particle(hit.rect.centerx, hit.rect.centery, STAR_COLOR)
                    particles.add(p)
                    all_sprites.add(p)

            # Check Collisions: Player vs Asteroids (Damage)
            if pygame.sprite.spritecollide(player, asteroids, False, pygame.sprite.collide_circle):
                game_over = True
                if score > high_score:
                    high_score = score
                # Explosion effect
                for _ in range(40):
                    p = Particle(player.rect.centerx, player.rect.centery, PARTICLE_COLOR)
                    particles.add(p)
                    all_sprites.add(p)
        else:
            # If game over, only update particles for a nice lingering explosion effect
            particles.update()

        # 3. Drawing / Rendering
        screen.fill(BG_COLOR)

        # Draw ambient starfield background
        for star_pos in bg_stars:
            pygame.draw.circle(screen, (80, 80, 100), star_pos, 1)

        # Draw all sprites (Players, obstacles, items, particles)
        all_sprites.draw(screen)

        # HUD Text (Score and Difficulty)
        score_txt = font_small.render(f"Score: {int(score)}", True, TEXT_COLOR)
        high_score_txt = font_small.render(f"High Score: {int(high_score)}", True, STAR_COLOR)
        screen.blit(score_txt, (15, 15))
        screen.blit(high_score_txt, (15, 50))

        # Game Over Overlay Screen
        if game_over:
            go_txt = font_large.render("GAME OVER", True, ASTEROID_COLOR)
            restart_txt = font_small.render("Press SPACE to Restart", True, TEXT_COLOR)
            
            # Center the text
            go_rect = go_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            restart_rect = restart_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            
            screen.blit(go_txt, go_rect)
            screen.blit(restart_txt, restart_rect)

        # Flip the display buffer
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()