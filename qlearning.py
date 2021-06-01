import numpy as np
import sys
from collections import defaultdict
import pickle
from time import sleep, time

if sys.argv[1] == "p":
    mode = "play"
if sys.argv[1] == "t":
    mode = "train"

if mode == "play":
    import snake
else:
    import snake_headless

rewardAlive = -1
rewardKill =  -10000
rewardScore = 50000000

alpha = 0.1
alphaD = 1
#alpha --> learning rate
#alphaD --> decay factor of the learning rate

gamma = 0.9
#discount factor

if mode == "play":
    e = 0.0001
    ed = 1
    emin = 0.0001
else:
    e = 0.9
    ed = 1.3
    emin = 0.0001

#e --> randomness
#ed --> decay factor of e



try:
    with open("Q\Q.pickle", "rb") as file:
        Q = defaultdict(lambda: [0,0,0,0], pickle.load(file))
except:
    Q = defaultdict(lambda: [0,0,0,0])  #(UP,LEFT,DOWN,RIGHT)

lastMoves = ""
def paramsToState(params):
    #{'food_pos': [150, 130], 'snake_pos': [230, 50], 'snake_body': [[230, 50], [220, 50], [210, 50]], 'score': 0, ....}
    global lastMoves

    ################# relativeFoodPosition (where is the food relative to the body) ###################
    relativeFoodPostion = [0,0,0,0,0,0]
        
    if (params["food_pos"][0] - params["snake_pos"][0]) > 0:        #foodRight
        relativeFoodPostion[0] = 1
    if (params["food_pos"][0] - params["snake_pos"][0]) < 0 :       #foodLeft
        relativeFoodPostion[1] = 1
    if ((params["food_pos"][0] - params["snake_pos"][0]) == 0):     #foodXMiddle
        relativeFoodPostion[2] = 1

    if (params["food_pos"][1] - params["snake_pos"][1]) > 0:        #foodDown
        relativeFoodPostion[3] = 1
    if (params["food_pos"][1] - params["snake_pos"][1]) < 0 :       #foodTop
       relativeFoodPostion[4] = 1
    if ((params["food_pos"][1] - params["snake_pos"][1]) == 0):     #foodYMiddle
        relativeFoodPostion[5] = 1

    rFP = ""                        #als String concatenated
    for x in relativeFoodPostion:
        rFP += str(x)

    ################# ScreenDanger (at the edge of the screen?) ###################

    screenDanger = [0,0,0,0]
    if(params["screenSizeX"] - params["snake_pos"][0] == 10):                               #dangerRight
        screenDanger[0] = 1
    if(params["screenSizeX"] - params["snake_pos"][0] == params["screenSizeX"]):            #dangerLeft
        screenDanger[1] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == 10):                               #dangerBottom
        screenDanger[2] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == params["screenSizeY"]):            #dangerTop
        screenDanger[3] = 1

    sD = ""                        #als String concatenated
    for x in screenDanger:
        sD += str(x)

    ################# Danger Body (is body reachable to bite?) ###################

    snake_body = []
    skip = 0
    for pos in params["snake_body"]:                # ignore the first 4 body parts
        if (skip > 3):
             snake_body.append(pos)
        skip+=1
    
    bodyDanger = [0,0,0,0]
    for bodyPart in snake_body:
        #print(bodyPart)
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == 10 ):  #BodyPartUp
            bodyDanger[0] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == -10 ): #BodypartDown
            bodyDanger[1] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 10 and params["snake_pos"][1] - bodyPart[1] == 0 ):  #BodyPartLeft
            bodyDanger[2] = 1
        if(params["snake_pos"][0] - bodyPart[0] == -10 and params["snake_pos"][1] - bodyPart[1] == 0 ): #BodypartRight
            bodyDanger[3] = 1
            

    bD = ""                        #as String concatenated
    for x in bodyDanger:
        bD += str(x)

    direction = ""
    dx = params["snake_body"][1][0] - params["snake_body"][0][0]
    dy = params["snake_body"][1][1] - params["snake_body"][0][1]

    if dx == -10 and dy == 0:
        #Moving right
        direction="0"
    if dx == 10 and dy == 0:
        #Moving left
        direction="1"
    if dx == 0 and dy == 10:
        #Moving up
        direction="2"
    if dx == 0 and dy == -10:
        #Moving down
        direction="3"


    #state = xxxxxx_xxxx_xxxx_xx
    #state contains where the food is relative to the snake, if a screen edge is near, if a body part is near and the direction the snake took

    state = rFP + "_" + sD + "_" + bD + "_" + direction
    return state

