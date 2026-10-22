# Vehicle ML Django Dashboard

A complete local Django implementation of `Vehicle_ML_Django_Dashboard_Tutorial.pdf`. The original tutorial text is saved in `tutorial_extracted.txt`.

## Run on Windows

Python 3.12 or later is recommended. From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ . Stop the server with Ctrl+C.

If Django and pandas are already installed, use `python manage.py runserver` directly. The tutorial template loads Bootstrap from a CDN, so internet access is needed for its styling.

## Dashboard template

The home page renders `vehicles/templates/vehicles/dashboard.html` using the HTML shown in Part 7 of the PDF. The PDF names the path `index.html` but also calls it `dashboard.html`; this project uses the requested `dashboard.html` filename.

The page follows the tutorial's Bootstrap 5.3.2 layout: sidebar navigation, an 80vh scrollable content panel, blue heading, and manufacturer frequency table in an info-colored card. Bootstrap CSS and JavaScript load from the same jsDelivr CDN specified in the PDF, requiring internet access for Bootstrap styling and behavior. Metadata for responsive rendering and a dataset-error message are included.

The manufacturer table counts records from your CSV. A responsive Plotly.js bar chart below it displays the same manufacturer counts, with hover details, zoom, and image download. Plotly.js 4.1.1 loads from its CDN and requires internet access; the table remains available if the chart library cannot load. No Python Plotly package is required. The previous custom overview is retained in `index.html` as an unused template. Backend filtering, sorting, and pagination remain available through query parameters; their controls and the additional charts are not part of the PDF template. Filtered CSV export remains available at `/export/`.

No trained ML model or prediction workflow is defined in the PDF.

## Dataset

`vehicles_ml_dataset (1).csv` is the active source: 10,000 records and 22 original columns. It is read directly from the project root on each request. The former synthetic dataset is no longer used.

The data layer maps `selling_price` to price, `kilometers_driven` to mileage, and `body_type` to the display alias previously used in the explorer. The PDF template displays manufacturer counts only. Currency is not specified by the source, so prices have no currency symbol. Generated IDs (`ROW-00001`, etc.) identify one-based CSV data row positions; the file provides no vehicle IDs or model names.

One record (ROW-00003) has `active` in `kilometers_driven`. The data layer treats invalid mileage as missing and excludes it from any mileage average. It does not affect manufacturer counts. The record stays in totals, filters, tables, and exports. Some other fields in that row also appear inconsistent; the source file is preserved without guessing corrections.

Filtered CSV exports retain all 22 original columns and values, including client fields, without the internal display aliases or generated row IDs. Spreadsheet formula-like text is escaped for export. The original file is never rewritten.

Required source columns are `manufacturer`, `body_type`, `year`, `fuel_type`, `transmission`, `kilometers_driven`, and `selling_price`. Year and selling price must be finite, nonnegative numbers. Invalid or missing mileage is allowed and reported. Other source columns are preserved for export. No upload or record editing is provided because the tutorial uses a local file.

## Validate

```powershell
python manage.py check
python manage.py test
```

The generated Django settings use local development defaults (`DEBUG=True`). Configure a private secret key, allowed hosts, static serving, and production security settings before any public deployment. The optional `/admin/` route requires a user created with `python manage.py createsuperuser`; the CSV is not a database model.
