from core.classifier import FEATURES

def validate_measurements(values):
    if len(values) != 4:
        raise ValueError("Please provide all four measurements.")
    cleaned = []
    errors = []
    for label, raw in zip(FEATURES, values):
        try:
            value = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{label.replace('_', ' ').title()} must be a number.")
            continue
        if not 0.0 < value <= 10.0:
            errors.append(f"{label.replace('_', ' ').title()} must be greater than 0 and at most 10 cm.")
        cleaned.append(value)
    if errors:
        raise ValueError("\n".join(errors))
    return cleaned
