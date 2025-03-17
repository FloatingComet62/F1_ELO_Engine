# import pandas as pd
import fastf1
import fastf1.plotting
# import datetime
import math
import numpy as np
import pickle
# import matplotlib.pyplot as plt

session = fastf1.get_session(2024, 1, 'R')
session.load()


def variance(llist):
    avg_l = avg(llist)
    return sum(map(lambda x: (x - avg_l)**2, llist)) / len(llist)


def avg(llist):
    return sum(llist) / len(llist)


def get_time(timestamp):
    return timestamp.seconds + 0.000001 * timestamp.microseconds


with open("space_data.dat", "rb") as f:
    spaces_data = pickle.load(f)
    print(spaces_data['max_verstappen'])


def get_driver_space(lap, lap_num, driver_num, did):
    a = 1
    b = 4
    spaces = spaces_data[did][lap_num]
    return a * (1-math.exp(-spaces[0] / 1000)) + b * (1-math.exp(-spaces[1] / 1000))


"""
    position = int(lap[lap["DriverNumber"] == driver_num]["Position"].iloc[0])

    ahead_lap = lap.pick_drivers(driver_num)
    distance_ahead = ahead_lap \
        .get_car_data() \
        .add_driver_ahead()["DistanceToDriverAhead"].mean()
    if np.isnan(distance_ahead):
        distance_ahead = math.inf

    try:
        driver_behind = str(lap[lap["Position"] == position + 1]["Driver"].iloc[0])
        behind_lap = lap.pick_drivers(driver_behind)
        distance_behind = behind_lap \
            .get_car_data() \
            .add_driver_ahead()["DistanceToDriverAhead"].mean()
    except IndexError as _:
        distance_behind = math.inf

    if did not in spaces_data:
        spaces_data[did] = {}
    spaces_data[did][lap_num] = (distance_ahead, distance_behind)
    return a * distance_ahead + b * (1-math.exp(-distance_behind))
"""


def lap_times(session, driver):
    laps = session.laps.pick_drivers(driver["DriverNumber"]).pick_wo_box()
    lap_times = []
    last_position = laps.iloc[0]["Position"]
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


class TeamBuilder:
    def __init__(self, session, team_id):
        self.session = session
        self.team_id = team_id

    def add_driver(self, driver):
        if "driver1" not in dir(self):
            self.driver1 = driver
            return
        if "driver2" not in dir(self):
            self.driver2 = driver
            return
        # Todo: handle this scenaio
        raise ValueError("A team can't have more than 2 driver on a grid at a time")

    def build(self):
        return Team(self.session, self.team_id, self.driver1, self.driver2)


class Team:
    def __init__(self, session, team_id, driver1, driver2):
        self.session = session
        self.team_id = team_id
        self.driver1 = driver1
        self.driver2 = driver2

    def get_achieved_time(self):
        if "achieved_time" in dir(self):
            return self.achieved_time
        lap_results = session.laps.pick_drivers([
            self.driver1["DriverNumber"],
            self.driver2["DriverNumber"]
        ]).pick_wo_box().pick_not_deleted().pick_accurate()
        sector_bests = [999, 999, 999]
        for lap_idx in range(len(lap_results)):
            lap = lap_results.iloc[lap_idx]
            try:
                sector_bests[0] = min(sector_bests[0], get_time(lap["Sector1Time"]))
                sector_bests[1] = min(sector_bests[1], get_time(lap["Sector2Time"]))
                sector_bests[2] = min(sector_bests[2], get_time(lap["Sector3Time"]))
            except Exception as _:
                pass
        self.achieved_time = sum(sector_bests)
        return self.achieved_time

    def __str__(self):
        return f"{self.team_id}({self.driver1}, {self.driver2})"


team_builders = {}
for driver_num in session.drivers:
    driver = session.get_driver(driver_num)
    team_id = driver["TeamId"]

    if team_id not in team_builders:
        team_builders[team_id] = TeamBuilder(session, team_id)
    team_builders[team_id].add_driver(driver)

teams = {}
for key in team_builders.keys():
    teams[key] = team_builders[key].build()

laps = {}
session_laps = []
for i in range(session.total_laps + 1):
    session_laps.append(session.laps[session.laps["LapNumber"] == i])

for (team, team_data) in teams.items():
    achieved_time = team_data.get_achieved_time()
    driver1_times = lap_times(session, team_data.driver1)
    driver2_times = lap_times(session, team_data.driver2)
    driver1_id = team_data.driver1["DriverId"]
    driver2_id = team_data.driver2["DriverId"]
    for (lap, driver1_time) in driver1_times:
        score = achieved_time / driver1_time
        driver_space = get_driver_space(session_laps[lap], lap, team_data.driver1["DriverNumber"], driver1_id)
        send_data = (driver1_id, driver_space)
        if lap not in laps:
            laps[lap] = [send_data]
            continue
        laps[lap].append(send_data)
    print(f"{driver1_id} analyzed")
    for (lap, driver2_time) in driver2_times:
        score = achieved_time / driver2_time
        driver_space = get_driver_space(session_laps[lap], lap, team_data.driver2["DriverNumber"], driver2_id)
        send_data = (driver2_id, driver_space)
        if lap not in laps:
            laps[lap] = [send_data]
            continue
        laps[lap].append(send_data)
    print(f"{driver2_id} analyzed")

# with open("space_data.dat", "wb") as f:
#     pickle.dump(spaces_data, f)

for (lap, lap_times) in laps.items():
    lap_times.sort(key=lambda x: x[1], reverse=True)
    print(f"{lap}: {lap_times[0][0]} ({lap_times[0][1]})")

# Position changes (used to track overtakes)
"""
fig, ax = plt.subplots(figsize=(8.0, 4.9))

for driver in session.drivers:
    driver_laps = session.laps.pick_drivers(driver)
    driver_abbreviation = driver_laps['Driver'].iloc[0]
    style = fastf1.plotting.get_driver_style(
        identifier=driver_abbreviation,
        style=['color', 'linestyle'],
        session=session
    )
    ax.plot(
        driver_laps['LapNumber'],
        driver_laps['Position'],
        label=driver_abbreviation,
        **style
    )

ax.set_ylim([20.5, 0.5])
ax.set_yticks([1, 5, 10, 15, 20])
ax.set_xlabel('Lap')
ax.set_ylabel('Position')

ax.legend(bbox_to_anchor=(1.0, 1.02))
plt.tight_layout()
plt.show()
"""

# Typr strategies (tracking per sector pace for on different types is a bad thing)
"""
laps = session.laps
drivers = session.drivers
driver_abbreviations = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Driver", "Stint", "Compound"])
stints = stints.count().reset_index()
stints = stints.rename(columns={"LapNumber": "StintLength"})

fig, ax = plt.subplots(figsize=(5, 1))
for driver in driver_abbreviations:
    driver_stints = stints.loc[stints["Driver"] == driver]

    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        compound_color = fastf1.plotting.get_compound_color(
            row["Compound"],
            session=session
        )
        plt.barh(
            y=driver,
            width=row["StintLength"],
            left=previous_stint_end,
            color=compound_color,
            edgecolor="black",
            fill=True
        )
        previous_stint_end += row["StintLength"]

plt.xlabel("Lap Number")
plt.grid(False)
ax.invert_yaxis()

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.show()
"""
