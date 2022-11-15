import AsteroidUniverse

#Run the set up screen
game = AsteroidUniverse.AsteroidUniverse()
#Restart the board if the restart button was pressed
while game.Run() == True:
    game = AsteroidUniverse.AsteroidUniverse()