import pickle
from driver import Driver
from trueskill import Rating, rate, rate_1vs1


def sgn(x):
    return x/abs(x)


class RatingManager:
    def __init__(self, file_name):
        self.file_name = file_name
        try:
            with open(self.file_name, "rb") as f:
                self.data = pickle.load(f)
                print("Loaded rating data")
                print(self.data)
        except FileNotFoundError as _:
            self.data = {}

    def get_rating(self, driver):
        if isinstance(type(driver), Driver):
            driver = driver.id
        if driver not in self.data:
            self.data[driver] = Rating()
        return self.data[driver]

    def send_lap_scores(self, scores):
        self.data['void'] = Rating()
        ordered_ratings = list(map(
            lambda x: {x[0]: self.get_rating(x[0])},
            scores
        ))
        for new_dict in rate(ordered_ratings):
            self.data.update(new_dict)

    def send_result_scores(
            self,
            winner_driver_id,
            loser_driver_id,
            point_diff,
    ):
        self.data['void'] = Rating()
        self.get_rating(winner_driver_id)
        self.get_rating(loser_driver_id)

        for _ in range(point_diff):
            (
                self.data[winner_driver_id],
                self.data[loser_driver_id]
            ) = rate_1vs1(
                self.data[winner_driver_id],
                self.data[loser_driver_id]
            )

    def save(self):
        print(self.data)
        with open(self.file_name, "wb") as f:
            pickle.dump(self.data, f)
