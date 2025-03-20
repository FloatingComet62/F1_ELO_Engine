from helper import get_time
from driver import Driver, DummyDriver


class TeamBuilder:
    def __init__(self, session, team_id):
        self.session = session
        self.team_id = team_id
        self.driver1 = None
        self.driver2 = None

    def add_driver(self, driver):
        if not self.driver1:
            self.driver1 = Driver(self.session, driver)
            return
        if not self.driver2:
            self.driver2 = Driver(self.session, driver)
            return
        # Todo: handle this scenaio
        raise ValueError("A team can't have more than 2 driver on a grid at a time")

    def build(self):
        if not self.driver2:
            self.driver2 = DummyDriver(self.session)
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
        lap_results = self.session.laps.pick_drivers([
            self.driver1.num,
            self.driver2.num,
        ]).pick_wo_box().pick_not_deleted().pick_accurate()
        sector_bests = [999, 999, 999]
        for lap_idx in range(len(lap_results)):
            lap = lap_results.iloc[lap_idx]
            try:
                sector_bests = list(map(
                    lambda x: min(x, get_time(lap["Sector1Time"])),
                    sector_bests
                ))
            except Exception as _:
                pass
        self.achieved_time = sum(sector_bests)
        return self.achieved_time

    def __str__(self):
        return f"{self.team_id}({self.driver1}, {self.driver2})"
