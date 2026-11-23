import csv
from pathlib import Path
from datetime import datetime
from core.validation import validate_measurements
from core.classifier import FEATURES

def import_csv(path, model, store):
    imported, errors = 0, []
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in FEATURES if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("CSV is missing required columns: " + ", ".join(missing))
        for line, row in enumerate(reader, start=2):
            try:
                values = validate_measurements([row.get(k, "") for k in FEATURES])
                prediction = model.predict(values)
                record = dict(zip(FEATURES, values))
                record.update(prediction)
                record["notes"] = row.get("notes", "Imported from CSV")
                record["source"] = "CSV import"
                store.add(record)
                imported += 1
            except Exception as exc:
                errors.append(f"Row {line}: {str(exc).replace(chr(10), '; ')}")
    return imported, errors

def export_records(records, folder, formats=("csv", "md", "txt")):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = []
    if "csv" in formats:
        path = folder / f"iris_report_{stamp}.csv"
        if records:
            fields = list(dict.fromkeys(k for r in records for k in r))
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(records)
        else:
            path.write_text("No records available.\n", encoding="utf-8")
        paths.append(path)
    summary = ["# Iris Classifier Report", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", f"Total records: {len(records)}", ""]
    for i, r in enumerate(records, 1):
        summary.append(f"{i}. **{r.get('species','Unknown')}** | Confidence: {r.get('confidence',0):.1%} | Measurements: " +
                       ", ".join(f"{k.replace('_',' ')}={r.get(k,'')}" for k in ("sepal_length","sepal_width","petal_length","petal_width")))
    if not records:
        summary.append("No records available.")
    if "md" in formats:
        path = folder / f"iris_report_{stamp}.md"
        path.write_text("\n".join(summary), encoding="utf-8")
        paths.append(path)
    if "txt" in formats:
        path = folder / f"iris_report_{stamp}.txt"
        path.write_text("\n".join(x.replace("**", "") for x in summary), encoding="utf-8")
        paths.append(path)
    return paths
