import json
import os
import tempfile
import unittest
from unittest.mock import patch

from feedback import prompt_feedback, _load, _save


class TestPromptFeedback(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)  # remove so _load treats it as empty

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def _run(self, inputs):
        with patch('builtins.input', side_effect=inputs):
            return prompt_feedback('test_script', feedback_file=self.tmp.name)

    def test_valid_rating_no_comment(self):
        entry = self._run(['4', ''])
        self.assertIsNotNone(entry)
        self.assertEqual(entry['rating'], 4)
        self.assertEqual(entry['comment'], '')
        self.assertEqual(entry['script'], 'test_script')

    def test_valid_rating_with_comment(self):
        entry = self._run(['5', 'Great script!'])
        self.assertEqual(entry['rating'], 5)
        self.assertEqual(entry['comment'], 'Great script!')

    def test_skip_on_empty_input(self):
        entry = self._run([''])
        self.assertIsNone(entry)
        self.assertFalse(os.path.exists(self.tmp.name))

    def test_invalid_rating_string(self):
        entry = self._run(['abc', ''])
        self.assertIsNone(entry)

    def test_rating_out_of_range(self):
        entry = self._run(['6', ''])
        self.assertIsNone(entry)

    def test_rating_zero(self):
        entry = self._run(['0', ''])
        self.assertIsNone(entry)

    def test_feedback_saved_to_file(self):
        self._run(['3', 'okay'])
        records = _load(self.tmp.name)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['rating'], 3)

    def test_multiple_entries_appended(self):
        self._run(['1', 'bad'])
        self._run(['5', 'great'])
        records = _load(self.tmp.name)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['rating'], 1)
        self.assertEqual(records[1]['rating'], 5)

    def test_entry_has_timestamp(self):
        entry = self._run(['3', ''])
        self.assertIn('timestamp', entry)
        self.assertTrue(len(entry['timestamp']) > 0)


if __name__ == '__main__':
    unittest.main()
