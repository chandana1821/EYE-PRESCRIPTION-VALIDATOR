"""Standalone Eye Prescription Validator Flask application."""
from decimal import Decimal, InvalidOperation
import math
import re

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

FIELDS = {
    "od_sph": ("Right Eye SPH", Decimal("-20"), Decimal("20"), True),
    "od_cyl": ("Right Eye CYL", Decimal("-10"), Decimal("10"), True),
    "od_axis": ("Right Eye Axis", Decimal("0"), Decimal("180"), False),
    "os_sph": ("Left Eye SPH", Decimal("-20"), Decimal("20"), True),
    "os_cyl": ("Left Eye CYL", Decimal("-10"), Decimal("10"), True),
    "os_axis": ("Left Eye Axis", Decimal("0"), Decimal("180"), False),
}
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")


def validate_prescription(data):
    """Validate a mapping of six prescription fields; return values and errors."""
    errors = {}
    normalized = {}
    if not isinstance(data, dict):
        return {}, {key: f"{label} is required." for key, (label, *_rest) in FIELDS.items()}

    for key, (label, minimum, maximum, quarter_steps) in FIELDS.items():
        raw = data.get(key)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            errors[key] = f"{label} is required."
            continue

        # Accept only scalar numeric values or numeric strings; disallow bools and arrays.
        if isinstance(raw, bool) or not isinstance(raw, (str, int, float, Decimal)):
            errors[key] = f"{label} must be numeric." if quarter_steps else "Axis must be a whole number."
            continue
        string_value = str(raw).strip()
        if not NUMERIC_RE.fullmatch(string_value):
            errors[key] = f"{label} must be numeric." if quarter_steps else "Axis must be a whole number."
            continue
        try:
            value = Decimal(string_value)
        except InvalidOperation:
            errors[key] = f"{label} must be numeric." if quarter_steps else "Axis must be a whole number."
            continue
        if not value.is_finite():
            errors[key] = f"{label} must be numeric." if quarter_steps else "Axis must be a whole number."
            continue
        if value < minimum or value > maximum:
            errors[key] = f"{label} is outside the permitted range."
            continue
        # Manual hardening: check quarter steps from the exact rational value.
        # Decimal multiplication can round very long fractions at the active
        # context precision, incorrectly accepting a value just off a 0.25 step.
        numerator, denominator = value.as_integer_ratio()
        if quarter_steps and (numerator * 4) % denominator != 0:
            errors[key] = f"{label} must be in increments of 0.25."
            continue
        if not quarter_steps and value != value.to_integral_value():
            errors[key] = "Axis must be a whole number."
            continue
        normalized[key] = int(value) if not quarter_steps else float(value)

    return normalized, errors


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/validate")
def validate():
    if request.is_json:
        try:
            data = request.get_json(silent=False)
        except Exception:
            return jsonify({"success": False, "errors": {"_request": "Malformed JSON request."}}), 400
    else:
        data = request.form.to_dict()

    values, errors = validate_prescription(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400
    return jsonify({"success": True, "prescription": values})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
