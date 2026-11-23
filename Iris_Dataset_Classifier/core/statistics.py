from collections import Counter
from statistics import mean

def build_summary(records):
    counts = Counter(r.get("species", "Unknown") for r in records)
    result = {
        "total_records": len(records),
        "species_counts": dict(counts),
        "average_confidence": mean([r.get("confidence", 0) for r in records]) if records else 0.0,
    }
    for field in ("sepal_length", "sepal_width", "petal_length", "petal_width"):
        vals = [float(r[field]) for r in records if r.get(field) is not None]
        result[field + "_average"] = mean(vals) if vals else None
    return result
