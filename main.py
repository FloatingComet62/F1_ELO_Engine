# from fastf1 import Cache
from session import Session
from rating import RatingManager

rating_manager = RatingManager("rating.dat")
# Cache.set_disabled()
log = open("log.txt", "a")
log.write("run\n")

for i in range(24):
    try:
        session = Session((2024, i + 1, 'R'))
        session.calculate_lap_scores()
        session.save()
        session.run_elo_round_for_lap_scores(rating_manager)
        session.run_elo_round_for_results(rating_manager)
        rating_manager.save()
    except Exception as e:
        log.write(f"{i}: {str(e)}\n")
        log.flush()
log.close()