oldState = None
oldAction = None
gameCounter = 0
gameScores = []

def emulate(params):
    global oldState
    global oldAction

    state = paramsToState(params)
    estReward = Q[state]

    prevReward = Q[oldState]

    index = 0
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3
    

    #reward more negative, when taking many moves; reset, when food is eaten
    reward = (0 -params["moveSinceScore"]) / 50

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (reward + gamma * max(estReward) )

    Q[oldState] = prevReward

    oldState = state
    basedOnQ = np.random.choice([True, False], p=[1-e,e])

    #basedOnQ --> choice based on Q-table
    #basedOnQ == false --> random choice based on e (decreases over time with ed)

    if basedOnQ == False:
        choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
        oldAction = choice
        return choice
    else:
        if estReward[0] > estReward[1] and estReward[0] > estReward[2] and estReward[0] > estReward[3]:
            oldAction = 'U'
            return 'U'
        if estReward[1] > estReward[0] and estReward[1] > estReward[2] and estReward[1] > estReward[3]:
            oldAction = 'L'
            return 'L'
        if estReward[2] > estReward[0] and estReward[2] > estReward[1] and estReward[2] > estReward[3]:
            oldAction = 'D'
            return 'D'
        if estReward[3] > estReward[0] and estReward[3] > estReward[1] and estReward[3] > estReward[2]:
            oldAction = 'R'
            return 'R'
        else:
            choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
            oldAction = choice
            return choice
        

gameCounter = []
gameCounter = 0
start = 0 
end = 0

    
def onGameOver(score, moves):
    global oldState
    global oldAction
    global gameCounter
    global alpha, e, ed
    global start, end



    gameScores.append(score)

    #update Q of previous state (state which lead to gameOver)
    prevReward = Q[oldState]

    if oldAction == None:
        index = 0
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                        alpha * rewardKill

    Q[oldState] = prevReward

    oldState = None
    oldAction = None

    #save Q as pickle
    if gameCounter % 200 == 0:
        with open("Q/" + "Q" + ".pickle","wb" ) as file:
            pickle.dump(dict(Q), file)
        print("+++++++++ Pickle saved +++++++++")

    #show some stats
    if gameCounter % 100 == 1:
        end = time()
        timeD = end - start
        print (str(gameCounter)+ " : " + "\t" + 'meanScore: ' +  str(np.mean(gameScores[-100:])) + "| HighScore: " + str(np.max(gameScores)) + \
              '| moves: ' + str(np.mean(moves[-100:])) + "| time for 10 games: " + str(round(timeD*10)/100))
        start = time()

    #print hyperparameters
    if gameCounter % 100 == 0:
        print ("a:", alpha)
        print ("e:", e)
        print ("g:", gamma)

    #decrease alpha / e over time (moves)
    if gameCounter % 100 == 0:
        alpha = alpha * alphaD
        if e > emin:
            e = e / ed

    gameCounter += 1



def onScore(params):
    global oldState
    global oldAction
    global gameCounter

    state = paramsToState(params)

    estReward = Q[state]

    prevReward = Q[oldState]

    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (rewardScore + gamma * max(estReward) )

    Q[oldState] = prevReward



if mode == "play":
    snake.main(emulate, onGameOver, onScore)
else:
    snake_headless.main(emulate, onGameOver, onScore)

