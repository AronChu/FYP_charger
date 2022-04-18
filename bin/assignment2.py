import numpy as np
import pandas as pd
import scipy.linalg as la
from numpy.linalg import matrix_power
import matplotlib.pyplot as plt
import heapq
import sys
import random
import math

# the object for Student(Customer)
class Student:
    # key is ID, 0-based
    # constructor
    def __init__(self, ID):
        self.ID = ID
        self.arrival_time_record = []
        self.preference_record = []

    # setter for arrival_time
    def set_arrival_time(self, arrival_time):
        self.arrival_time = arrival_time
        self.arrival_time_record.append(arrival_time)

    # setter for preference
    def set_preference(self, preference):
        self.preference = preference
        self.preference_record.append(preference)

    def __lt__(self,other):
        return self.ID < other.ID

    # used in initialization at the beginning of each day
    def retrieve_arrival_time_and_preference(self, day):
        self.arrival_time = self.arrival_time_record[day-1]
        self.preference = self.preference_record[day-1].copy()
        self.is_arrived = False
        self.next_event_time = self.arrival_time
        self.next_event_type = "arrival"
        self.is_departed = False



# the object for Booth(Server)
class Booth:
    # key is ID, 0-based
    # constructor
    def __init__(self, ID, service_time):
        self.idle = True
        self.ID = ID
        self.service_time = service_time
        self.serving = -1
        self.next_event_time = 0
        self.booth_queue = []

    # When a student comes in front of this booth
    def set_busy(self, sID, arrival_time):
        if self.idle:
            self.idle = False
            self.serving = sID
            self.next_event_time = arrival_time + self.service_time
        else:
            self.booth_queue.append((sID, arrival_time))

    # When a student depart from this booth, set_next() method is called
    # The purpose is either moving next student to the boost, or set booth to idle
    # This method returns the waiting time of the next student
    def set_next(self):
        waiting_time = 0

        if len(self.booth_queue) > 0:
            item = self.booth_queue.pop(0)
            self.serving = item[0]
            waiting_time = self.next_event_time - item[1]
            self.next_event_time = self.next_event_time + self.service_time
            self.idle = False
            return waiting_time

        self.idle = True
        self.serving = -1
        return waiting_time

    # When a student comes in front of this booth, and this booth is busy
    def enqueue_student(self, sID, arrival_time):
        self.booth_queue.append((sID, arrival_time))

    # used in initialization at the beginning of each day
    def reset(self):
        self.idle = True
        self.next_event_time = 0
        self.serving = -1
        self.booth_queue = []

# Function for calculating the travelling time between two booths, or one booth to exit/entrance
def traveling_time(location1, location2, n):
    if str(location2) == "Library":
        return math.floor((location1+1)/2)
    elif str(location2) == "SC":
        return math.floor((n-location1+2)/2)
    if str(location1) == "Library":
        return math.floor((location2+1)/2)
    elif str(location1) == "SC":
        return math.floor((n-location2+2)/2)
    else:
        return abs(math.floor((location1+1)/2)-math.floor((location2+1)/2))

# Convert time (in min) back to string format
# for example, 121 time unit = 2hr + 1min, means "13:01"
# You should return "13:01" instead of "13:1" in this example
def change_to_time_format(value):
    if value%60 >= 10:
        return str(int(11+value/60))+":"+str(value%60)
    return str(int(11+value/60))+":0"+str(value%60)


# initialize both customers and servers at the beginning of each day
def initialization(student_list, booth_list, current_day):

    # reset student and booth

    for tmp_student in student_list:
        tmp_student.retrieve_arrival_time_and_preference(current_day)

    for tmp_booth in booth_list:
        tmp_booth.reset()

    return student_list, booth_list


# determine time of next event
def timing_routine(student_list, booth_list, current_time, termination_time, total_booth):

    # time of next event can depend on arrival
    min_student_time = termination_time * 100
    for tmp_student in student_list:
        min_student_time = min(min_student_time, tmp_student.next_event_time)

    # time of next event can depend on booth
    min_booth_time = termination_time * 100
    for tmp_booth in booth_list:
        if not tmp_booth.idle:
            min_booth_time = min(min_booth_time, tmp_booth.next_event_time)


    # advance to the time
    current_time = min(min_student_time, min_booth_time)

    return current_time

