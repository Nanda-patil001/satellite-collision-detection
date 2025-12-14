import math
import matplotlib.pyplot as plt
from sgp4.api import Satrec, jday

# ---------------- CONFIG ----------------
ALERT_DISTANCE = 5.0  # km
file_path = "data/active.txt"

# ---------------- LOAD SATELLITES ----------------
sats = []

with open(file_path) as f:
    lines = f.readlines()

for i in range(0, len(lines), 3):
    name = lines[i].strip()
    l1 = lines[i + 1].strip()
    l2 = lines[i + 2].strip()

    sat = Satrec.twoline2rv(l1, l2)
    sats.append((name, sat))

    if len(sats) == 60:
        break

print("Total satellites loaded:", len(sats))

# ---------------- DISTANCE FUNCTION ----------------
def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2 +
        (p1[2] - p2[2])**2
    )

# ---------------- TEST: FIRST 2 SATELLITES ----------------
sat1_name, sat1 = sats[0]
sat2_name, sat2 = sats[1]

print("\nChecking collision risk for first 2 satellites...\n")

alert_found = False

for t in range(360):  # 1 hour, every 10 seconds
    jd, fr = jday(2024, 1, 1, 0, 0, t * 10)

    e1, p1, _ = sat1.sgp4(jd, fr)
    e2, p2, _ = sat2.sgp4(jd, fr)

    if e1 == 0 and e2 == 0:
        d = distance(p1, p2)

        if d < ALERT_DISTANCE:
            print("⚠️ COLLISION ALERT!")
            print(f"Time: {t * 10} seconds")
            print(f"{sat1_name} & {sat2_name}")
            print(f"Distance: {d:.2f} km")
            alert_found = True
            break

if not alert_found:
    print("✅ No collision risk detected in 1 hour.")
# ---------------- CHECK ALL SATELLITE PAIRS ----------------
print("\n--- Checking collision risk for ALL satellites ---\n")
# ---------------- GRAPH: Distance vs Time (First 2 Satellites) ----------------
times = []
distances = []

for t in range(360):  # 1 hour, every 10 seconds
    jd, fr = jday(2024, 1, 1, 0, 0, t * 10)

    e1, p1, _ = sat1.sgp4(jd, fr)
    e2, p2, _ = sat2.sgp4(jd, fr)

    if e1 == 0 and e2 == 0:
        d = distance(p1, p2)
        times.append(t * 10)
        distances.append(d)

plt.figure()
plt.plot(times, distances)
plt.xlabel("Time (seconds)")
plt.ylabel("Distance (km)")
plt.title(f"Distance Between {sat1_name} and {sat2_name}")
plt.grid(True)
plt.savefig("distance_graph.png")
plt.show()

alerts = []

for i in range(len(sats)):
    for j in range(i + 1, len(sats)):

        sat1_name, sat1 = sats[i]
        sat2_name, sat2 = sats[j]

        # ---- QUICK INITIAL DISTANCE CHECK (OPTIMIZATION) ----
        jd0, fr0 = jday(2024, 1, 1, 0, 0, 0)

        e1_0, p1_0, _ = sat1.sgp4(jd0, fr0)
        e2_0, p2_0, _ = sat2.sgp4(jd0, fr0)

        if e1_0 != 0 or e2_0 != 0:
            continue

        if distance(p1_0, p2_0) > 2000:  # km
            continue

        for t in range(60):  # 1 hour, every 10 seconds
            jd, fr = jday(2024, 1, 1, 0, 0, t * 60)

            e1, p1, _ = sat1.sgp4(jd, fr)
            e2, p2, _ = sat2.sgp4(jd, fr)

            if e1 == 0 and e2 == 0:
                d = distance(p1, p2)

                if d < ALERT_DISTANCE:
                    print("⚠️ COLLISION RISK FOUND!")
                    print(f"{sat1_name} ↔ {sat2_name}")
                    print(f"Time: {t * 60} sec | Distance: {d:.2f} km\n")

                    alerts.append((t * 60, sat1_name, sat2_name, d))
                    break

print(f"Total collision alerts found: {len(alerts)}")
# ---------------- SAVE RESULTS TO FILE ----------------
with open("collision_results.txt", "w") as f:
    f.write("Satellite Collision Detection Results\n")
    f.write("====================================\n\n")

    if len(alerts) == 0:
        f.write("No collision risks detected.\n")
        print("✅ No collision risks detected. Results saved.")
    else:
        for alert in alerts:
            time_sec, s1, s2, dist = alert
            f.write(
                f"Time: {time_sec} sec | {s1} ↔ {s2} | Distance: {dist:.2f} km\n"
            )

        print(f"⚠️ {len(alerts)} collision alerts saved to collision_results.txt")