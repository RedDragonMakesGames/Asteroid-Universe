import pygame
from pygame.locals import *
import random
import math
import sys

#Defines
XSPACING = 20
YSPACING = 20
TOPBAR = 100
XSIZE = 500
YSIZE = 500
SHIPSPEEDINCREASE = 0.1
MAXSPEED = 6
BULLETCOOLDOWN = 20
BULLETLIFETIME = 60
CANHITSHIPTIME = 5          #Time after which the bullet has cleared the ship, and can hit it on a loop
BULLETSPEED = (0,-8)
BIGASTEROIDSPEED = (0,-1)
LITTLEASTEROIDSPEED = (0,-2)
NOOFASTEROIDSTOSPLITINTO = 3
SPINRATE = 2

UNIVERSES = ["Donut", "Folded", "Double Folded"]
universeType = "Donut"

#Helper functions
def CheckTounching(pos1, pos2, size):
    if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
        return True
    else:
        return False

def HandleEdges(pos, rot):
    if universeType == "Donut":
        pos, rot = HandleDonutEdges(pos, rot)
    elif universeType == "Folded":
        pos, rot = HandleFoldedEdges(pos, rot)
    elif universeType == "Double Folded":
        pos, rot = HandleDoubleFoldedEdges(pos, rot)
    
    return pos, rot

def HandleDonutEdges(pos, rot):
    if pos[0] < XSPACING:
        pos = pos[0] + XSIZE, pos[1]
    elif pos[0] > XSIZE + XSPACING:
        pos = pos[0] - XSIZE, pos[1]
    if pos[1] < YSPACING + TOPBAR:
        pos = pos[0], pos[1] + YSIZE
    elif pos[1] > YSIZE + YSPACING + TOPBAR:
        pos = pos[0], pos[1] - YSIZE
    return pos, rot

def HandleDoubleFoldedEdges(pos, rot):
    if pos[0] < XSPACING:
        pos = pos[0], (YSIZE - (pos[1] - YSPACING - TOPBAR)) + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,0))
    elif pos[0] > XSIZE + XSPACING:
        pos = pos[0], (YSIZE - (pos[1] - YSPACING - TOPBAR)) + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,0))
    if pos[1] < YSPACING + TOPBAR:
        pos = (XSIZE - (pos[0] - XSPACING)) + XSPACING, pos[1]
        rot = rot.reflect(pygame.Vector2(0,1))
    elif pos[1] > YSIZE + YSPACING + TOPBAR:
        pos = (XSIZE - (pos[0] - XSPACING)) + XSPACING, pos[1]
        rot = rot.reflect(pygame.Vector2(0,1))
    return pos, rot

def HandleFoldedEdges(pos, rot):
    if pos[0] < XSPACING:
        pos = pos[1] - YSPACING -TOPBAR + XSPACING, pos[0] - XSPACING + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,1))
    elif pos[0] > XSIZE + XSPACING:
        pos = pos[1] - YSPACING -TOPBAR + XSPACING, pos[0] - XSPACING + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,1))
    elif pos[1] < YSPACING + TOPBAR:
        pos = pos[1] - YSPACING -TOPBAR + XSPACING, pos[0] - XSPACING + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,1))
    elif pos[1] > YSIZE + YSPACING + TOPBAR:
        pos = pos[1] - YSPACING -TOPBAR + XSPACING, pos[0] - XSPACING + YSPACING + TOPBAR
        rot = rot.reflect(pygame.Vector2(1,1))
    return pos, rot

class Bullet:
    def __init__(self, pos, rotation):
        self.pos = pos
        self.rotation = rotation
        self.momentum = pygame.Vector2(BULLETSPEED).rotate(rotation)
        self.lifetime = BULLETLIFETIME
    
    def Tick(self):
        self.lifetime -= 1
        if self.lifetime < 0:
            return True
        self.pos = (self.pos[0] + self.momentum[0], self.pos[1] + self.momentum[1])
        self.pos, self.momentum = HandleEdges(self.pos, self.momentum)