# extract and evaulate all jobs happens at current time
def call_event(student_list, booth_list, current_day, current_time, termination_time, total_booth, simulation_log):

    current_waiting_time = 0
    current_traveling_time = 0
    current_tour_time = 0


    # student events
    # the idea is to use a state machine
    # "arrival" -> "traveling" -> "waiting" <-> "traveling" -> "depart"
    for tmp_student in student_list:
        if tmp_student.next_event_time == current_time:
            if tmp_student.next_event_type == "arrival":
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Student " + str(tmp_student.ID+1) + " arrives Art Fair", "len(Queue)":"NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                time = traveling_time(tmp_student.preference[0]+1, "Library", total_booth)
                current_traveling_time = current_traveling_time + time
                tmp_student.next_event_time = current_time + time
                tmp_student.next_event_type = "traveling"
            elif tmp_student.next_event_type == "traveling":
                target_booth = tmp_student.preference.pop(0)
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Student " + str(tmp_student.ID+1) + " arrives at booth " + str(target_booth+1), "len(Queue)":str(len(booth_list[target_booth].booth_queue)+1)}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                booth_list[target_booth].enqueue_student(tmp_student.ID, current_time)
                tmp_student.next_event_time = termination_time * 100
                tmp_student.next_event_type = "waiting"
            elif tmp_student.next_event_type == "waiting":
                tmp_student.next_event_time = termination_time * 100
            elif tmp_student.next_event_type == "departure":
                datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Student " + str(tmp_student.ID+1) + " departs Art Fair", "len(Queue)":"NA"}
                simulation_log = simulation_log.append(datum, ignore_index=True)
                tmp_student.next_event_time = termination_time * 100
                tmp_student.is_departed = True

    # booth events
    for tmp_booth in booth_list:
        if tmp_booth.idle and len(tmp_booth.booth_queue) > 0:
            tmp_booth.next_event_time = current_time
            tmp_booth.set_next()


        elif not tmp_booth.idle and tmp_booth.next_event_time == current_time:
            datum = {"Day":current_day, "Time":change_to_time_format(current_time), "Event":"Student " + str(tmp_booth.serving+1) + " departs at booth " + str(tmp_booth.ID+1), "len(Queue)":str(len(tmp_booth.booth_queue))}
            simulation_log = simulation_log.append(datum, ignore_index=True)
            if len(student_list[tmp_booth.serving].preference) == 0:
                student_list[tmp_booth.serving].next_event_type = "departure"
                t1 = traveling_time(tmp_booth.ID+1, "Library", total_booth)
                t2 = traveling_time(tmp_booth.ID+1, "SC", total_booth)
                time = min(t1, t2)
                current_traveling_time = current_traveling_time + time
                student_list[tmp_booth.serving].next_event_time = current_time + time
                current_tour_time = current_tour_time + (student_list[tmp_booth.serving].next_event_time - student_list[tmp_booth.serving].arrival_time)
            else:
                student_list[tmp_booth.serving].next_event_type = "traveling"
                time = traveling_time(student_list[tmp_booth.serving].preference[0]+1, tmp_booth.ID+1, total_booth)
                current_traveling_time = current_traveling_time + time
                student_list[tmp_booth.serving].next_event_time = current_time + time
            current_waiting_time = current_waiting_time + tmp_booth.set_next()


    return student_list, booth_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time

# output student record to a csv file
# pay attention: you need to change the 0-based numbers to 1-based numbers in the output
def output_student(student_list, student_file, D):
    header_list = ["student_id"]
    for i in np.arange(D):
        header_list.append("arrival_time_day_"+str(i+1))
    for i in np.arange(D):
        header_list.append("preference_day_"+str(i+1))
    record_student = pd.DataFrame([], columns = header_list)

    for tmp_student in student_list:
        student_dict = {"student_id":tmp_student.ID+1}

        for i in np.arange(D):
            student_dict["arrival_time_day_"+str(i+1)] = change_to_time_format(tmp_student.arrival_time_record[i])
            student_dict["preference_day_"+str(i+1)] = str([x+1 for x in tmp_student.preference_record[i]])

        record_student = record_student.append(student_dict, ignore_index=True)

    record_student.to_csv(student_file, index = False)

