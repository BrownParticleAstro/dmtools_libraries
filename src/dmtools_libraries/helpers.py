unit_factors = {
    'eV': 1e0,
    'keV': 1e3,
    'MeV': 1e6,
    'GeV': 1e9,
    'TeV': 1e12
}

def normalize_unit(unit):
    # Remove '/c^2', '/c2', '/c²', etc. and whitespace
    unit = unit.strip()
    if '/c' in unit:
        unit = unit.split('/c')[0]
    return unit

def convert_mass_units(value, from_unit, to_unit):
    """
    Convert a mass value (or array) from one energy/c^2 unit to another.
    from_unit and to_unit can be like 'GeV', 'GeV/c^2', 'MeV/c2', etc.
    """
    from_unit_norm = normalize_unit(from_unit)
    to_unit_norm = normalize_unit(to_unit)
    # print("convert_mass_units : from ", from_unit_norm, " to ", to_unit_norm)
    if from_unit_norm not in unit_factors or to_unit_norm not in unit_factors:
        raise ValueError(f"Supported units: {list(unit_factors.keys())}")
    try:
        value_eV = value * unit_factors[from_unit_norm]
        result = value_eV / unit_factors[to_unit_norm]
    except:
        result = 0
    return result

allowed_units = ['eV', 'keV', 'MeV', 'GeV', 'TeV']

def get_x_label(selected_unit):
    selected_unit = normalize_unit(selected_unit)
    if selected_unit not in allowed_units:
        #raise ValueError(f"Unit must be one of: {allowed_units}")
        selected_unit = 'GeV'  # Default to GeV if invalid unit is provided
    return r"$\mathrm{DM\ Mass}\ [\mathrm{" + selected_unit + r"}/c^{2}]$"
