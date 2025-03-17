Engine failure can suck my dick


# First method
## Race

Instead of only comparing race results, we compare EVERY LAP.
Because an ELO engine needs to lot of rounds to be precise.
For chess, it works. For f1, not so much.

Because F1 doesn't have a lot of races
> How many f1 races have ever happened>
> > 1125
> 
> How many FIDE rated chess games have ever happened?
> > Uncountable, but world record of **7 million** over a single day

So my initial thought was, every lap is a round!
But I can't compare 2 different drivers on 2 different teams, right?

I have an idea!
Instead of comparing the timings directly, we compare relative speed achieved

For proper comparison, across all sectors properly
We describe a term called "Achieved Time".
Basically a **achieved lap time** is the sum of every sector times of a particular team's best.
e.g.

| Drivers       | Sector1 | Sector2 | Sector3 | Lap time | Lap time (seconds) | Score  |
| ------------- | ------- | ------- | ------- | -------- | ------------------ | ------ |
| D1            | 30.000  | 18.000  | 22.000  | 1:10.000 | 70                 | 94.714 |
| D2            | 29.700  | 19.000  | 21.000  | 1:09.700 | 69.7               | 95.121 |
| D1            | 29.300  | 17.200  | 20.300  | 1:06.800 | 66.8               | 99.251 |
| D2            | 29.400  | 17.000  | 20.000  | 1:06.400 | 66.4               | 99.849 |
| Achieved Time | 29.300  | 17.000  | 20.000  | 1:06.300 | 66.3               | 100    |

We will run rounds after every lap, and compare who has the highest *score*.
Remember, the comparison should only be done for the same laps, to counter fuel loads. If you compare a 2nd lap of a race with the last lap, the chances of the last lap being faster is higher because of less fuel load.

Another advantage of this strategy is the weather conditions are similar.
We have 342,820km of f1 racing history or roughly 67,781 laps of racing
If the number of rounds still become a problem, we can compare each sector!
Giving us roughly 203344 rounds to work with. 

Now you might say that a driver's lap time was slower, but they did an overtake!
To that I say, **yes**
Those laps are forgiven

Now you might say, compare those overtakes as well!
But overtakes can be a might more complicated
e.g.
I wouldn't be surprised if an alphine in ultrasofts overtook a mclaren in wets on a dry track

My point is typres, and their ages as well
These things mess the timeline a lot
So either I have to come up with a way of comparing them, or simply ignore them

This is a problem for future me.

## Qualifying
Achieved Time similar to race, but they don't overlap.
Higher score wins, thus we can compare different team drivers as well!

## Pseudocode

### Race
```
driver_scores = []
for lap in race.lap_count:
	for team in teams:
		achieved_time = get_achieved_time(team.race_lap_times())
		driver1_time = lap_time(lap, team.driver1)
		driver2_time = lap_time(lap, team.driver2)
		if get_position_change(driver1) == 0:
			driver_scores[lap][team.driver1] = driver1_time / achieved_time
		if get_position_change(driver2) == 0:
			driver_scores[lap][team.driver2] = driver2_time / achieved_time

	lap_driver_scores = driver_scores[lap]
		for (driver1_data, driver2_data) in combination(lap_driver_scores):
			run_elo_round(driver1_data, driver2_data)
```

## Problems
A driver in dirty air as they are fighting for points will have a lower laptime compared to a team mate behind with clean air who is not fighting for points

## Possible solution
- Put a position based multiplier?
- Compensate for `driver_space`
  > driver_space: How much gap is in front and back

# Second method
## Formula for `driver_space`
`a * <gap-in-front> + b * <gap-in-back>`
for now, i am going to set a=b=1, but in the future I will tune these 2 variables.
If defending is harder, then b > a
If attacking is harder, then a > b

Or something like that.