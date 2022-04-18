import numpy as np
import pandas as pd
import scipy.linalg as la
from numpy.linalg import matrix_power
import matplotlib.pyplot as plt
import heapq
import sys
import random
import math

np.random.seed(0)
number_of_charger = 10
number_of_car = number_of_charger*5
charger_xcoord = np.random.randint(0,100,number_of_charger)
charger_ycoord = np.random.randint(0,100,number_of_charger)

def map_init():
    coord = np.zeros((100,100))
    i = 0
    while(i< number_of_charger): #coorddinates of EVCEIS =1 else =0
        coord[charger_xcoord[i],charger_ycoord[i]] = 1
        i += 1

def charging_time_type(type): #estimated time required for charging
    if(type == 'quick'):
        return 60
    if(type == 'medium'):
        return 120
    if(type == 'standard'):
        return 240

class car():
    def __init__(self, ID):
        self.ID = ID
        self.start_time_record = []
        self.preference_record = []

    def set_start_time(self, start_time):
        self.start_time = start_time
        self.start_time_record.append(start_time)

    # setter for preference
    def set_preference(self, preference):
        self.preference = preference
        self.preference_record.append(preference)

    def __lt__(self, other):
        return self.ID < other.ID

    def retrieve_start_time_and_preference(self, day): #initialization
        self.start = self.start_time_record[day - 1]
        self.preference = self.preference_record[day - 1].copy()
        self.is_start = False
        self.next_event_time = self.start_time
        self.next_event_type = "Start"
        self.is_departed = False


class charger:
    def __init__(self, ID, type):
        self.idle = True
        self.ID = ID
        self.type = type
        self.charging_time = charging_time_type()
        self.serving = -1
        self.next_event_time = 0
        self.charger_queue = []

    def set_busy(self, cID, charging_time):
        if self.idle: #(有位)
            self.idle = False
            self.serving = cID
            self.next_event_time = charging_time + self.charging_time
        else: #(無位)
            self.charger_queue.append((cID, charging_time))

    def set_next(self):
        waiting_time = len(self.charger_queue) * self.charging_time

        if len(self.charger_queue) > 0: #有人排隊
            item = self.charger_queue.pop(0)
            self.serving = item[0]#第一個去充電
            self.next_event_time = self.next_event_time + self.charging_time #next_event_time =>下一次queue move嘅時間
            self.idle = False
            return waiting_time

        self.idle = True #無人排隊/available
        self.serving = -1
        return waiting_time

    def enqueue_car(self, cID, charging_time):
        self.charger_queue.append((cID, charging_time))


    def reset(self):
        self.idle = True
        self.next_event_time = 0
        self.serving = -1
        self.charger_queue = []

def traveling_time(location1, location2, n):
    x = (abs(math.floor(location1 + 1)/2 - math.floor(location2+1)/2))
    return int("{:.0f}".format(x))

def change_to_time_format(value):
    i = 0
    hr = 0
    mins = value %60
    value1 = value
    while(i<1440):
        value1 = value1 - 60
        if value1 <= 0 :
            break
        else:
            hr = hr + 1
        i = i +1
    hr = 11+ hr
    return str(hr)+":"+str("{:0>2d}".format(mins))

def initialization(car_list, charger_list, current_day):

    for tmp_car in car_list:
        tmp_car.retrieve_start_time_and_preference(current_day)

    for tmp_charger in charger_list:
        tmp_charger.reset()

    return car_list, charger_list

def timing_routine(car_list, charger_list, current_time, termination_time, total_charger):

    # time of next event can depend on arrival
    min_car_time = termination_time * 100
    for tmp_car in car_list:
        min_car_time = min(min_car_time, tmp_car.next_event_time)

    # time of next event can depend on charger
    min_charger_time = termination_time * 100
    for tmp_charger in charger_list:
        if not tmp_charger.idle:
            min_charger_time = min(min_charger_time, tmp_charger.next_event_time)


    # advance to the time
    current_time = min(min_car_time, min_charger_time)

    return current_time

