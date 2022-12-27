##importing libraries - not reinventing the wheel
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import mediapipe as mp
import random
import pygame
import cv2

print('hello jagiya')

SCREEN_WIDTH = 960#1536
SCREEN_HEIGHT = 720#864
#pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect = self.surf.get_rect()

    def update(self, x, y):
        #self.rect = self.surf.get_rect(center=(x,y))
        self.rect = self.surf.get_rect(center=(960 * x, 720 * y))

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect = self.surf.get_rect(center = (
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT)))
        self.speed = random.randint(5, 20)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        self.rect = self.surf.get_rect(center = (
            random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
            random.randint(0, SCREEN_HEIGHT)))

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()

pygame.init()
pygame.mixer.init()
pygame.display.set_caption('4dot')
pygame.display.set_icon(pygame.image.load('me.jpg'))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 800)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 1500)

player = Player()

enemies = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

collision_sound = pygame.mixer.Sound("Collision.ogg")
collision_sound.set_volume(0.7)

##mediapipe_initialisation##
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

  pygame.mixer.music.load("wakeUp.mp3")
  pygame.mixer.music.play(loops=-1)

  while cap.isOpened():
    ret, frame = cap.read()

    image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    #image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
      landmarks = results.pose_landmarks.landmark
      WRIST = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    except:
      #print('--error occured--')
      continue
##
    for event in pygame.event.get():
        if event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        elif event.type == ADDCLOUD:
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

    player.update(WRIST[0], WRIST[1])

    enemies.update()
    clouds.update()

    screen.fill((135, 206, 250))

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    if pygame.sprite.spritecollideany(player, enemies):
        player.kill()
        i=0
        while i<5:
            collision_sound.play()
            i+=1
        break

    pygame.display.flip()
    clock.tick(30)
##
    mp.solutions.drawing_utils.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow('arhsim', image)

    if cv2.waitKey(1) == ord('q'):
      break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()
