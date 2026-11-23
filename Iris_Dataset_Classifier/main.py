import argparse
from core.classifier import IrisClassifier
from storage.persistence import RecordStore

def main():
    parser = argparse.ArgumentParser(description="Iris Dataset Classifier Demo")
    parser.add_argument("--cli", action="store_true", help="launch terminal interface")
    args = parser.parse_args()
    model = IrisClassifier()
    store = RecordStore()
    if args.cli:
        from core.cli import run_cli
        run_cli(model, store)
    else:
        try:
            from gui.dashboard import IrisApp
            app = IrisApp(model, store)
            app.mainloop()
        except Exception as exc:
            print(f"GUI could not start: {exc}")
            print("Try: python main.py --cli")

if __name__ == "__main__":
    main()
