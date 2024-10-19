import pygame
import os
import sys
from random import randint, choice
from constants import *

def resource_path(relative_path: str) -> str:

    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def save_path(relative_path: str) -> str:

    if getattr(sys, 'frozen', False): return os.path.join(os.getenv('APPDATA'), '08BitPixels/Google Dino Game/', relative_path)
    else: return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Google Dino Game')
pygame.display.set_icon(pygame.image.load(resource_path('images/Player/PlayerStand.png')).convert_alpha())
clock = pygame.time.Clock()
main_font = pygame.font.Font(resource_path('fonts/BBB_Simulator_Black.otf'), 50)

class Game:

	def __init__(self) -> None:

		self.active = False

		# Audio
		self.death_sound = pygame.mixer.Sound(resource_path('audio/die.wav'))
		self.death_sound.set_volume(1)
		self.point_sound = pygame.mixer.Sound(resource_path('audio/point.wav'))
		self.point_sound.set_volume(1)

		# Timers
		self.obst_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obst_timer, 1000)
		self.bird_frame_timer = pygame.USEREVENT + 2
		pygame.time.set_timer(self.bird_frame_timer, 200)
		
		# Title Text
		self.nametxt_surf = main_font.render('GOOGLE DINO GAME', False, (64, 64, 64))
		self.nametxt_rect = self.nametxt_surf.get_rect(center = (WIDTH / 2, 50))

		self.gameovertxt_surf = main_font.render('GAME OVER', False, (64, 64, 64))
		self.gameovertxt_rect = self.gameovertxt_surf.get_rect(center = (WIDTH / 2, 50))

		# Instruction Text
		self.instrtxt_surf = main_font.render('SPACE to Begin', False, (64, 64, 64))
		self.instrtxt_rect = self.instrtxt_surf.get_rect(center = (WIDTH / 2, HEIGHT - 50))

		# Score, Highscore

		self.load_save()

		self.current_time = 0
		self.start_time = 0
		self.score = 0
		self.highscore_beaten = False

		self.score_surf = main_font.render(f'{self.current_time:06}', False, (16, 16, 16))
		self.score_rect = self.score_surf.get_rect(midright = (WIDTH - 50, 50))

		self.hiscore_surf = main_font.render(f'HI {self.highscore:06}', False, (64, 64, 64))
		self.hiscore_rect = self.hiscore_surf.get_rect(midright = (WIDTH - 275, 50))

		# Objects
		self.player = pygame.sprite.GroupSingle()
		self.player.add(Player())
		self.enemy_group = pygame.sprite.Group()
		self.ground = pygame.sprite.Group()
		self.ground.add(Ground(0), Ground(2404))

	def check_collision(self) -> None:

		if pygame.sprite.spritecollide(self.player.sprite, self.enemy_group, False, pygame.sprite.collide_rect):
			if pygame.sprite.spritecollide(self.player.sprite, self.enemy_group, False, pygame.sprite.collide_mask):

				self.death_sound.play()
				self.active = False

	def update_score(self) -> None:

		if self.score > self.highscore: 
			
			if self.highscore_beaten == False and self.score > 1: self.point_sound.play()
			self.highscore = self.score
			self.highscore_beaten = True

		self.current_time = int(pygame.time.get_ticks() / 100) - self.start_time

		self.score_surf = main_font.render(f'{self.current_time:06}', False, (16, 16, 16))
		self.hiscore_surf = main_font.render(f'HI {self.highscore:06}', False, (64, 64, 64))

		self.score = self.current_time

	def save(self, high_score: int) -> None:

		print('Saving...')
		with open(save_path('saves/saves.txt'), 'w') as saves: saves.writelines(f'highscore={high_score}')
		print('Saved')

	def load_save(self) -> None:

		if os.path.isdir(save_path('saves\\')):

			with open(save_path('saves/saves.txt'), 'r') as saves: self.highscore = int(saves.readlines()[0].split('=')[1].strip('\n'))

		else:

			print('No save file present; creating new one...')
			os.makedirs(save_path('saves\\'))
			self.save(high_score = 0, costume_num = 0)
			self.highscore = 0

	def restart(self) -> None:

		self.player.sprite.reset()
		self.enemy_group.empty()
		self.ground.empty()
		self.ground.add(Ground(0), Ground(2404))
		self.start_time = int(pygame.time.get_ticks() / 100)
		self.active = True
		self.highscore_beaten = False
		self.hiscore_rect = self.hiscore_surf.get_rect(midright = (WIDTH - 275, 50))

class Enemy(pygame.sprite.Sprite):

	def __init__(self, type) -> None:

		super().__init__()

		# Images
		if type == 'Cactus':

			cact_1 = pygame.image.load(resource_path('images/cactus/Cactus1.png')).convert_alpha()
			self.frames = [cact_1]
			self.frame_vel = 0
			y_pos = 315

		elif type == 'Bird':
			
			bird_1 = pygame.image.load(resource_path('images/Bird/Bird1.png')).convert_alpha()
			bird_2 = pygame.image.load(resource_path('images/Bird/Bird2.png')).convert_alpha()
			self.frames = [bird_1, bird_2]
			self.frame_vel = 0.05
			y_pos = 240

		self.frame_index = 0
		self.scroll_vel = 3

		self.image = self.frames[self.frame_index]
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect(midbottom = (WIDTH + randint(0, 300), y_pos))

	def update(self) -> None:

		self.animate()
		self.scroll()

	def scroll(self) -> None:

		self.rect.centerx -= self.scroll_vel
		if self.rect.right < 0: self.kill()
	
	def animate(self) -> None:
		
		self.frame_index += self.frame_vel
		self.frame_index %= len(self.frames)
		self.image = self.frames[int(self.frame_index)]
		self.mask = pygame.mask.from_surface(self.image)

