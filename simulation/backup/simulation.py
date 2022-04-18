import numpy as np
import pandas as pd
import sys
import random
import math

seed = 0
np.random.seed(seed)
random.seed(seed)
usingrate = 100
averagewaitingtime = 0

class Car:
    def __init__(self, ID):
        self.ID = ID
        self.arrival_time_record = []
        self.preference_record = []
        self.destination_record = []
        self.distance_record = []
        self.coordinate_record = []
        self.total_charging_time = []

    def set_arrival_time(self, arrival_time):
        self.arrival_time = arrival_time
        self.arrival_time_record.append(arrival_time)

    def set_destination(self, destination):
        self.destination = destination
        self.destination_record.append(destination)

    def set_coordinate(self, coordinate):
        self.coordinate = coordinate
        self.coordinate_record.append(coordinate)

    def set_preference(self, preference):
        self.preference = preference
        self.preference_record.append(preference)

    def __lt__(self,other):
        return self.ID < other.ID

    def retrieve_arrival_time_and_preference(self, day):
        self.arrival_time = self.arrival_time_record[day-1]
        self.preference = self.preference_record[day-1].copy()
        self.is_arrived = False
        self.next_event_time = self.arrival_time
        self.next_event_type = "arrival"
        self.is_departed = False


class Charger:
    def __init__(self, ID, charging_time, coordinate):
        self.idle = True
        self.ID = ID
        self.charging_time = charging_time
        self.coordinate = coordinate
        self.serving = -1
        self.next_event_time = 0
        self.charger_queue = []

    def set_busy(self, sID, arrival_time):
        if self.idle:
            self.idle = False
            self.serving = sID
            self.next_event_time = arrival_time + self.charging_time
        else:
            self.charger_queue.append((sID, arrival_time))

    def set_next(self):
        waiting_time = 0

        if len(self.charger_queue) > 0:
            item = self.charger_queue.pop(0)
            self.serving = item[0]
            waiting_time = self.next_event_time - item[1]
            self.next_event_time = self.next_event_time + self.charging_time
            self.idle = False
            return waiting_time

        self.idle = True
        self.serving = -1
        return waiting_time

    def enqueue_car(self, sID, arrival_time):
        self.charger_queue.append((sID, arrival_time))


    def reset(self):
        self.idle = True
        self.next_event_time = 0
        self.serving = -1
        self.charger_queue = []

def distance_calculation(u, v):
    return math.sqrt((abs(v[0]-u[0]))**2+abs((v[1]-u[1]))**2)

def total_time_on_charging_calculation(tmp_car, tmp_charger):
    return int(distance_calculation(tmp_charger.coordinate,tmp_car.coordinate)/5)+len(tmp_charger.charger_queue)*tmp_charger.charging_time

def preference_update(tmp_car, charger_list):
    tmp_car.total_charging_time = []
    for tmp_charger in charger_list:
        tmp_car.total_charging_time.append(total_time_on_charging_calculation(tmp_car, tmp_charger))

    i = 0
    y = []
    for time in tmp_car.total_charging_time:
        if tmp_car.total_charging_time[i] == min(tmp_car.total_charging_time):
            break
        i += 1
    tmp_car.preference = []
    y.append(i)
    tmp_car.set_preference(y)
    i = 0

def change_to_time_format(value):
    if value%60 >= 10:
        return str(int(value/60))+":"+str(value%60)
    return str(int(value/60))+":0"+str(value%60)


def initialization(car_list, charger_list, current_day):


    for tmp_car in car_list:
        tmp_car.retrieve_arrival_time_and_preference(current_day)

    for tmp_charger in charger_list:
        tmp_charger.reset()

    return car_list, charger_list


def timing_routine(car_list, charger_list, current_time, termination_time, total_charger):

    min_car_time = termination_time * 100
    for tmp_car in car_list:
        min_car_time = min(min_car_time, tmp_car.next_event_time)

    min_charger_time = termination_time * 100
    for tmp_charger in charger_list:
        if not tmp_charger.idle:
            min_charger_time = min(min_charger_time, tmp_charger.next_event_time)


    current_time = min(min_car_time, min_charger_time)

    return current_time

