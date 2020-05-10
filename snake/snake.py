import pygame, sys, time, random
import numpy as np
from time import sleep

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
game_window = None

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
    global game_window
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


    # Initialise game window
    pygame.display.set_caption('Snake Eater')
    game_window = pygame.display.set_mode((screenSize['x'], screenSize['y']))

    # FPS controller
    fps_controller = pygame.time.Clock()

    mainGame(emulate, fps_controller, onGameOver, onScore)


moveCounter = 0
moves = []
moveSinceScore = 0

def mainGame(emulate, fps_controller, onGameOver, onScore):
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to
    global game_window
    moveCounter = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Whenever a key is pressed down
            elif event.type == pygame.KEYDOWN:
                # W -> Up; S -> Down; A -> Left; D -> Right
                if event.key == pygame.K_UP or event.key == ord('w'):
                    change_to = 'UP'
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    change_to = 'RIGHT'
                # Esc -> Create event to quit the game
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))


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

        # GFX
        game_window.fill(colors['black'])

        #draw snake_body (head is darkGreen)
        for index, pos in enumerate(snake_body):
            if(index > 0):
                pygame.draw.rect(game_window, colors['green'], pygame.Rect(pos[0], pos[1], 10, 10))
            else:
                pygame.draw.rect(game_window, colors['darkGreen'], pygame.Rect(pos[0], pos[1], 10, 10))

        for index, pos in enumerate(snake_body):
            if pos == food_pos:
                pygame.draw.rect(game_window, colors['red'], pygame.Rect(pos[0], pos[1], 10, 10))

        # draw Snake food
        pygame.draw.rect(game_window, colors['red'], pygame.Rect(food_pos[0], food_pos[1], 10, 10))


       

        # Game Over conditions
        # Getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x']-10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y']-10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)


        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, game_window, screenSize, onGameOver)
                

        # Refresh game screen
        pygame.display.update()
        # Refresh rate
        fps_controller.tick(FPS)    

# Game Over
def game_over(emulate, colors, score, game_window, screenSize, onGameOver):
    global moves, moveCounter
    moveCounter = 0
    onGameOver(score, moves)

    game_window.fill(colors['black'])
    pygame.display.flip()

    newGame()
