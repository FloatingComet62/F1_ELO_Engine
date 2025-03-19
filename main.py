from fastf1 import Cache
from session import Session
from rating import RatingManager

rating_manager = RatingManager("rating.dat")
Cache.set_disabled()
session = Session((2024, 21, 'R'))
session.calculate_lap_scores()
session.run_elo_round_for_lap_scores(rating_manager)
session.run_elo_round_for_results(rating_manager)

session.deinit()
rating_manager.deinit()