def call_event(car_list, charger_list, current_day, current_time, termination_time, total_charger, simulation_log):

    current_waiting_time = 0
    current_traveling_time = 0
    current_tour_time = 0
    for tmp_car in car_list:
        if tmp_car.next_event_time == current_time:
            if tmp_car.next_event_type == "arrival":
                if tmp_car.ID < usingrate:
                    preference_update(tmp_car, charger_list)
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Car " + str(tmp_car.ID+1) + " starts traveling", "len(Queue)":"NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                time = int(distance_calculation(charger_list[tmp_car.preference_record[0][0]].coordinate,tmp_car.coordinate)/5)
                current_traveling_time = current_traveling_time + time
                tmp_car.next_event_time = current_time + time
                tmp_car.next_event_type = "traveling"
            elif tmp_car.next_event_type == "traveling":
                if tmp_car.ID < usingrate:
                    preference_update(tmp_car, charger_list)
                target_charger = tmp_car.preference.pop(0)
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Car " + str(tmp_car.ID+1) + " arrives at charger " + str(target_charger+1), "len(Queue)":str(len(charger_list[target_charger].charger_queue)+1)}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                charger_list[target_charger].enqueue_car(tmp_car.ID, current_time)
                tmp_car.next_event_time = termination_time * 100
                tmp_car.next_event_type = "waiting"
            elif tmp_car.next_event_type == "waiting":
                tmp_car.next_event_time = termination_time * 100
            elif tmp_car.next_event_type == "departure":
                datum = {"Day": current_day, "Time": change_to_time_format(current_time),
                         "Event": "Car " + str(tmp_car.ID + 1) + " finish traveling", "len(Queue)": "NA"}
                if current_time>termination_time:
                    datum = {"Day":current_day+1, "Time":change_to_time_format(current_time-termination_time), "Event":"Car " + str(tmp_car.ID+1) + " finish traveling", "len(Queue)":"NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                tmp_car.next_event_time = termination_time* 1000
                tmp_car.is_departed = True

    for tmp_charger in charger_list:
        if tmp_charger.idle and len(tmp_charger.charger_queue) > 0:
            tmp_charger.next_event_time = current_time
            tmp_charger.set_next()


        elif not tmp_charger.idle and tmp_charger.next_event_time == current_time:
            if current_time> termination_time:
                datum = {"Day":current_day+1, "Time":change_to_time_format(0), "Event":"Car " + str(tmp_charger.serving+1) + " cannot finish charging and depart at charger " + str(tmp_charger.ID+1), "len(Queue)":"NA"}
            else:
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Car " + str(tmp_charger.serving+1) + " departs at charger " + str(tmp_charger.ID+1), "len(Queue)":str(len(tmp_charger.charger_queue))}
            simulation_log = simulation_log.append(datum, ignore_index=True)
            if len(car_list[tmp_charger.serving].preference) == 0:
                car_list[tmp_charger.serving].next_event_type = "departure"
                time = int(distance_calculation(tmp_charger.coordinate,car_list[tmp_charger.serving].coordinate)/5)
                current_traveling_time = current_traveling_time + time
                car_list[tmp_charger.serving].next_event_time = current_time + time
                current_tour_time = current_tour_time + (car_list[tmp_charger.serving].next_event_time - car_list[tmp_charger.serving].arrival_time)
            else:
                car_list[tmp_charger.serving].next_event_type = "traveling"
                time = int(distance_calculation(tmp_charger.coordinate,car_list[tmp_charger.serving].coordinate)/5)
                current_traveling_time = current_traveling_time + time
                car_list[tmp_charger.serving].next_event_time = current_time + time
            current_waiting_time = current_waiting_time + tmp_charger.set_next()


    return car_list, charger_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time

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

def output_config(D, n, N, Charger_charging_time, config_file, car_file, log_file, summary_file):

    header_list = ["ColA", "ColB"]
    record_config = pd.DataFrame([], columns = header_list)

    record_config = record_config.append({"ColA":"D","ColB":str(D)}, ignore_index=True)
    record_config = record_config.append({"ColA":"n","ColB":str(n)}, ignore_index=True)
    record_config = record_config.append({"ColA":"N","ColB":str(N)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Charger_charging_time","ColB":str(Charger_charging_time)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Car_file","ColB":str(car_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Log_file","ColB":str(log_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Summary_file","ColB":str(summary_file)}, ignore_index=True)

    record_config.to_csv(config_file, index = False, header = False)

def charging_time_type(type):
    if (type == 1):
        return 45
    elif (type == 2):
        return 120
    elif (type == 3):
        return 240

def reset_car_and_charger(car_list,charger_list):
    for tmp_car in car_list:
        tmp_car.preference = []
        tmp_car.coordinate = []
        tmp_car.destination= []
        tmp_car.destination_record = []
        tmp_car.preference_record = []
        tmp_car.arrival_time_record = []
        tmp_car.distance_record = []

    for tmp_charger in charger_list:
        tmp_charger.coordinate = []


curr_time = 0
isFileInput = False
car_list = []

if len(sys.argv) == 2:

    isFileInput = True
    config = pd.read_csv(sys.argv[1], header=None, index_col=0, skip_blank_lines=True)
    print(config)

    D = int(config[1].D)
    n = int(config[1].n)
    N = int(config[1].N)
    Charger_charging_time = list(map(int, config[1].Charger_charging_time.split("[")[1].split("]")[0].split(",")))
    car_file = config[1].Car_file
    log_file = config[1].Log_file
    summary_file = config[1].Summary_file

    car_df = pd.read_csv(car_file, header=0, skip_blank_lines=True)

    for ind, row in car_df.iterrows():
        tmp_car = Car(row["car_id"]-1)
        for d in np.arange(D):
            s = row["arrival_time_day_"+str(d+1)].split(":")
            tmp_car.set_arrival_time((int(s[0])-11)*60+int(s[1]))
            one_base_list = list(map(int, row["preference_day_"+str(d+1)].split("[")[1].split("]")[0].split(",")))
            tmp_car.set_preference([x-1 for x in one_base_list])
        car_list.append(tmp_car)


else:

    D = 1
    n = 10
    N = 100
    Charger_charging_time = []
    Charger_coord = []
    Destination = []
    config_file = "config_default_random.csv"
    car_file = "car_default_random.csv"
    log_file = "simulation_log.csv"
    summary_file = "simulation_summary.csv"

    carid = 0
    set_destination = []

    while carid < N:
        tmp_car = Car(carid)
        i = 0
        while i < D:
            tmp_car.set_arrival_time(int(480+np.random.uniform(180)))
            tmp_car.set_destination(random.sample(range(0, 99), 2))
            tmp_car.set_coordinate(random.sample(range(0, 99), 2))
            i = i + 1
        car_list.append(tmp_car)
        carid = carid + 1

    for tmp_car in car_list:
        i = 0
        distance = []
    i = 0
    while i < n:
        Charger_charging_time.append(charging_time_type(random.randint(1,3)))
        i = i + 1




termination_time = 1440
current_day = 1
charger_list = []
chargerid = 0
debug = False
y = []
for charging_time in Charger_charging_time:
    coordinate = random.sample(range(0,99), 2)
    new_charger = Charger(chargerid, charging_time, coordinate)
    charger_list.append(new_charger)
    chargerid = chargerid + 1

for tmp_car in car_list:
    i = 0
    while i < D:
        for tmp_charger in charger_list:
            for destination in tmp_car.destination_record:
                tmp_car.distance_record.append(distance_calculation(destination, tmp_charger.coordinate))
        x = 0
        for distance in tmp_car.distance_record:
            if (min(tmp_car.distance_record) == distance):
                break
            x += 1

        y.append(x)
        x = 0
        preference = y
        tmp_car.set_preference(preference)

        y = []
        i = i + 1



simulation_log = pd.DataFrame([], columns = ["Day", "Time", "Event", "len(Queue)"])
simulation_summary = pd.DataFrame([], columns = ["Day", "TotalWaitingTime", "TotalTravelingTime", "TotalTourTime"])

while current_day <= D:

    car_list, charger_list = initialization(car_list, charger_list, current_day)
    current_time = 0
    is_system_clear = True
    total_waiting_time = 0
    total_waiting_time_ofsuer = 0
    total_traveling_time = 0
    total_tour_time = 0

    while current_time < termination_time or not is_system_clear:

        if debug:
            print(current_time)

        current_time = timing_routine(car_list, charger_list, current_time, termination_time, n)

        car_list, charger_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time = call_event(car_list, charger_list, current_day, current_time, termination_time, n, simulation_log)
        is_system_clear = True
        for tmp_car in car_list:
            if not tmp_car.is_departed:
                is_system_clear = False

        if current_time > termination_time:
            for tmp_car in car_list:
                if tmp_car.next_event_type == "waiting":
                    tmp_car.preference = []
                    datum = {"Day": current_day+1, "Time": change_to_time_format(0),
                             "Event": "Car " + str(tmp_car.ID + 1) + " cannot wait for a charger today and finish traveling", "len(Queue)": "NA"}
                    simulation_log = simulation_log.append(datum, ignore_index=True)
                    tmp_car.next_event_time = termination_time * 100
                    tmp_car.next_event_type = "departure"
                    tmp_car.is_departed = True

        total_waiting_time = total_waiting_time + current_waiting_time
        total_traveling_time = total_traveling_time + current_traveling_time
        total_tour_time = total_tour_time + current_tour_time

    datum = {"Day":current_day, "TotalWaitingTime":total_waiting_time, "TotalTravelingTime":total_traveling_time, "TotalTourTime":total_tour_time}
    simulation_summary = simulation_summary.append(datum, ignore_index=True)
    current_day = current_day + 1

if not isFileInput:
    output_car(car_list, car_file, D)
    output_config(D, n, N, Charger_charging_time, config_file, car_file, log_file, summary_file)


simulation_log.to_csv(log_file, index = False)
simulation_summary.to_csv(summary_file, index = False)
print("Total Waiting Time:"+ str(total_waiting_time))
print("Total Traveling Time:"+ str(total_traveling_time))
print("Total Tour Time:"+ str(total_tour_time))