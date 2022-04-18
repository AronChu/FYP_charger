import numpy as np
import pandas as pd
import random
import math
import csv

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
    distance = math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2)
    return distance/10

def total_time_on_charging_calculation(tmp_car, tmp_charger):
    return int(distance_calculation(tmp_charger.coordinate,tmp_car.coordinate)/12.5)+len(tmp_charger.charger_queue)*tmp_charger.charging_time

def preference_update(tmp_car, charger_list):
    tmp_car.total_charging_time = []
    for tmp_charger in charger_list:
        tmp_car.total_charging_time.append(total_time_on_charging_calculation(tmp_car, tmp_charger))
    y = []
    for time in range(len(tmp_car.total_charging_time)):
        if tmp_car.total_charging_time[time] == min(tmp_car.total_charging_time):
            break

    tmp_car.preference = []
    y.append(time)
    tmp_car.set_preference(y)

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
                time = int(distance_calculation(tmp_charger.coordinate,car_list[tmp_charger.serving].coordinate)/12.5)
                current_traveling_time = current_traveling_time + time
                car_list[tmp_charger.serving].next_event_time = current_time + time
                current_tour_time = current_tour_time + (car_list[tmp_charger.serving].next_event_time - car_list[tmp_charger.serving].arrival_time)
            else:
                car_list[tmp_charger.serving].next_event_type = "traveling"
                time = int(distance_calculation(tmp_charger.coordinate,car_list[tmp_charger.serving].coordinate)/12.5)
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

def user_behavior(behavior_mode):
    if behavior_mode == "weekdays":
        return int(360 + np.random.uniform(240))
    else:
        return int(540 + np.random.uniform(660))

def user_destination_genertate(charger_distribution):
    car_destination_list = []
    car_destination = []
    for district in charger_distribution:
        for x in range(5*int(district[2])):
            car_destination.append(int(district[0]) + random.randint(0, 50))
            car_destination.append(int(district[1]) + random.randint(0, 50))
            car_destination_list.append(car_destination)
            car_destination= []
    return car_destination_list


#main
Number_of_days = 1
Number_of_charger = 80
Number_of_car = 400
config_file = "config_default_random.csv"
car_file = "car_default_random.csv"
log_file = "simulation_log.csv"
summary_file = "simulation_summary.csv"
usingrate = 0*4
termination_time = 1440
current_day = 1
charger_list = []
car_list = []
charger_charging_time = []
charger_coordinate = []
seed = 9
np.random.seed(seed)
random.seed(seed)
cant_find_charger = 0
charger_coordinate_list = []
file = open('charger_coordinate.csv')
csv_reader = csv.reader(file)
charger_distribution = []
behavior_mode = "weekdays"
#behavior_mode = "holiday"
average_waiting_time = []
cant_find_charger_rate = []

#read csv to generate the coordinate of charger
for row in csv_reader:
    charger_distribution.append(row)
for district in charger_distribution:
    for charger in range(int(district[2])):
        charger_coordinate = []
        charger_coordinate.append(int(district[0]) + random.randint(0, 50))
        charger_coordinate.append(int(district[1]) + random.randint(0, 50))
        charger_coordinate_list.append(charger_coordinate)

#init car
car_destination_list = user_destination_genertate(charger_distribution)
for carid in range(Number_of_car):
    tmp_car = Car(carid)
    tmp_car.set_arrival_time(user_behavior(behavior_mode))
    tmp_car.set_destination(car_destination_list[carid])
    tmp_car.set_coordinate(random.sample(range(0, 999), 2))
    car_list.append(tmp_car)

#init charger
for chargerid in range(Number_of_charger):
    charging_time = charging_time_type(random.randint(1, 3))
    charger_charging_time.append(charging_time)
    coordinate = charger_coordinate_list[chargerid]
    new_charger = Charger(chargerid, charging_time, coordinate)
    charger_list.append(new_charger)

#set perference
temp_perference = []
for tmp_car in car_list:
    for tmp_charger in charger_list:
        for destination in tmp_car.destination_record:
            tmp_car.distance_record.append(distance_calculation(destination,tmp_charger.coordinate))
        temp_charger_id = 0
    for distance in tmp_car.distance_record:
        if (min(tmp_car.distance_record) == distance):
            break
        temp_charger_id = temp_charger_id + 1
    temp_perference.append(temp_charger_id)
    temp_charger_id = 0
    preference = temp_perference
    tmp_car.set_preference(preference)
    temp_perference = []

for tmp_car in car_list:
    #print(tmp_car.ID)
    #("Coordinate:")
    #print(tmp_car.coordinate)
    #print("Destination:")
    #print(tmp_car.destination_record)
    #print(tmp_car.distance_record)
    #print(tmp_car.preference_record)
    pass

for tmp_charger in charger_list:
    #print(tmp_charger.coordinate)
    #print(tmp_charger.charging_time)
    pass

#exe
simulation_log = pd.DataFrame([], columns = ["Day", "Time", "Event", "len(Queue)"])
simulation_summary = pd.DataFrame([], columns = ["Day", "TotalWaitingTime", "TotalTravelingTime", "TotalTourTime"])
while(usingrate <= 400):
    #print("usingrate: "+str(usingrate/4)+"%")
    while(current_day <= Number_of_days):
        car_list, charger_list = initialization(car_list, charger_list, current_day)
        current_time = 0
        is_system_clear = True
        total_waiting_time = 0
        total_traveling_time = 0
        total_tour_time = 0
        cant_find_charger = 0
        while current_time < termination_time or not is_system_clear:

            current_time = timing_routine(car_list, charger_list, current_time, termination_time, Number_of_charger)

            car_list, charger_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time = call_event(
                car_list, charger_list, current_day, current_time, termination_time, Number_of_charger, simulation_log)
            is_system_clear = True
            for tmp_car in car_list:
                if not tmp_car.is_departed:
                    is_system_clear = False

            if current_time > termination_time:
                for tmp_car in car_list:
                    if tmp_car.next_event_type == "waiting":
                        tmp_car.preference = []
                        datum = {"Day": current_day + 1, "Time": change_to_time_format(0),
                                 "Event": "Car " + str(
                                     tmp_car.ID + 1) + " cannot wait for a charger today and finish traveling",
                                 "len(Queue)": "NA"}
                        cant_find_charger = cant_find_charger + 1
                        simulation_log = simulation_log.append(datum, ignore_index=True)
                        tmp_car.next_event_time = termination_time * 100
                        tmp_car.next_event_type = "departure"
                        tmp_car.is_departed = True

            total_waiting_time = total_waiting_time + current_waiting_time
            total_traveling_time = total_traveling_time + current_traveling_time
            total_tour_time = total_tour_time + current_tour_time

        datum = {"Day": current_day, "TotalWaitingTime": total_waiting_time, "TotalTravelingTime": total_traveling_time,
                 "TotalTourTime": total_tour_time}
        simulation_summary = simulation_summary.append(datum, ignore_index=True)
        current_day = current_day + 1
        output_car(car_list, car_file, Number_of_days)
        output_config(Number_of_days, Number_of_charger, Number_of_car, charger_charging_time, config_file, car_file, log_file, summary_file)
        average_waiting_time.append((total_waiting_time/Number_of_car))
        cant_find_charger_rate.append(100 * cant_find_charger / Number_of_car)
    current_day = current_day -1
    usingrate = usingrate + 40
simulation_log.to_csv(log_file, index = False)
simulation_summary.to_csv(summary_file, index = False)
for time in average_waiting_time:
    print(time)
for rate in cant_find_charger_rate:
    print(rate)