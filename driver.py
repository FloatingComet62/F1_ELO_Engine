import pickle
import numpy as np
import math

from helper import get_time


class Driver:
    def __init__(self, session, driver_data):
        self.session = session
        self.data = driver_data
        self.id = self.data["DriverId"]
        self.num = self.data["DriverNumber"]

    def lap_time(self):
        laps = self.session.laps \
            .pick_drivers(self.num) \
            .pick_wo_box()
        lap_times = []
        # Sometimes driver pace trackers don't work
        # e.g. Sau Paulo 2024, GASLLLLLLLLLLLLLY
        try:
            last_position = laps.iloc[0]["Position"]
        except Exception as _:
            return []

        for lap_idx in range(len(laps)):
            if lap_idx == 0:
                # todo: maybe don't?
                # skip opening lap
                continue
            lap = laps.iloc[lap_idx]
            new_position = lap["Position"]

            # if position change, skip
            if new_position != last_position:
                last_position = new_position
                continue
            last_position = new_position
            lap_times.append((int(lap["LapNumber"]), get_time(lap["LapTime"])))
        return lap_times

    def get_space(self, spaces_data, lap_data, lap_num):
        a = 1
        b = 4
        if self.id in spaces_data and lap_num in spaces_data[self.id]:
            spaces = spaces_data[self.id][lap_num]
            return (
                a * (1-math.exp(-spaces[0] / 1000)) +
                b * (1-math.exp(-spaces[1] / 1000))
            ) / (a+b)

        print(f"Calculating space for {self.id} for Lap {lap_num}")
        position = int(lap_data[lap_data["DriverNumber"] == self.num]["Position"].iloc[0])

        ahead_lap = lap_data.pick_drivers(self.num)
        distance_ahead = ahead_lap \
            .get_car_data() \
            .add_driver_ahead()["DistanceToDriverAhead"].mean()
        if np.isnan(distance_ahead):
            distance_ahead = math.inf

        try:
            driver_behind = str(lap_data[lap_data["Position"] == position + 1]["Driver"].iloc[0])
            behind_lap = lap_data.pick_drivers(driver_behind)
            distance_behind = behind_lap \
                .get_car_data() \
                .add_driver_ahead()["DistanceToDriverAhead"].mean()
        except IndexError as _:
            distance_behind = math.inf

        if self.id not in spaces_data:
            spaces_data[self.id] = {}
        spaces_data[self.id][lap_num] = (distance_ahead, distance_behind)
        spaces = spaces_data[self.id][lap_num]
        return (
            a * (1-math.exp(-spaces[0] / 1000)) +
            b * (1-math.exp(-spaces[1] / 1000))
        ) / (a+b)


class DummyDriver:
    def __init__(self, session):
        self.session = session
        self.id = 'void'
        self.num = 0

    def lap_time(self):
        lap_times = []
        for i in range(self.session.total_laps):
            lap_times.append((i + 1, math.inf))
        return lap_times

    def get_space(self, _spaces_data, _lap_data, _lap_num):
        return 1