class Player(pygame.sprite.Sprite):

	def __init__(self) -> None:

		# Images
		self.jump1 = pygame.image.load(resource_path('images/Player/PlayerStand.png')).convert_alpha()
		self.walk1 = pygame.image.load(resource_path('images/Player/PlayerWalk1.png')).convert_alpha()
		self.walk2 = pygame.image.load(resource_path('images/Player/PlayerWalk2.png')).convert_alpha()
		self.duck1 = pygame.image.load(resource_path('images/Player/PlayerDuck1.png')).convert_alpha()
		self.duck2 = pygame.image.load(resource_path('images/Player/PlayerDuck2.png')).convert_alpha()

		# Audio
		self.jump_sound = pygame.mixer.Sound(resource_path('audio/jump.wav'))
		self.jump_sound.set_volume(1)
 
		super().__init__()
		self.image = self.walk1
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect(midbottom = (200, 300))

		# Intro Screen
		self.intro = self.jump1
		self.intro = pygame.transform.scale2x(self.intro)
		self.intro_rect = self.intro.get_rect(center = (WIDTH / 2, HEIGHT / 2))

		# Variables
		self.grav = 0
		self.jump_vel = -7
		self.fall_vel = 0.15
		self.ducking = False
		self.walk_frames = [self.walk1, self.walk2]
		self.duck_frames = [self.duck1, self.duck2]
		self.frame_index = 0
		self.animation_vel = 0.1

		self.reset()

	def update(self) -> None:

		self.fall()
		self.animate()
		self.input()

	def input(self) -> None:

		keys = pygame.key.get_pressed()
		mouse_pressed = pygame.mouse.get_pressed()

		if (keys[pygame.K_SPACE] or mouse_pressed[0]) and self.on_ground() and not self.ducking: self.jump()
		if (keys[pygame.K_DOWN] or mouse_pressed[2]) and self.on_ground():

			self.duck()
			self.ducking = True
		
		else: self.ducking = False

	def animate(self) -> None:

		if self.on_ground() and not self.ducking:
				
			self.frame_index += self.animation_vel 
			self.frame_index %= len(self.walk_frames)
			self.image = self.walk_frames[int(self.frame_index)]
			self.mask = pygame.mask.from_surface(self.image)
			self.rect = self.image.get_rect(midbottom = (80, 315))

		elif not self.on_ground(): self.image = self.jump1
			
	def fall(self) -> None:

		self.grav += self.fall_vel
		self.rect.y += self.grav

		if self.on_ground(): self.rect.bottom = 315

	def jump(self) -> None:

		self.grav = self.jump_vel
		self.jump_sound.play()

	def duck(self) -> None:

		self.frame_index += self.animation_vel 
		self.frame_index %= len(self.duck_frames)
		self.image = self.duck_frames[int(self.frame_index)]
		self.rect = self.image.get_rect(midbottom = (80, 315))

	def on_ground(self) -> bool:
		return True if self.rect.bottom >= 315 else False

	def reset(self) -> None:

		self.frame_index = 0
		self.grav = 0
		self.image = self.jump1
		self.rect = self.image.get_rect(midbottom = (80, 315))

class Ground(pygame.sprite.Sprite):
	
	def __init__(self, x_offset) -> None:

		super().__init__()
		self.image = pygame.image.load(resource_path('images/Ground.png')).convert_alpha()
		self.rect = self.image.get_rect(center = (0, HEIGHT - 100))

		self.rect.x = x_offset
		self.scroll_vel = 3
	
	def update(self) -> None:
		self.scroll()

	def scroll(self) -> None:

		self.rect.x -= self.scroll_vel
		if self.rect.right < 0: self.rect.left = WIDTH

def main():

	# Objects
	game = Game()
	player = game.player
	enemy_group = game.enemy_group
	ground = game.ground
	
	while True:

		# Pygame Event Loop
		for event in pygame.event.get():
			
			# Close Window
			if event.type == pygame.QUIT:

				game.save(game.highscore)
				pygame.quit()
				exit()

			if game.active:

				# Timers
				if event.type == game.obst_timer:

					enemy_group.add(Enemy(choice(['Cactus', 'Bird'])))

			else:

				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
					game.restart()                

		if game.active:

			screen.fill('#e3e3e3')

			# Ground
			ground.draw(screen)
			ground.update()

			# Enemy
			enemy_group.draw(screen)
			enemy_group.update()

			# Player
			player.draw(screen)
			player.update()

			# Game
			game.check_collision()
			game.update_score()
			screen.blit(game.score_surf, game.score_rect)
			screen.blit(game.hiscore_surf, game.hiscore_rect)
		
		else:

			screen.fill((200, 200, 200))

			if game.score == 0: 
				
				screen.blit(game.nametxt_surf, game.nametxt_rect)

			else: 
				
				game.score_rect = game.score_surf.get_rect(midright = (WIDTH - 50, 50))
				screen.blit(game.score_surf, game.score_rect)
				game.hiscore_rect = game.hiscore_surf.get_rect(midright = (WIDTH - 50, 100))
				screen.blit(game.hiscore_surf, game.hiscore_rect)
				screen.blit(game.gameovertxt_surf, game.gameovertxt_rect)
				  
			screen.blit(game.instrtxt_surf, game.instrtxt_rect)
			screen.blit(player.sprite.intro, player.sprite.intro_rect)

		pygame.display.update()
		clock.tick(FPS)

main()