def call_event(car_list, charger_list, current_day, current_time, termination_time, total_charger, simulation_log):

    for tmp_car in car_list:#update event of car
        if tmp_car.next_event_time == current_time:
            if tmp_car.next_event_type == "start":
                datum = {"Day": current_day, "Time": change_to_time_format(current_time),
                         "Event": "car " + str(tmp_car.ID + 1) + " starts traveling", "len(Queue)": "NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                tmp_car.next_event_time = current_time + traveling_time()
                tmp_car.next_event_type = "arrive"
            elif tmp_car.next_event_type == "arrive":
                target_charger = tmp_car.preference.pop(0)
                datum = {"Day": current_day, "Time": change_to_time_format(current_time),
                         "Event": "car " + str(tmp_car.ID + 1) + " arrives at charger " + str(target_charger + 1),
                         "len(Queue)": str(len(charger_list[target_charger].charger_queue) + 1)}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                charger_list[target_charger].enqueue_car(tmp_car.ID, current_time)
                tmp_car.next_event_time = termination_time * 100
                tmp_car.next_event_type = "waiting"
            elif tmp_car.next_event_type == "waiting":
                tmp_car.next_event_time = termination_time * 100
            elif tmp_car.next_event_type == "finish":
                datum = {"Day": current_day, "Time": change_to_time_format(current_time),
                         "Event": "car " + str(tmp_car.ID + 1) + " finish traveling", "len(Queue)": "NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                tmp_car.next_event_time = termination_time * 100
                tmp_car.is_departed = True

    # charger events
    for tmp_charger in charger_list:
        if tmp_charger.idle and len(tmp_charger.charger_queue) > 0: #無人serve緊同有人排緊隊
            tmp_charger.next_event_time = current_time #下一位
            tmp_charger.set_next() #下一位


        elif not tmp_charger.idle and tmp_charger.next_event_time == current_time:#serve完一個人
            datum = {"Day": current_day, "Time": change_to_time_format(current_time),
                     "Event": "car " + str(tmp_charger.serving + 1) + " departs at charger " + str(tmp_charger.ID + 1),
                     "len(Queue)": str(len(tmp_charger.charger_queue))}
            simulation_log = simulation_log.append(datum, ignore_index=True)
            car_list[tmp_charger.serving].next_event_type = "finish"
            car_list[tmp_charger.serving].next_event_time = current_time

    return car_list, charger_list, simulation_log

def output_car(car_list, car_file, D):
    header_list = ["car_id"]
    for i in np.arange(D):
        header_list.append("arrival_time_day_"+str(i+1))
    for i in np.arange(D):
        header_list.append("preference_day_"+str(i+1))
    record_car = pd.DataFrame([], columns = header_list)

    for tmp_car in car_list:
        car_dict = {"car_id":tmp_car.ID+1}

        for i in np.arange(D):
            car_dict["arrival_time_day_"+str(i+1)] = change_to_time_format(tmp_car.arrival_time_record[i])
            car_dict["preference_day_"+str(i+1)] = str([x+1 for x in tmp_car.preference_record[i]])

        record_car = record_car.append(car_dict, ignore_index=True)

    record_car.to_csv(car_file, index = False)

# output config to a csv file
def output_config(D, n, N, charger_charging_time, config_file, car_file, log_file, summary_file):

    header_list = ["ColA", "ColB"]
    record_config = pd.DataFrame([], columns = header_list)

    record_config = record_config.append({"ColA":"D","ColB":str(D)}, ignore_index=True)
    record_config = record_config.append({"ColA":"n","ColB":str(n)}, ignore_index=True)
    record_config = record_config.append({"ColA":"N","ColB":str(N)}, ignore_index=True)
    record_config = record_config.append({"ColA":"charger_charging_time","ColB":str(charger_charging_time)}, ignore_index=True)
    record_config = record_config.append({"ColA":"car_file","ColB":str(car_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Log_file","ColB":str(log_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Summary_file","ColB":str(summary_file)}, ignore_index=True)

    record_config.to_csv(config_file, index = False, header = False)


# main program
curr_time = 0
isFileInput = False
car_list = []

if len(sys.argv) == 2:
    # initialization with a config file

    isFileInput = True
    config = pd.read_csv(sys.argv[1], header=None, index_col=0, skip_blank_lines=True)
    print(config)

    D = int(config[1].D)
    n = int(config[1].n)
    N = int(config[1].N)
    charger_charging_time = list(map(int, config[1].charger_charging_time.split("[")[1].split("]")[0].split(",")))
    car_file = config[1].car_file
    log_file = config[1].Log_file
    summary_file = config[1].Summary_file

    car_df = pd.read_csv(car_file, header=0, skip_blank_lines=True)

    # retrive the data from car_df(dataframe) to car_list(list of car objects)
    # pay attention: all numbers in the dataframe are 1-based, you need to change them back to 0-based
    for ind, row in car_df.iterrows():
        tmp_car = car(row["car_id"]-1)
        for d in np.arange(D):
            s = row["arrival_time_day_"+str(d+1)].split(":")
            tmp_car.set_arrival_time((int(s[0])-11)*60+int(s[1]))
            one_base_list = list(map(int, row["preference_day_"+str(d+1)].split("[")[1].split("]")[0].split(",")))
            tmp_car.set_preference([x-1 for x in one_base_list])
        car_list.append(tmp_car)


else:
    # initialization with random numbers

    D = 2
    n = number_of_charger
    N = number_of_car
    charger_charging_time = []
    config_file = "config_default_random.csv"
    car_file = "car_default_random.csv"
    log_file = "simulation_log.csv"
    summary_file = "simulation_summary.csv"

    # generate DN arrival time for the cars
    np.random.seed(0)
    cid = 0
    while cid < N:
        tmp_car = car(cid)
        i = 0
        while i < D:
            tmp_car.set_start_time(int(np.random.uniform(20)))
            i = i + 1
        car_list.append(tmp_car)
        cid = cid + 1

    # generate DN list of distinct integers as the preference of the cars
    np.random.seed(1)
    random.seed(1)
    for tmp_car in car_list:
        i = 0
        while i < D:
            p = min(int(np.random.uniform(5)+1), n)
            preference = random.sample(range(0,n), p)
            tmp_car.set_preference(preference)
            i = i + 1

    # generate n numbers as the charging time of the chargers
    np.random.seed(2)
    i = 0
    while i < n:
        charger_charging_time.append(int(min(1+np.random.exponential(5), 10)))
        i = i + 1




# main simulation
# initialization before simulation
termination_time = 420
current_day = 1
charger_list = []
bid = 0
debug = False
# create the list of charger objects
for charging_time in charger_charging_time:
    new_charger = charger(bid, charging_time)
    charger_list.append(new_charger)
    bid = bid + 1

simulation_log = pd.DataFrame([], columns = ["Day", "Time", "Event", "len(Queue)"])
simulation_summary = pd.DataFrame([], columns = ["Day", "TotalWaitingTime", "TotalTravelingTime", "TotalTourTime"])

while current_day <= D:

    # initialization for a day in the simulation
    car_list, charger_list = initialization(car_list, charger_list, current_day)
    current_time = 0
    is_system_clear = True
    total_waiting_time = 0
    total_traveling_time = 0
    total_tour_time = 0


    while current_time < termination_time or not is_system_clear:

        if debug:
            print(current_time)

        # determine the time
        current_time = timing_routine(car_list, charger_list, current_time, termination_time, n)

        # update different lists and log sheet
        car_list, charger_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time = call_event(car_list, charger_list, current_day, current_time, termination_time, n, simulation_log)

        # check if Art Fair clear
        is_system_clear = True
        for tmp_car in car_list:
            if not tmp_car.is_departed:
                is_system_clear = False

        if current_time > termination_time:
            for tmp_car in car_list:
                if tmp_car.next_event_type == "waiting":
                    tmp_car.preference = []


    # at the end of each day, append a row of statistics to the summary file
    datum = {"Day":current_day, "TotalWaitingTime":total_waiting_time, "TotalTravelingTime":total_traveling_time, "TotalTourTime":total_tour_time}
    simulation_summary = simulation_summary.append(datum, ignore_index=True)
    current_day = current_day + 1

# output statistics
if not isFileInput:
    # output car record to car_file
    output_car(car_list, car_file, D)
    # output config file to config_file
    output_config(D, n, N, charger_charging_time, config_file, car_file, log_file, summary_file)


simulation_log.to_csv(log_file, index = False)
simulation_summary.to_csv(summary_file, index = False)