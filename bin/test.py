import numpy as np
import math
#generate stations EVCEI
station = [[1,10],[-55,-8],[99,99],[28,-50],[35,35],[77,-4],[-24,66],[-14,-59]]
#generate where they start
cars_start = [[20,10],[-58,-92],[-7,25],[-28,-0],[-64,25],[1,-24],[-23,66],[-94,-95],[50,-12],[-9,-14],[-1,22],[-9,22],[3,-16],[12,-22],[-4,-16],[4,1],[20,100],[-78,-2],[-20,95],[67,-80],[-42,41],[1,-54],[10,1],[-5,16]]
#generate their destinations
cars_dest = [[27,-25],[-5,-92],[-57,52],[-50,-0],[-6,42],[25,-84],[-82,-81],[-4,-50],[52,-83],[-5,0],[-22,22],[-1,1],[3,-1],[0,0],[3,6],[9,15],[-18,-33],[-69,88],[99,-1],[-6,-16],[43,78],[-4,-10],[-70,68],[23,22]]

def distance_cal(station,cars_dest,i,j):
    return math.sqrt(((cars_dest[i][0]-station[j][0]))*(cars_dest[i][0]-station[j][0])+((cars_dest[i][1]-station[j][1])*(cars_dest[i][1]-station[j][1])))

def waiting_time(station_queue):
    i = 0
    j = 0
    totaltime = 0
    while(j<len(station)):
        if (station_queue[j][1] != 0):
            totaltime = totaltime + (station_queue[j][1])*(station_queue[j][1]-1)
        j = j + 1
    j = 0
    print(totaltime)
    return totaltime/len(cars_dest)


distance = np.zeros((len(cars_dest),len(station)))
min_dest = np.zeros(((len(cars_dest), 2)))
station_queue = np.zeros((len(station),2))
i = 0
j = 0
min = 99999
while(i<len(cars_dest)):
    while(j<len(station)):
        distance[i][j] = (distance_cal(station,cars_dest,i,j))
        if (min > (distance_cal(station,cars_dest,i,j))):
            min = (distance_cal(station,cars_dest,i,j))
            min_dest[i][0] = i
            min_dest[i][1] = j
        j = j + 1
    j = 0
    i = i + 1
    print(min)
    min = 99999

i = 0
j = 0
while(i< len(cars_dest)):
    while(j< len(station)):
        station_queue[j][0] = j
        if(min_dest[i][1] == j):
            station_queue[j][1] = station_queue[j][1] + 1
        j = j + 1
    j = 0
    i = i + 1
print(distance)
print(min_dest)
print(station_queue)
print(waiting_time(station_queue))
