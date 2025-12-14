from sgp4.api import Satrec, jday
import math

file_path = "data/active.txt"

sats = []

with open(file_path) as f:
    lines = f.readlines()

for i in range(0, len(lines), 3):
    name = lines[i].strip()
    l1 = lines[i+1].strip()
    l2 = lines[i+2].strip()

    sat = Satrec.twoline2rv(l1, l2)
    sats.append((name, sat))

    if len(sats) == 60:
        break

print("Total satellites:", len(sats))
# simulate for 1 hour (every 10 seconds)
time_steps = 360   # 360 × 10 sec = 1 hour
step_sec = 10

for t in range(time_steps):
    jd, fr = jday(2024, 1, 1, 0, 0, t * step_sec)

    for name, sat in sats:
        error, position, velocity = sat.sgp4(jd, fr)

        if error == 0:
            x, y, z = position
            print(f"{name}: x={x:.2f}, y={y:.2f}, z={z:.2f}")

    print("-" * 40)
def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2 +
        (p1[2] - p2[2])**2
    )
print("\nChecking distance between first 2 satellites...\n")

sat1_name, sat1 = sats[0]
sat2_name, sat2 = sats[1]

for t in range(10):   # only 10 steps for testing
    jd, fr = jday(2024, 1, 1, 0, 0, t * 10)

    e1, p1, _ = sat1.sgp4(jd, fr)
    e2, p2, _ = sat2.sgp4(jd, fr)

    if e1 == 0 and e2 == 0:
        d = distance(p1, p2)
        print(f"Time {t*10}s | Distance between {sat1_name} & {sat2_name} = {d:.2f} km")
ALERT_DISTANCE = 5.0  # km
alert_found = False

print("\n--- Collision Risk Check (First 2 Satellites) ---\n")

for t in range(360):  # 1 hour, every 10 seconds
    jd, fr = jday(2024, 1, 1, 0, 0, t * 10)

    e1, p1, _ = sat1.sgp4(jd, fr)
    e2, p2, _ = sat2.sgp4(jd, fr)

    if e1 == 0 and e2 == 0:
        d = distance(p1, p2)

        if d < ALERT_DISTANCE:
            print(f"⚠️ ALERT at t={t*10}s!")
            print(f"{sat1_name} & {sat2_name}")
            print(f"Distance = {d:.2f} km\n")
            alert_found = True
            break

if not alert_found:
    print("✅ No collision risk detected in 1 hour.")
with open("collision_results.txt", "w") as f:
    f.write("Satellite Collision Analysis Results\n")
    f.write("==================================\n\n")

    if len(alerts) == 0:
        f.write("No collision risks detected.\n")
    else:
        for alert in alerts:
            time, sat1, sat2, dist = alert
            f.write(f"Time: {time}s | {sat1} - {sat2} | Distance: {dist:.2f} km\n")