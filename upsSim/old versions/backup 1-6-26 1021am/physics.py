def calculate_balance(aircraft_config, manifest):
    """
    aircraft_config: The dictionary for the specific plane from your JSON
    manifest: A list of dicts like {'pos': '1L', 'weight': 4500, 'type': 'AAY'}
    """
    total_weight = 0
    total_moment = 0

    # Basic Operating Weight (Empty Weight) of the aircraft
    # In a production environment, these would come from the aircraft_config JSON
    empty_weight = 180000
    empty_arm = 900  # The balance point of the plane with no cargo

    total_weight += empty_weight
    total_moment += (empty_weight * empty_arm)

    for item in manifest:
        pos_id = item['pos']
        weight = item['weight']
        can_type = item.get('type') # Get the ULD type (e.g., 'AAD')

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