class Asteroid:
    def __init__(self, pos, isBig):
        self.pos = pos
        self.isBig = isBig
        self.rotation = random.randint(0, 359)
        if isBig:
            self.momentum = pygame.Vector2(BIGASTEROIDSPEED).rotate(self.rotation)
        else:
            self.momentum = pygame.Vector2(LITTLEASTEROIDSPEED).rotate(self.rotation)
        
    def Tick(self):
        self.pos = (self.pos[0] + self.momentum[0], self.pos[1] + self.momentum[1])
        self.pos, self.momentum = HandleEdges(self.pos, self.momentum)     

class AsteroidUniverse:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Asteroid Universe")

        self.clock = pygame.time.Clock()

        #Load assets
        self.ship = pygame.image.load('Assets/ship.png')
        self.bullet = pygame.image.load('Assets/bullet.png')
        self.smallAsteroid = pygame.image.load('Assets/asteroidSmall.png')
        self.bigAsteroid = pygame.image.load('Assets/asteroidBig.png')
        self.retry = pygame.image.load('Assets/retry.png')

        self.screen = pygame.display.set_mode((XSIZE + 2 * XSPACING, YSIZE + 2 * YSPACING + TOPBAR))

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((150,150,150))

        self.playAreaBackground = pygame.Surface((XSIZE,YSIZE))
        self.playAreaBackground = self.playAreaBackground.convert()
        self.playAreaBackground.fill((255,255,255))

        self.shipPos = (XSIZE/2 + XSPACING, YSIZE/2 + YSPACING + TOPBAR)
        self.shipRotation = 0
        self.shipMomentum = (0,0)

        self.bulletCooldown = 0
        self.bullets = []

        self.universe = 0
        global universeType
        universeType = "Donut"

        self.asteroids = []

        if pygame.font:
            self.font = pygame.font.Font(None, 32)

        self.score = 0
        self.lost = False

    def Run(self):
        self.finished = False

        while not self.finished:
            #Handle input
            self.HandleInput()

            #Draw screen
            self.Draw()

            self.clock.tick(60)

            if not self.lost:
                if self.bulletCooldown > 0:
                    self.bulletCooldown -= 1
                for b in self.bullets:
                    if b.Tick() == True:
                        self.bullets.remove(b)
                for a in self.asteroids:
                    a.Tick()

                self.CheckCollision()

                if len(self.asteroids) == 0:
                    self.SpawnAsteroids()
        
        pygame.quit()
        return True

    def HandleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if self.lost == True:
                    pos = pygame.mouse.get_pos()
                    if CheckTounching(pos, (self.screen.get_size()[0] - self.retry.get_size()[0] - XSPACING, 3 * YSPACING), self.retry.get_size()):
                        self.finished = True
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    self.universe += 1
                    if self.universe > len(UNIVERSES) - 1:
                        self.universe = 0
                    global universeType
                    universeType = UNIVERSES[self.universe]

        if self.lost:
            return

        if pygame.key.get_pressed()[K_LEFT]:
            self.TurnShipLeft()

        if pygame.key.get_pressed()[K_RIGHT]:
            self.TurnShipRight()

        if pygame.key.get_pressed()[K_UP]:
            self.IncreaseShipSpeed()

        if pygame.key.get_pressed()[K_DOWN]:
            self.DecreaseShipSpeed()
        
        if pygame.key.get_pressed()[K_SPACE]:
            self.FireBullet()

        self.CalculateShipPosition()
    
    def TurnShipLeft(self):
        self.shipRotation -= SPINRATE
        if self.shipRotation < 0:
            self.shipRotation = 359

    def TurnShipRight(self):
        self.shipRotation += SPINRATE
        if self.shipRotation > 359:
            self.shipRotation = 0

    def IncreaseShipSpeed(self):
        speedchangeVector = pygame.math.Vector2(0, -SHIPSPEEDINCREASE)
        rotatedMovement = speedchangeVector.rotate(self.shipRotation)
        newX = self.shipMomentum[0] + rotatedMovement[0]
        newY = self.shipMomentum[1] + rotatedMovement[1]
        if (pygame.math.Vector2.magnitude(pygame.math.Vector2(newX,newY)) < MAXSPEED):
            self.shipMomentum = (newX, newY)

    def DecreaseShipSpeed(self):
        speedchangeVector = pygame.math.Vector2(0, SHIPSPEEDINCREASE)
        rotatedMovement = speedchangeVector.rotate(self.shipRotation)
        newX = self.shipMomentum[0] + rotatedMovement[0]
        newY = self.shipMomentum[1] + rotatedMovement[1]
        #Do not allow the ship to reverse, only stop
        momentumAngle = pygame.math.Vector2.angle_to(pygame.math.Vector2(0,-1), pygame.math.Vector2(newX, newY))
        #Put onto same scale as ship rotation
        if momentumAngle < 0:
            momentumAngle += 360
        differenceAngle = momentumAngle - self.shipRotation
        if (differenceAngle > -90 and differenceAngle < 90):
            self.shipMomentum = (newX, newY)

    def CalculateShipPosition(self):
        self.shipPos = (self.shipPos[0] + self.shipMomentum[0], self.shipPos[1] + self.shipMomentum[1])
        #Handle edges here
        self.shipPos, self.shipMomentum = HandleEdges(self.shipPos, pygame.Vector2(self.shipMomentum))

    def FireBullet(self):
        if self.bulletCooldown > 0:
            return
        self.bulletCooldown = BULLETCOOLDOWN
        self.bullets.append(Bullet(self.shipPos, self.shipRotation))
    
    def CheckCollision(self):
        for a in self.asteroids:
            if a.isBig:
                asteroidOrigin = (self.bigAsteroid.get_size()[0]/2, self.bigAsteroid.get_size()[1]/2)
                adjustedPos = a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]
                if (CheckTounching(self.shipPos, adjustedPos, self.bigAsteroid.get_size())):
                    self.lost = True
            else:
                asteroidOrigin = (self.smallAsteroid.get_size()[0]/2, self.smallAsteroid.get_size()[1]/2)
                adjustedPos = a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]
                if (CheckTounching(self.shipPos, adjustedPos, self.smallAsteroid.get_size())):
                    self.lost = True 
        for b in self.bullets:
            if b.lifetime < BULLETLIFETIME - CANHITSHIPTIME:
                if (CheckTounching(b.pos, self.shipPos, self.ship.get_size())):
                    self.lost = True
            for a in self.asteroids:
                if a.isBig:
                    asteroidOrigin = (self.bigAsteroid.get_size()[0]/2, self.bigAsteroid.get_size()[1]/2)
                    adjustedPos = a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]
                    if (CheckTounching(b.pos, adjustedPos, self.bigAsteroid.get_size())):
                        if b in self.bullets:
                            self.bullets.remove(b)
                            self.SplitAsteroid(a.pos)
                            self.asteroids.remove(a)
                            self.score += 10
                else:
                    asteroidOrigin = (self.smallAsteroid.get_size()[0]/2, self.smallAsteroid.get_size()[1]/2)
                    adjustedPos = a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]
                    if (CheckTounching(b.pos, adjustedPos, self.smallAsteroid.get_size())):
                        if b in self.bullets:
                            self.bullets.remove(b)
                            self.asteroids.remove(a)
                            self.score += 20
    
    def SpawnAsteroids(self):
        leftPos = self.shipPos[0] - XSIZE/4
        if leftPos < XSPACING:
            leftPos += XSIZE
        rightPos = self.shipPos[0] + XSIZE/4
        if rightPos > XSPACING + XSIZE:
            rightPos -= XSIZE
        topPos = self.shipPos[1] - YSIZE/4
        if topPos < YSPACING + TOPBAR:
            topPos += YSIZE
        bottomPos = self.shipPos[1] + YSIZE/4
        if bottomPos > YSPACING + XSIZE + TOPBAR:
            bottomPos -= YSIZE
        
        self.asteroids.append(Asteroid((leftPos,topPos), True))
        self.asteroids.append(Asteroid((leftPos,bottomPos), True))
        self.asteroids.append(Asteroid((rightPos,topPos), True))
        self.asteroids.append(Asteroid((rightPos,bottomPos), True))

    def SplitAsteroid(self, pos):
        for i in range(0, NOOFASTEROIDSTOSPLITINTO):
            self.asteroids.append(Asteroid(pos, False))

    def Draw(self):
        #clear screen
        self.screen.blit(self.background, (0,0))

        #draw play area background
        self.screen.blit(self.playAreaBackground, (XSPACING, YSPACING + TOPBAR))

        #Draw ship
        shipOrigin = (self.ship.get_size()[0]/2, self.ship.get_size()[1]/2)
        shipRect = self.ship.get_rect(topleft = (self.shipPos[0] - shipOrigin[0], self.shipPos[1] - shipOrigin[1]))
        offsetCenterToPivot = pygame.math.Vector2(self.shipPos) - shipRect.center
        rotatedOffset = offsetCenterToPivot.rotate(self.shipRotation)
        rotatedImageCenter = (self.shipPos[0] - rotatedOffset.x, self.shipPos[1] - rotatedOffset.y)
        rotatedShip = pygame.transform.rotate(self.ship, -self.shipRotation)
        rotatedImageRect = rotatedShip.get_rect(center = rotatedImageCenter)

        self.screen.blit(rotatedShip, rotatedImageRect)

        #Draw bullets
        for b in self.bullets:
            bulletOrigin = (self.bullet.get_size()[0]/2, self.bullet.get_size()[1]/2)
            bulletRect = self.bullet.get_rect(topleft = (b.pos[0] - bulletOrigin[0], b.pos[1] - bulletOrigin[1]))
            offsetCenterToPivot = pygame.math.Vector2(b.pos) - bulletRect.center
            rotatedOffset = offsetCenterToPivot.rotate(b.rotation)
            rotatedImageCenter = (b.pos[0] - rotatedOffset.x, b.pos[1] - rotatedOffset.y)
            rotatedBullet = pygame.transform.rotate(self.bullet, -b.rotation)
            rotatedImageRect = rotatedBullet.get_rect(center = rotatedImageCenter)

            self.screen.blit(rotatedBullet, rotatedImageRect)
        
        #Draw asteroids
        for a in self.asteroids:
            if a.isBig:
                asteroidOrigin = (self.bigAsteroid.get_size()[0]/2, self.bigAsteroid.get_size()[1]/2)
                asteroidRect = self.bigAsteroid.get_rect(topleft = (a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]))
            else:
                asteroidOrigin = (self.smallAsteroid.get_size()[0]/2, self.smallAsteroid.get_size()[1]/2)
                asteroidRect = self.smallAsteroid.get_rect(topleft = (a.pos[0] - asteroidOrigin[0], a.pos[1] - asteroidOrigin[1]))
            offsetCenterToPivot = pygame.math.Vector2(a.pos) - asteroidRect.center
            rotatedOffset = offsetCenterToPivot.rotate(a.rotation)
            rotatedImageCenter = (a.pos[0] - rotatedOffset.x, a.pos[1] - rotatedOffset.y)
            if a.isBig:
                rotatedAsteroid = pygame.transform.rotate(self.bigAsteroid, -a.rotation)
            else:
                rotatedAsteroid = pygame.transform.rotate(self.smallAsteroid, -a.rotation)
            rotatedImageRect = rotatedAsteroid.get_rect(center = rotatedImageCenter)

            self.screen.blit(rotatedAsteroid, rotatedImageRect)            

        #Draw score
        scoreStr = "Score: " + str(self.score)
        scoreTxt = self.font.render(scoreStr, True, (10,10,10))
        self.screen.blit(scoreTxt, (XSPACING,YSPACING))

        #Draw current universe
        uniString = "Current universe: " + str(UNIVERSES[self.universe])
        uniTxt = self.font.render(uniString, True, (10,10,10))
        self.screen.blit(uniTxt, (XSPACING, 3 * YSPACING))

        if self.lost == True:
            endStr = "You lose!"
            endText = self.font.render(endStr, True, (10,10,10))
            self.screen.blit(endText, (self.screen.get_size()[0] - endText.get_size()[0] - XSPACING, YSPACING))
            self.screen.blit(self.retry, (self.screen.get_size()[0] - self.retry.get_size()[0] - XSPACING, 3 * YSPACING))

        #Refresh the screen
        pygame.display.flip()

#game = AsteroidUniverse()
#game.Run()