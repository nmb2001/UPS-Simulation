import math


def calculate_balance(aircraft_config, manifest):
    """
    Validates if the loaded manifest is safe based on CoG limits.
    Updated to use 'current_weight' to match your ULD database schema.
    """
    total_weight = 0
    total_moment = 0

    # Basic Operating Weight (Empty Weight) of the aircraft
    empty_weight = 180000
    empty_arm = 900  # The balance point of the plane with no cargo

    total_weight += empty_weight
    total_moment += (empty_weight * empty_arm)

    for item in manifest:
        pos_id = item['pos']
        # Updated from 'weight' to 'current_weight' to match your ULD DB columns
        weight = item['current_weight']
        can_type = item.get('type')  # Get the ULD type (e.g., 'AAD')

        # 1. Check if the position exists in the aircraft configuration
        if pos_id not in aircraft_config['uld_positions']:
            print(f"CRITICAL ERROR: Position {pos_id} is not valid for this aircraft!")
            return False, 0

        pos_data = aircraft_config['uld_positions'][pos_id]

        # 2. TYPE VALIDATION: Check if the ULD type is allowed in this position
        allowed_types = pos_data.get('allowed_cans', [])
        if can_type not in allowed_types:
            print(f"CRITICAL ERROR: {can_type} is not allowed in position {pos_id}!")
            print(f"Allowed types for {pos_id} are: {allowed_types}")
            return False, 0

        # 3. Pull the 'arm' from JSON and update totals
        arm = pos_data['arm_inches']
        total_weight += weight
        total_moment += (weight * arm)

    # The Golden Formula: Total Moment / Total Weight = Center of Gravity
    center_of_gravity = total_moment / total_weight

    # Check against Forward and Aft limits
    fwd_limit = aircraft_config['balance_constraints']['forward_limit_inches']
    aft_limit = aircraft_config['balance_constraints']['aft_limit_inches']

    is_safe = fwd_limit <= center_of_gravity <= aft_limit

    return is_safe, round(center_of_gravity, 2)


def calculate_flight_time(origin, destination, cruise_speed):
    """
    Calculates flight duration based on distance and aircraft speed.
    """
    # Coordinates for airports i pulled online
    coords = {
        'SDF': (38.1, -85.7),
        'ATL': (33.6, -84.4),
        'ORD': (41.9, -87.9),
        'LAX': (33.9, -118.4)
    }

    if origin not in coords or destination not in coords:
        return 2.0  # Default 2 hour flight if airports unknown

    lat1, lon1 = coords[origin]
    lat2, lon2 = coords[destination]

    # Calculate distance (I am not the best at math, but it works for this simple simulation!)
    distance = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 60

    # Time = Distance / Speed
    return distance / (cruise_speed if cruise_speed > 0 else 450)