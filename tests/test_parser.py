import unittest
from src.parser import parse_prescriptions

class TestParser(unittest.TestCase):
    def test_parse_prescriptions(self):
        input_str = """Warfarin: once daily (morning)
Ibuprofen: thrice daily
Metformin: twice daily (morning, evening)
"""
        result = parse_prescriptions(input_str)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], "Warfarin")
        self.assertEqual(result[0]['frequency'], 1)
        self.assertIn('morning', result[0]['preferred_times'])
        
        self.assertEqual(result[1]['name'], "Ibuprofen")
        self.assertEqual(result[1]['frequency'], 3)
        self.assertEqual(result[1]['preferred_times'], [])

        self.assertEqual(result[2]['name'], "Metformin")
        self.assertEqual(result[2]['frequency'], 2)
        self.assertEqual(set(result[2]['preferred_times']), set(['morning', 'evening']))

if __name__ == '__main__':
    unittest.main()
