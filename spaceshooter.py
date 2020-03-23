#!/usr/bin/env python3

import pygame
import random
import sys

class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        # Equivalent statements:
        #pygame.sprite.Sprite.__init__(self)
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render('Score: 0        Lives: 5')   
        
    def render(self, text):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.image.blit(self.text, self.rect)
    
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    def update(self, game, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))

#Enemy Starship
class BasicEnemy(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        #Health is the amount of shots it takes to finish one of them off
        self.health = 1 * game.difficulty
        #explosion sound
        self.deathSound = pygame.mixer.Sound("assets/enemyDead.mp3")
        #Different enemy ships as the game progresses
        if(game.difficulty < 10):
            self.image = pygame.image.load("assets/enemyShip" + str(game.difficulty) + ".PNG")
        #Only a limited number of pictures though. Once you've been through 9 rounds, just keep showing picture 9
        else:
            self.image = pygame.image.load("assets/enemyShip" + str(9) + ".PNG")
        self.rect = self.image.get_rect()
        #the position doesn't matter too much, since it gets set again when the game creates enemies
        self.rect.x = 50
        self.rect.y = 30
        self.direction = 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    #Basically, will check if the enemy is dead. IF not, then move!
    def update(self, game, doIChange):
        if (self.health < 1):
            game.enemies.remove(self)
            self.deathSound.play()
            game.score += game.difficulty
        if(doIChange):
            self.direction *= -1
            self.rect.y += 20
        if(self.direction == 1):
            self.rect.x += 1
        if(self.direction == -1):
            self.rect.x -= 1
        #Enemies wrap around from bottom back to top
        if(self.rect.y > 585):
            self.rect.y = 20

class Stars(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #2 different pictures. The big one occurs 20% of the time, the small one 80%. The small one is star1
        if(random.randint(0, 4) != 4):
            self.image = pygame.image.load('assets/star1.PNG')
        else:
            self.image = pygame.image.load('assets/star2.PNG')
        self.rect = self.image.get_rect()
        self.rect.x = (random.randint(0, 760))
        self.rect.y = 0
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    #Will just move the stars.
    def update(self, game):
        self.rect.y +=5
        if(self.rect.y > 585):
            game.stars.remove(self)

#User's starship
class Hero(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/heroShip.PNG')
        self.rect = self.image.get_rect()
        #Starting position
        self.rect.x = 375
        self.rect.y = 570
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def update(self, game, ugprades):
        #The hero can only hit the upgrades and the start button. This will let them choose upgrades and start each round.
        hitUpgrades = pygame.sprite.spritecollideany(self, game.upgrades)
        hitStart = pygame.sprite.spritecollideany(self, game.starting)
        #Which upgrade to upgrade which stat?
        if (hitUpgrades):
            if(hitUpgrades.numType == 0):
                game.heroDamage += 1
            if(hitUpgrades.numType == 1):
                game.heroMovementSpeed += 3
            if(hitUpgrades.numType == 2):
                game.heroAttackSpeed /= 1.3
            game.upgrades.empty()
            game.chooseUpgrade = True
        #Start the next round
        if (hitStart):
            game.chooseUpgrade = False
            game.resetMap = True
            game.starting.empty()

#Simple button sprite
class StartRoundButton(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/startRound.PNG')
        self.rect = self.image.get_rect()
        self.rect.x = 375
        self.rect.y = 570

#Bullet of the user's starship
class Bullet(pygame.sprite.Sprite):
    #Give bullet the hero object so that it can position itself off of hero
    def __init__(self, game, heroShip):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/Bullet.PNG')
        self.rect = self.image.get_rect()
        self.rect.x = heroShip.rect.x
        self.rect.y = heroShip.rect.y
        #Ting sound
        self.hit_sound = pygame.mixer.Sound("assets/enemyHit.wav")
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def update(self, game, enemies):
        #Movement is fast
        self.rect.y -= 10
        #If too high, delete self
        if(self.rect.y < 9):
            game.bullets.remove(self)
        #If I hit object, will play the sound, remove myself, and damage enemy.
        hitObject = pygame.sprite.spritecollideany(self, enemies)
        if (hitObject):
            hitObject.health -= game.heroDamage
            self.hit_sound.play()
            game.bullets.remove(self)


#Bullet of the enemy starship
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, game, enemyShip, bulletType):
        self.myType = bulletType
        pygame.sprite.Sprite.__init__(self)
        #Two types of bullets. Bullet 1 is a slow, blue circle.
        #Bullet 2 is a fast, red laser.
        #As the game progresses, each one will appear at different rates. Explain later.
        if(self.myType == 1):
            self.image = pygame.image.load('assets/enemyBullet1.PNG')
        if(self.myType == 2):
            self.image = pygame.image.load('assets/enemyBullet2.PNG')
        self.rect = self.image.get_rect()
        self.rect.x = enemyShip.rect.x
        self.rect.y = enemyShip.rect.y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, game, heroShip):
        #Depending on type, the speeds are different. Red is twice as fast.
        if(self.myType == 1):
            self.rect.y += 2
        if(self.myType == 2):
            self.rect.y += 4
        if(self.rect.y > 585):
            game.enemyBullets.remove(self)
        #if I hit the hero, damage him.
        hitObject = pygame.sprite.collide_rect(self, heroShip)
        if (hitObject):
            game.lives -= 1
            game.enemyBullets.remove(self)

#Upgrades sprite, for upgrading inbetween rounds!!!!
class Upgrades(pygame.sprite.Sprite):
    #Gonna use upgrades!
    #Three seperate upgrades, but I want to use them in a group, so I will implement them all here
    def __init__(self, game, num):
        pygame.sprite.Sprite.__init__(self)
        self.numType = num
        self.image = pygame.image.load("assets/upgradePic" + str(self.numType) + ".PNG")
        self.rect = self.image.get_rect()
        #Position depending on num. There 3 numbers, 0, 1, and 2. However, if someone gives me a bad number, it'll default to 2.
        if(num == 0):
            self.rect.y = 100
            self.rect.x = 100
        elif(num == 1):
            self.rect.y = 100
            self.rect.x = 350
        else:
            self.rect.y = 100
            self.rect.x = 550

    def draw(self, screen):
        screen.blit(self.image, self.rect)

#Main method
class Game:
    def __init__(self):
        pygame.init()
        # Credit to Toby Fox for his song Megolavania which is an absolute bopper, from his 10/10 my favorite game
        # Undertale. If you haven't played it, you neeeeeed to, imo. Go in blind, too. Very important.
        pygame.mixer.music.load('assets/loopSong.MP3')

        pygame.mixer.music.play(-1)
        pygame.key.set_repeat(50)

        self.clock = pygame.time.Clock()
        self.bullets = pygame.sprite.Group()
        self.enemyBullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.upgrades = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.starting = pygame.sprite.Group()

        self.hero = Hero()

        self.overlay = Overlay()

        self.screen = pygame.display.set_mode((800, 600))

        self.lives = 5
        self.heroDamage = 1
        self.heroAttackSpeed = 250
        self.heroMovementSpeed = 7
        #Tracks score. Each enemy counts for as many points as the difficulty. Round 1, difficulty 1, each enemy is worth 1.
        #Round 2, difficulty 2, each enemy is worth 2, etc. etc.
        self.score = 0
        #Tracks difficulty, +1 every round.
        self.difficulty = 0
        #Time for shoot is a timer. The hero's attack speed is in ms. So, after 250 ms (counted by this timeForShoot), the hero can attack again.
        #Resets after a shot.
        self.timeForShoot = 0

        self.done = False
        self.doIChange = False
        self.canShoot = True
        self.chooseUpgrade = False
        self.resetMap = True

    def run(self):
        while(not self.done):
            self.doIChange = False
            #I have no idea why it works the way it does, but testing things out this makes the movement the slickest.
            #and it requires the event thing, too. wack. However, this rocks because if you have it under the event handler, it cna only do one thing at a time.
            #If you do movement like this, you can move in several directions and shoot at the same time!!!
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                if(self.hero.rect.y > 15):
                    self.hero.rect.y -= self.heroMovementSpeed
            if keys[pygame.K_RIGHT]:
                if(self.hero.rect.x < 768):
                    self.hero.rect.x += self.heroMovementSpeed
            if keys[pygame.K_DOWN]:
                if(self.hero.rect.y < 575):
                    self.hero.rect.y += self.heroMovementSpeed
            if keys[pygame.K_LEFT]:
                if(self.hero.rect.x > 15):
                    self.hero.rect.x -= self.heroMovementSpeed
            if keys[pygame.K_ESCAPE]:
                self.done = True
            if keys[pygame.K_SPACE]:
                #Give bullet the hero object so that it can position itself off of hero
                if(self.canShoot == True and self.timeForShoot == 0):
                    this = Bullet(self, self.hero)
                    self.bullets.add(this)
                    self.canShoot = False

            #Escape escapes. neat.
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.done = True
            
            #0 lives kills you
            if(self.lives < 0):
                self.done = True

            #Reset enemies
            #After a round is finished, and the hero steps on StartRound, reset map will become true. This creates enemies again with a +1 in difficulty!
            if(self.resetMap == True):
                self.difficulty += 1
                for i in range(0, 10):
                    for j in range (0, 10):
                        enemy = BasicEnemy(self)
                        enemy.rect.x = j * 60
                        enemy.rect.y = i * 40
                        self.enemies.add(enemy)
                self.resetMap = False

            #Movement for enemies, and shooting for enemies
            #Checks all enemies. If one gets too close to the wall, they drop down, and change direction.
            for badGuy in self.enemies:
                if(badGuy.rect.x > 760):
                    self.doIChange = True
                if(badGuy.rect.x < 0):
                    self.doIChange = True

                #This is a random algorithm. The red laser bullets increase exponentially, while the blue circles
                #decrease linearly. The graphs intersect at around 4.4. This means that at round 4, there are more blues than reds.
                #However, at round 5 there are more reds than blue.
                if(random.randint(0, round(200 * self.difficulty + 750)) == round(200 * self.difficulty) + 750):
                    bulletType = 1
                    theThis = EnemyBullet(self, badGuy, bulletType)
                    self.enemyBullets.add(theThis)
                if(random.randint(0, round(20000/(self.difficulty ** 1.5))) == round(20000/(self.difficulty ** 1.5))):
                    bulletType = 2
                    theThis = EnemyBullet(self, badGuy, bulletType)
                    self.enemyBullets.add(theThis)

            #Board will need to be reset. First. give an upgrade. Once upgrade is choosen, player moves back to original spot, and starts next round
            if(len(self.enemies) == 0 and self.chooseUpgrade == False):
                for i in range (0, 3):
                    myUpgrade = Upgrades(self, i)
                    self.upgrades.add(myUpgrade)
            
            #Upgrade is chosen, player should move back
            if(self.chooseUpgrade == True):
                thisStart = StartRoundButton(self)
                self.starting.add(thisStart)
                


            self.enemies.update(self, self.doIChange)
            self.enemyBullets.update(self, self.hero)

            #Movement for bullets
            self.bullets.update(self, self.enemies)
            self.hero.update(self, self.upgrades)

            #STAAAAAARS
            if(random.randint(0, 7) == 7):
                thisStar = Stars()
                self.stars.add(thisStar)
            self.stars.update(self)

            #Update overlay
            self.overlay.update(self, self.score, self.lives)

            #Creating the screen
            self.screen.fill((0, 0, 0))
            self.stars.draw(self.screen)
            self.enemies.draw(self.screen)
            self.enemyBullets.draw(self.screen)
            self.hero.draw(self.screen)
            self.bullets.draw(self.screen)
            self.upgrades.draw(self.screen)
            self.starting.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.timeForShoot += self.clock.tick(60)
            if(self.canShoot == True):
                self.timeForShoot = 0
            if(self.timeForShoot > self.heroAttackSpeed):
                self.canShoot = True
            

if __name__ == "__main__":
    game = Game()
    game.run()
