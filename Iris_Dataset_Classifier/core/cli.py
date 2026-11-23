from datetime import datetime
from core.validation import validate_measurements
from core.statistics import build_summary
from core.search import search_records
from core.warnings import measurement_warnings
from storage.import_export import import_csv, export_records
from core.classifier import FEATURES, DISPLAY_FEATURES

def ask_measurements():
    raw = [input(f"{name} (cm): ").strip() for name in DISPLAY_FEATURES]
    return validate_measurements(raw)

def run_cli(model, store):
    print("\n" + "="*54 + "\n       IRIS DATASET CLASSIFIER DEMO\n" + "="*54)
    while True:
        print("\n1. New prediction\n2. View records\n3. Search records\n4. Summary\n5. Import CSV\n6. Export reports\n0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                values = ask_measurements()
                result = model.predict(values)
                print(f"\nPrediction: {result['species']} ({result['confidence']:.1%} confidence)")
                for warning in measurement_warnings(values, model.ranges):
                    print("• " + warning)
                record = dict(zip(FEATURES, values))
                record.update(result)
                record["source"] = "Terminal"
                store.add(record)
                print("Record saved.")
            elif choice == "2":
                for r in store.records:
                    print(f"{r.get('id')} | {r.get('species')} | {r.get('created_at','')}")
                if not store.records: print("No records yet.")
            elif choice == "3":
                keyword = input("Keyword (blank for all): ")
                species = input("Species (All/Setosa/Versicolor/Virginica): ").strip().title() or "All"
                if species not in ("All", "Setosa", "Versicolor", "Virginica"): species = "All"
                for r in search_records(store.records, keyword, species):
                    print(f"{r.get('id')} | {r.get('species')} | {r.get('confidence',0):.1%}")
            elif choice == "4":
                s = build_summary(store.records)
                print(f"Total records: {s['total_records']} | Average confidence: {s['average_confidence']:.1%}")
                print("Species counts:", s["species_counts"])
            elif choice == "5":
                path = input("CSV file path: ").strip().strip('"')
                count, errors = import_csv(path, model, store)
                print(f"Imported {count} row(s).")
                for error in errors: print(error)
            elif choice == "6":
                paths = export_records(store.records, "reports")
                print("Created:", *(str(p) for p in paths), sep="\n")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Please choose a listed option.")
        except (ValueError, OSError, FileNotFoundError) as exc:
            print("Could not complete that action:", exc)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
