from pickle import load

try:
    with open("rating.dat", "rb") as f:
        data = list(load(f).items())
        data.sort(key=lambda x: x[1], reverse=True)
        for (i, (driver_id, rating)) in enumerate(data):
            if driver_id == 'void':
                continue
            s = f"{i+1} {driver_id}"
            print(f"{s.ljust(30)} {rating.mu:.2f}")
except FileNotFoundError:
    print("No rating data")
