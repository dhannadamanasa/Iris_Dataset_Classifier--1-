# Iris Dataset Classifier Demo

A beginner-friendly desktop application and terminal program for classifying Iris flowers with a Random Forest model.

## Features
- Modern Tkinter desktop dashboard with Dashboard, New Prediction, Records and Analytics pages
- Iris classification using scikit-learn's built-in Iris dataset (no dataset download required)
- Defensive validation for blank, non-numeric and out-of-range measurements
- JSON and CSV local persistence
- Keyword/species search and category filtering
- Summary metrics and Matplotlib visualizations
- Measurement warnings for unusual values and dataset-boundary values
- Bulk CSV import with row-by-row error reporting
- Export reports to CSV, Markdown and plain text
- Menu-driven terminal interface
- Graceful handling of missing/corrupted storage files

## Requirements
- Python 3.10+
- Tkinter (usually included with Python; on some Linux distributions install `python3-tk`)

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

## Run the GUI
```bash
python main.py
```

## Run the terminal interface
```bash
python main.py --cli
```

## Input fields
- Sepal length (cm)
- Sepal width (cm)
- Petal length (cm)
- Petal width (cm)

The application predicts one of: setosa, versicolor, virginica.

## CSV import format
The first row must contain these columns:
`sepal_length,sepal_width,petal_length,petal_width`

Optional columns: `species`, `notes`. Imported rows are validated individually. Valid rows are classified and saved; invalid rows are listed in the import result.

## Local data
Application records are stored in `data/records.json` and `data/records.csv`.
These files are created automatically. Existing files are not overwritten during startup.

## Project layout
- `main.py`: application entry point
- `core/`: classifier, validation, summaries, search and warnings
- `storage/`: persistence and import/export
- `gui/`: Tkinter interface and charts
- `utils/`: shared helpers
- `reports/`: exported reports

## Notes
The model is trained locally from scikit-learn's built-in Iris dataset. It does not send flower measurements to a server. The warning indicators are data-quality guidance, not medical or scientific certification.
