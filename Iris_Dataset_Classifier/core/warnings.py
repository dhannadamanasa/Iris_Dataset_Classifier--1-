def measurement_warnings(values, ranges):
    warnings = []
    for key, value in zip(ranges, values):
        low, high = ranges[key]
        if value < low or value > high:
            warnings.append(
                f"{key.replace('_', ' ').title()} ({value:g} cm) is outside the Iris training-data range ({low:g}–{high:g} cm)."
            )
    if not warnings:
        warnings.append("All measurements are within the observed Iris dataset ranges.")
    return warnings
