import unittest

from app.service import generate_note


class StarterServiceTests(unittest.TestCase):
    def test_returns_basic_fields(self):
        result = generate_note(
            {
                "encounter_id": "test-1",
                "transcript": "The synthetic patient reports poor sleep.",
                "intake": {"diagnosis": "Insomnia"},
                "note_format": "structured",
            }
        )
        self.assertIn("assessment", result)
        self.assertIn("risk", result)
        self.assertIn("model_used", result)

    def test_explicit_denial(self):
        result = generate_note(
            {
                "encounter_id": "test-2",
                "transcript": "The synthetic patient denies current suicidal thoughts.",
                "intake": {},
            }
        )
        self.assertEqual(result["risk"]["current_suicidal_ideation"], "denied")


if __name__ == "__main__":
    unittest.main()
