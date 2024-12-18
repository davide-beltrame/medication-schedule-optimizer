import sys
import os

# Aggiungi il percorso assoluto della cartella principale al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import parse_prescriptions
import unittest

class TestParserInput(unittest.TestCase):
    def test_sample_input(self):
        input_str = """Aspirin: once daily (morning)
Ibuprofen: twice daily
Diet: breakfast 8 am; lunch 1 pm; dinner 8 pm
"""
        prescriptions, diet = parse_prescriptions(input_str)
        self.assertEqual(len(prescriptions), 2)
        self.assertEqual(prescriptions[0]['name'].title(), "Aspirin")
        self.assertEqual(prescriptions[0]['frequency'], 1)
        self.assertIn('morning', prescriptions[0]['preferred_times'])

        self.assertEqual(prescriptions[1]['name'].title(), "Ibuprofen")
        self.assertEqual(prescriptions[1]['frequency'], 2)
        self.assertEqual(prescriptions[1]['preferred_times'], [])

        self.assertIn('breakfast', diet)
        self.assertIn('lunch', diet)
        self.assertIn('dinner', diet)
        # Just a basic test to confirm parsing works as intended

if __name__ == '__main__':
    unittest.main()
