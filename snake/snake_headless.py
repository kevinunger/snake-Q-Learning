import pygame, sys, time, random
import numpy as np
from time import sleep

#Headless version for training that disables fps limit and graphics

screenSize = {'x': 500,'y':500}
FPS = 100
direction = 'RIGHT'
change_to = direction
colors = {
    'black': pygame.Color(0, 0, 0), 
    'white': pygame.Color(255, 255, 255), 
    'red': pygame.Color(255, 0, 0), 
    'green':pygame.Color(0, 255, 0), 
    'darkGreen':pygame.Color(50, 200, 50), 
    'blue': pygame.Color(0, 0, 255)
}


init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10 
init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10
snake_pos = [init_pos_x, init_pos_y]
snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
#food_pos = [20,30]

score = 0
food_spawn = True


def newGame():
    global snake_pos, food_pos, score, food_spawn, snake_body

    init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10 
    init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10

    snake_pos = [init_pos_x, init_pos_y]
    snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
    food_spawn = True

    score = 0

def main(emulate, onGameOver, onScore):
    # Checks for errors encountered
    check_errors = pygame.init()
    # pygame.init() example output -> (6, 0)
    # second number in tuple gives number of errors
    if check_errors[1] > 0:
        #print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
        sys.exit(-1)
    else:
        #print('[+] Game successfully initialised')
        pass


    mainGame(emulate, onGameOver, onScore)


moveCounter = 0
moves = []
moveSinceScore = 0

def mainGame(emulate, onGameOver, onScore):
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to

    moveCounter = 0
    while True:
            
        #calc diff between food and snake head
        diff = [snake_pos[0]-food_pos[0], snake_pos[1] - food_pos[1]]
        diff = abs(diff[0] + diff[1])
        
        #params that get converted to state (not all of them)
        params = {
            'food_pos': food_pos, 
            'snake_pos': snake_pos,
            'snake_body': snake_body,
            'score': score,
            'diff':diff,
            'screenSizeX': screenSize['x'],
            'screenSizeY': screenSize['y'],
            'moveSinceScore': moveSinceScore
            }

        ######## emulate keyPresses ##########
        #call emulate function in qlearning.py, returns direction
        choosenDirection = emulate(params)

        if choosenDirection == 'U':
            change_to = 'UP'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'D':
            change_to = 'DOWN'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'L':
            change_to = 'LEFT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'R':
            change_to = 'RIGHT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1


        # Making sure the snake cannot move in the opposite direction instantaneously
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Moving the snake
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))

        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            moveSinceScore = 0
            onScore(params)
            food_spawn = False
        else:
            snake_body.pop()

        # Spawning food on the screen
        if not food_spawn:
            food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
            for x in snake_body:    #when food spawns in snake body --> new position
                while (food_pos  == x):
                    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

        food_spawn = True


       

        # Game Over conditions
        # Getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)


        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, screenSize, onGameOver)
                
# Game Over
def game_over(emulate, colors, score, screenSize, onGameOver):
    global moves, moveCounter
    moveCounter = 0
    onGameOver(score, moves)

    newGame()
