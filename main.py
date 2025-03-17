import fastf1
import fastf1.plotting
import pickle
from team import TeamBuilder
from helper import avg, variance

CACHE_FILE = "space_data_brazil.dat"
session = fastf1.get_session(2024, 21, 'R')
session.load()


def pace_score(drive_score, driver_space, is_wet):
    if is_wet:
        return 100 * drive_score

    return 100 * drive_score * (1 - driver_space)


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
is_wet = []
for i in range(session.total_laps + 1):
    session_laps.append(session.laps[session.laps["LapNumber"] == i])
    is_wet.append(session.laps.pick_laps(i).get_weather_data()['Rainfall'].any())


try:
    with open(CACHE_FILE, "rb") as f:
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
        send_data = (team.driver1.id, pace_score(drive_score, driver_space, is_wet[lap]))
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
        send_data = (team.driver2.id, pace_score(drive_score, driver_space, is_wet[lap]))
        if lap not in laps:
            laps[lap] = [send_data]
            continue
        laps[lap].append(send_data)
    if len(scores) == 0:
        continue
    score_avg = avg(scores)
    v_avg = variance(scores) * score_avg
    print(f"{team.driver2.id} analyzed [avg: {score_avg:.2%}, variance: {v_avg:.3%}]")
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(spaces_data, f)
        print("Cache saved")

net_net_score = []
for (lap, net_score) in laps.items():
    scores = list(map(lambda x: x[1], net_score))
    net_net_score += scores
    net_score.sort(key=lambda x: x[1], reverse=True)
    print(f"{lap}: {net_score[0][0]} ({net_score[0][1]:.2f}%) (net: {avg(scores):.2f}%)")
print(f"net net: {avg(net_net_score):.2f}%")

with open(CACHE_FILE, "wb") as f:
    pickle.dump(spaces_data, f)
    print("Cache saved")
