"""
Variant 1 — Baseline: Center-following + Speed
-----------------------------------------------
Strategy: keep the car near the center line and reward higher speeds.
Simple and interpretable; serves as the control condition for comparison.
"""


def reward_function(params):
    distance_from_center = params["distance_from_center"]
    track_width = params["track_width"]
    speed = params["speed"]
    all_wheels_on_track = params["all_wheels_on_track"]
    is_offtrack = params["is_offtrack"]

    if is_offtrack or not all_wheels_on_track:
        return 1e-3

    # Three concentric bands: tight center gets the highest multiplier
    if distance_from_center <= 0.10 * track_width:
        center_reward = 1.0
    elif distance_from_center <= 0.25 * track_width:
        center_reward = 0.5
    elif distance_from_center <= 0.50 * track_width:
        center_reward = 0.1
    else:
        center_reward = 1e-3

    # Speed bonus: scale linearly between MIN and MAX speed
    MIN_SPEED = 1.0
    MAX_SPEED = 4.0
    speed_reward = (speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
    speed_reward = max(0.0, min(1.0, speed_reward))

    reward = 0.7 * center_reward + 0.3 * speed_reward
    return float(reward)
