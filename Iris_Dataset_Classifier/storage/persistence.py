import csv
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

class RecordStore:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.json_path = DATA_DIR / "records.json"
        self.csv_path = DATA_DIR / "records.csv"
        self.records = self.load()

    def load(self):
        if not self.json_path.exists():
            return []
        try:
            with self.json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            backup = DATA_DIR / "records_corrupt_backup.json"
            try:
                self.json_path.replace(backup)
            except OSError:
                pass
            return []

    def save(self):
        temp = self.json_path.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2, ensure_ascii=False)
        temp.replace(self.json_path)
        self.write_csv()

    def add(self, record):
        item = dict(record)
        item.setdefault("id", f"IR-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
        item.setdefault("created_at", datetime.now().astimezone().isoformat(timespec="seconds"))
        self.records.append(item)
        self.save()
        return item

    def write_csv(self):
        if not self.records:
            return
        fields = list(dict.fromkeys(k for r in self.records for k in r.keys()))
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(self.records)
