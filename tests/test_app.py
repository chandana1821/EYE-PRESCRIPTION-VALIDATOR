import json
import unittest

from app import app, validate_prescription


VALID = {"od_sph": "-2.00", "od_cyl": "-0.75", "od_axis": "90", "os_sph": "-1.50", "os_cyl": "-0.50", "os_axis": "75"}


class PrescriptionTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_valid_prescription(self):
        normalized, errors = validate_prescription(VALID)
        self.assertEqual(errors, {})
        self.assertEqual(normalized["od_axis"], 90)

    def test_sph_out_of_range(self):
        data = VALID | {"od_sph": "20.25"}
        self.assertIn("permitted range", validate_prescription(data)[1]["od_sph"])

    def test_cyl_out_of_range(self):
        data = VALID | {"os_cyl": "-10.25"}
        self.assertIn("permitted range", validate_prescription(data)[1]["os_cyl"])

    def test_invalid_axis(self):
        for axis in ("181", "-1", "90.5"):
            self.assertIn("os_axis", validate_prescription(VALID | {"os_axis": axis})[1])

    def test_empty_submission(self):
        response = self.client.post("/validate", data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json["errors"]), 6)

    def test_missing_fields(self):
        data = VALID.copy(); del data["od_sph"]
        self.assertIn("required", validate_prescription(data)[1]["od_sph"])

    def test_non_numeric(self):
        self.assertIn("numeric", validate_prescription(VALID | {"od_sph": "oops"})[1]["od_sph"])

    def test_incorrect_quarter_step(self):
        self.assertIn("increments", validate_prescription(VALID | {"os_sph": "1.10"})[1]["os_sph"])

    def test_malformed_json(self):
        response = self.client.post("/validate", data='{"od_sph":', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("_request", response.json["errors"])

    def test_multiple_invalid_fields(self):
        data = VALID | {"od_sph": "21", "od_axis": "181", "os_cyl": "0.1"}
        _, errors = validate_prescription(data)
        self.assertEqual(set(errors), {"od_sph", "od_axis", "os_cyl"})

    def test_extreme_and_nonfinite_values(self):
        _, errors = validate_prescription(VALID | {"od_sph": "9" * 1000, "os_cyl": "NaN"})
        self.assertIn("od_sph", errors)
        self.assertIn("os_cyl", errors)


if __name__ == "__main__":
    unittest.main()
