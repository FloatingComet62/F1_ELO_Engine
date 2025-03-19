import fastf1
import fastf1.plotting
import pickle
from team import TeamBuilder
from helper import avg, variance, str_session_data
from rating import RatingManager

RATING_FILE = "rating.dat"
SESSION = (2024, 21, 'R')
SPACE_DATA_FILE = f"space_data_{str_session_data(SESSION)}.dat"

rating_manager = RatingManager(RATING_FILE)
session = fastf1.get_session(*SESSION)
session.load()


def position_to_points(pos):
    return ([25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * 10)[int(pos - 1)]


def pace_score(drive_score, driver_space):
    return drive_score * (1 - driver_space**1/3)


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

session_laps = []
for i in range(session.total_laps + 1):
    session_laps.append(session.laps[session.laps["LapNumber"] == i])

try:
    with open(SPACE_DATA_FILE, "rb") as f:
        spaces_data = pickle.load(f)
except Exception as _:
    print("Spaces Cache not found")
    spaces_data = {}

laps = {}
scores = []
for team in teams.values():
    achieved_time = team.get_achieved_time()
    scores.clear()
    for (lap, driver1_time) in team.driver1.lap_time():
        drive_score = achieved_time / driver1_time
        scores.append(drive_score)
        driver_space = team.driver1.get_space(spaces_data, session_laps[lap], lap)
        send_data = (team.driver1.id, pace_score(drive_score, driver_space))
        if lap not in laps:
            laps[lap] = [send_data]
            continue
        laps[lap].append(send_data)
    if len(scores) != 0:
        score_avg = avg(scores)
        v_avg = variance(scores) * score_avg
        print(f"{team.driver1.id} analyzed [avg: {score_avg:.2%}, variance: {v_avg:.3%}]")
    scores.clear()
    for (lap, driver2_time) in team.driver2.lap_time():
        drive_score = achieved_time / driver2_time
        scores.append(drive_score)
        driver_space = team.driver2.get_space(spaces_data, session_laps[lap], lap)
        send_data = (team.driver2.id, pace_score(drive_score, driver_space))
        if lap not in laps:
            laps[lap] = [send_data]
            continue
        laps[lap].append(send_data)
    if len(scores) == 0:
        continue
    score_avg = avg(scores)
    v_avg = variance(scores) * score_avg
    print(f"{team.driver2.id} analyzed [avg: {score_avg:.2%}, variance: {v_avg:.3%}]")

for (lap, net_score) in laps.items():
    net_score.sort(key=lambda x: x[1], reverse=True)
    scores = list(map(lambda x: x[1], net_score))
    #rating_manager.send_lap_scores([*net_score])
    print(f"{lap}: {net_score[0][0]} ({net_score[0][1]:.2%}) (net: {avg(scores):.2%})")

print(session.results)
for team in teams.values():
    driver1_points = position_to_points(team.driver1.data["Position"])
    driver2_points = position_to_points(team.driver2.data["Position"])
    diff = abs(driver1_points - driver2_points)
    if driver1_points > driver2_points:
        rating_manager.send_result_scores(team.driver1.id, team.driver2.id, diff)
    else:
        rating_manager.send_result_scores(team.driver2.id, team.driver1.id, diff)

with open(SPACE_DATA_FILE, "wb") as f:
    pickle.dump(spaces_data, f)
    print("Cache saved")

rating_manager.deinit()
