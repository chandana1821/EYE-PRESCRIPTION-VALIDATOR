# Eye Prescription Validator

A small standalone Flask application for checking right and left eye SPH, CYL, and Axis values. It does not use a database; validation is performed on the server using decimal arithmetic.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Validate and test

```powershell
python -m unittest discover -s tests -v
```

The `POST /validate` endpoint accepts either form data or JSON with `od_sph`, `od_cyl`, `od_axis`, `os_sph`, `os_cyl`, and `os_axis`. Success returns a normalized `prescription` object; invalid input returns HTTP 400 and a field-keyed `errors` object. SPH is limited to −20..20, CYL to −10..10, both in quarter-diopter increments, and Axis to whole degrees 0..180.

This utility checks numeric ranges and formatting only. Confirm prescriptions with a licensed eye care professional.
