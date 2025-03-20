import numpy as np
from fastf1 import get_session
from team import TeamBuilder
from pickle import load as binary_load, dump as binary_dump
from helper import avg, str_session_data


def position_to_points(pos):
    return ([25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * 10)[int(pos - 1)]


def pace_score(drive_score, driver_space):
    return drive_score * (1 - driver_space**1/3)


def score_found(scores, driver):
    for (scored_driver, _score) in scores:
        if driver == scored_driver:
            return True
    return False


class Session:
    def __init__(self, session_data):
        session = get_session(*session_data)
        session.load()
        self.space_data_file = f"space_data_{str_session_data(session_data)}.dat"
        self.drivers = list(map(
            lambda driver_num: session.get_driver(driver_num)["DriverId"],
            session.drivers
        ))

        team_builders = {}
        for driver_num in session.drivers:
            driver = session.get_driver(driver_num)
            team_id = driver["TeamId"]

            if team_id not in team_builders:
                team_builders[team_id] = TeamBuilder(session, team_id)
            team_builders[team_id].add_driver(driver)

        self.teams = {}
        for key in team_builders.keys():
            self.teams[key] = team_builders[key].build()

        self.session_laps = []
        for i in range(session.total_laps + 1):
            self.session_laps.append(session.laps[session.laps["LapNumber"] == i])

        try:
            with open(self.space_data_file, "rb") as f:
                self.spaces_data = binary_load(f)
        except Exception as _:
            print("Spaces Cache not found")
            self.spaces_data = {}

    def calculate_lap_score(self, driver, achieved_time):
        for (lap, driver1_time) in driver.lap_time():
            drive_score = achieved_time / driver1_time
            driver_space = driver.get_space(
                self.spaces_data,
                self.session_laps[lap],
                lap
            )
            send_data = (driver.id, pace_score(drive_score, driver_space))
            if np.isnan(send_data[1]):
                continue
            if lap not in self.laps:
                self.laps[lap] = [send_data]
                continue
            self.laps[lap].append(send_data)

    def calculate_lap_scores(self):
        self.laps = {}
        for team in self.teams.values():
            achieved_time = team.get_achieved_time()
            self.calculate_lap_score(team.driver1, achieved_time)
            self.calculate_lap_score(team.driver2, achieved_time)

    def fill_missing_drivers(self, scores):
        for driver in self.drivers:
            if score_found(scores, driver):
                continue
            scores.append((driver, 0))

    def run_elo_round_for_lap_scores(self, rating_manager):
        assert self.laps

        for (lap, net_score) in self.laps.items():
            self.fill_missing_drivers(net_score)
            net_score.sort(key=lambda x: x[1], reverse=True)
            scores = list(map(lambda x: x[1], net_score))
            rating_manager.send_lap_scores([*net_score])
            print(f"{lap}: {net_score[0][0]} ({net_score[0][1]:.2%}) (net: {avg(scores):.2%})")

    def run_elo_round_for_results(self, rating_manager):
        for team in self.teams.values():
            driver1_points = position_to_points(team.driver1.data["Position"])
            driver2_points = position_to_points(team.driver2.data["Position"])
            diff = abs(driver1_points - driver2_points) * 10
            if driver1_points > driver2_points:
                rating_manager.send_result_scores(
                    team.driver1.id,
                    team.driver2.id,
                    diff
                )
                continue
            rating_manager.send_result_scores(
                team.driver2.id,
                team.driver1.id,
                diff
            )

    def save(self):
        with open(self.space_data_file, "wb") as f:
            binary_dump(self.spaces_data, f)
            print("Cache saved")
