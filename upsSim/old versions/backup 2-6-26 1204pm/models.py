import json


class ULD:
    try:
        with open('ULD_SPECS.json', 'r') as f:
            _specs = json.load(f)['uld_types']
    except Exception:
        _specs = {}

    def __init__(self, data):
        self.id = data['uld_id']
        self.type = data['uld_type']
        self.current_weight = data['current_weight']
        self.max_structural_weight = self._specs.get(self.type, {}).get('max_structural_weight', 10000)


class Aircraft:
    def __init__(self, db_row, config):
        self.id = db_row['aircraft_id']
        self.type = db_row['aircraft_type']
        self.location = db_row['current_location']
        self.cruise_speed = db_row['cruise_speed']

        # Physics / Config
        self.uld_layout = config['uld_positions']
        self.fwd_limit = config['balance_constraints']['forward_limit_inches']
        self.aft_limit = config['balance_constraints']['aft_limit_inches']

        self.manifest = {}  # {pos_id: ULD_Object}
        self.empty_weight = 180000
        self.empty_arm = 900

    def calculate_balance(self):
        total_weight = self.empty_weight
        total_moment = self.empty_weight * self.empty_arm

        for pos_id, uld in self.manifest.items():
            arm = self.uld_layout[pos_id]['arm_inches']
            total_weight += uld.current_weight
            total_moment += (uld.current_weight * arm)

        cog = total_moment / total_weight
        is_safe = self.fwd_limit <= cog <= self.aft_limit
        return is_safe, round(cog, 2)