# output config to a csv file
def output_config(D, n, N, Booth_promotion_time, config_file, student_file, log_file, summary_file):

    header_list = ["ColA", "ColB"]
    record_config = pd.DataFrame([], columns = header_list)

    record_config = record_config.append({"ColA":"D","ColB":str(D)}, ignore_index=True)
    record_config = record_config.append({"ColA":"n","ColB":str(n)}, ignore_index=True)
    record_config = record_config.append({"ColA":"N","ColB":str(N)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Booth_promotion_time","ColB":str(Booth_promotion_time)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Student_file","ColB":str(student_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Log_file","ColB":str(log_file)}, ignore_index=True)
    record_config = record_config.append({"ColA":"Summary_file","ColB":str(summary_file)}, ignore_index=True)

    record_config.to_csv(config_file, index = False, header = False)


# main program
curr_time = 0
isFileInput = False
student_list = []

if len(sys.argv) == 2:
    # initialization with a config file

    isFileInput = True
    config = pd.read_csv(sys.argv[1], header=None, index_col=0, skip_blank_lines=True)
    print(config)

    D = int(config[1].D)
    n = int(config[1].n)
    N = int(config[1].N)
    Booth_promotion_time = list(map(int, config[1].Booth_promotion_time.split("[")[1].split("]")[0].split(",")))
    student_file = config[1].Student_file
    log_file = config[1].Log_file
    summary_file = config[1].Summary_file

    student_df = pd.read_csv(student_file, header=0, skip_blank_lines=True)

    # retrive the data from student_df(dataframe) to student_list(list of student objects)
    # pay attention: all numbers in the dataframe are 1-based, you need to change them back to 0-based
    for ind, row in student_df.iterrows():
        tmp_student = Student(row["student_id"]-1)
        for d in np.arange(D):
            s = row["arrival_time_day_"+str(d+1)].split(":")
            tmp_student.set_arrival_time((int(s[0])-11)*60+int(s[1]))
            one_base_list = list(map(int, row["preference_day_"+str(d+1)].split("[")[1].split("]")[0].split(",")))
            tmp_student.set_preference([x-1 for x in one_base_list])
        student_list.append(tmp_student)


else:
    # initialization with random numbers

    D = 2
    n = 20
    N = 100
    Booth_promotion_time = []
    config_file = "config_default_random.csv"
    student_file = "student_default_random.csv"
    log_file = "simulation_log.csv"
    summary_file = "simulation_summary.csv"

    # generate DN arrival time for the students
    np.random.seed(0)
    sid = 0
    while sid < N:
        tmp_student = Student(sid)
        i = 0
        while i < D:
            tmp_student.set_arrival_time(int(np.random.uniform(400)))
            i = i + 1
        student_list.append(tmp_student)
        sid = sid + 1

    # generate DN list of distinct integers as the preference of the students
    np.random.seed(1)
    random.seed(1)
    for tmp_student in student_list:
        i = 0
        while i < D:
            p = min(int(np.random.uniform(5)+1), n)
            preference = random.sample(range(0,n), p)
            tmp_student.set_preference(preference)
            i = i + 1

    # generate n numbers as the promotion time of the booths
    np.random.seed(2)
    i = 0
    while i < n:
        Booth_promotion_time.append(int(min(1+np.random.exponential(5), 10)))
        i = i + 1




# main simulation
# initialization before simulation
termination_time = 420
current_day = 1
booth_list = []
bid = 0
debug = False
# create the list of booth objects
for promotion_time in Booth_promotion_time:
    new_booth = Booth(bid, promotion_time)
    booth_list.append(new_booth)
    bid = bid + 1

simulation_log = pd.DataFrame([], columns = ["Day", "Time", "Event", "len(Queue)"])
simulation_summary = pd.DataFrame([], columns = ["Day", "TotalWaitingTime", "TotalTravelingTime", "TotalTourTime"])

while current_day <= D:

    # initialization for a day in the simulation
    student_list, booth_list = initialization(student_list, booth_list, current_day)
    current_time = 0
    is_system_clear = True
    total_waiting_time = 0
    total_traveling_time = 0
    total_tour_time = 0


    while current_time < termination_time or not is_system_clear:

        if debug:
            print(current_time)

        # determine the time
        current_time = timing_routine(student_list, booth_list, current_time, termination_time, n)

        # update different lists and log sheet
        student_list, booth_list, simulation_log, current_waiting_time, current_traveling_time, current_tour_time = call_event(student_list, booth_list, current_day, current_time, termination_time, n, simulation_log)

        # check if Art Fair clear
        is_system_clear = True
        for tmp_student in student_list:
            if not tmp_student.is_departed:
                is_system_clear = False

        if current_time > termination_time:
            for tmp_student in student_list:
                if tmp_student.next_event_type == "waiting":
                    tmp_student.preference = []

        # statistics meausre update, used in the summary
        total_waiting_time = total_waiting_time + current_waiting_time
        total_traveling_time = total_traveling_time + current_traveling_time
        total_tour_time = total_tour_time + current_tour_time

    # at the end of each day, append a row of statistics to the summary file
    datum = {"Day":current_day, "TotalWaitingTime":total_waiting_time, "TotalTravelingTime":total_traveling_time, "TotalTourTime":total_tour_time}
    simulation_summary = simulation_summary.append(datum, ignore_index=True)
    current_day = current_day + 1

# output statistics
if not isFileInput:
    # output student record to student_file
    output_student(student_list, student_file, D)
    # output config file to config_file
    output_config(D, n, N, Booth_promotion_time, config_file, student_file, log_file, summary_file)


simulation_log.to_csv(log_file, index = False)
simulation_summary.to_csv(summary_file, index = False)
