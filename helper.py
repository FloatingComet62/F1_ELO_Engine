def variance(llist):
    if len(llist) == 0:
        return None
    avg_l = avg(llist)
    return sum(map(lambda x: (x - avg_l)**2, llist)) / len(llist)


def avg(llist):
    if len(llist) == 0:
        return None
    return sum(llist) / len(llist)


def get_time(timestamp):
    return timestamp.seconds + 0.000001 * timestamp.microseconds


def str_session_data(session_data):
    return "_".join(map(lambda x: str(x), session_data))

