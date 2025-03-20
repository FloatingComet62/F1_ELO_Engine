from pickle import load

try:
    with open("rating.dat", "rb") as f:
        data = list(load(f).items())
        data.sort(key=lambda x: x[1], reverse=True)
        for (i, (driver_id, rating)) in enumerate(data):
            print(f"{i + 1} {driver_id} {rating.mu}")
except FileNotFoundError:
    print("No rating data")
