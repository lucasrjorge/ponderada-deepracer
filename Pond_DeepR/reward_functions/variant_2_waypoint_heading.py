"""
Variant 2 — Waypoint Heading + Smooth Steering
-----------------------------------------------
Strategy: reward the agent for pointing toward the next waypoint AND for
keeping steering smooth. This teaches the car to anticipate curves instead
of reacting late, and discourages zig-zagging that wastes speed.

Key differences from Variant 1:
  - Heading alignment term replaces the pure center-band logic
  - Steering penalty discourages sharp / oscillating inputs
  - Speed is only rewarded when the heading is already good
"""

import math


def reward_function(params):
    x = params["x"]
    y = params["y"]
    heading = params["heading"]
    waypoints = params["waypoints"]
    closest_waypoints = params["closest_waypoints"]
    steering_angle = params["steering_angle"]
    speed = params["speed"]
    distance_from_center = params["distance_from_center"]
    track_width = params["track_width"]
    all_wheels_on_track = params["all_wheels_on_track"]
    is_offtrack = params["is_offtrack"]

    if is_offtrack or not all_wheels_on_track:
        return 1e-3

    # --- 1. Heading reward ---
    # Direction from current position toward the next waypoint
    next_wp = waypoints[closest_waypoints[1]]
    dx = next_wp[0] - x
    dy = next_wp[1] - y
    target_heading = math.degrees(math.atan2(dy, dx))

    heading_error = abs(target_heading - heading)
    if heading_error > 180:
        heading_error = 360 - heading_error

    # Smooth cosine falloff: perfect alignment = 1.0, 30° off = ~0.75, 90° off = 0
    heading_reward = math.cos(math.radians(heading_error))
    heading_reward = max(0.0, heading_reward)

    # --- 2. Steering smoothness penalty ---
    # Large absolute steering angle ↔ sharp turn or oscillation
    ABS_STEERING_THRESHOLD = 15.0  # degrees
    if abs(steering_angle) > ABS_STEERING_THRESHOLD:
        steering_penalty = 0.5
    else:
        steering_penalty = 1.0

    # --- 3. Speed reward (only meaningful when heading is good) ---
    MIN_SPEED = 1.0
    MAX_SPEED = 4.0
    speed_reward = (speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
    speed_reward = max(0.0, min(1.0, speed_reward))
    # Gate speed reward on heading quality so the agent doesn't rush into corners
    speed_reward *= heading_reward

    # --- 4. Center-line safety net ---
    if distance_from_center <= 0.30 * track_width:
        center_reward = 1.0
    elif distance_from_center <= 0.50 * track_width:
        center_reward = 0.3
    else:
        center_reward = 1e-3

    reward = (
        0.40 * heading_reward
        + 0.25 * speed_reward
        + 0.20 * center_reward
        + 0.15 * steering_penalty
    )
    return float(reward)
