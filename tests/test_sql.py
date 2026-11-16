"""Verify the executable SQL on boundary-month and NULL-community fixtures."""
import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / 'sql'

class SQLTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript('''CREATE TABLE crimes (
          year INTEGER, month INTEGER, primary_type TEXT, arrest INTEGER,
          community_area INTEGER, weekday INTEGER, hour INTEGER, season TEXT);
          INSERT INTO crimes VALUES
          (2025,10,'THEFT',1,25,0,12,'Autumn'),
          (2025,11,'THEFT',0,NULL,1,13,'Autumn'),
          (2026,10,'BATTERY',0,25,2,14,'Autumn');''')

    def tearDown(self):
        self.db.close()

    def query(self, name):
        return self.db.execute((SQL / (name + '.sql')).read_text(),
            {'comparison_months':10,'last_year':2026}).fetchall()

    def test_equal_month_cutoff(self):
        self.assertEqual(self.query('annual'), [(2025,1,1),(2026,1,0)])
        self.assertEqual(len(self.query('category_year')),2)
        self.assertEqual(len(self.query('monthly')),3)

    def test_null_geography_and_arrest_denominator(self):
        rows = self.query('areas')
        self.assertEqual(sum(r[1] for r in rows),3)
        self.assertEqual(next(r for r in rows if r[0] == 25),(25,2,1,0.5))
        self.assertEqual(next(r for r in rows if r[0] is None),(None,1,0,0.0))
        theft=next(r for r in self.query('categories') if r[0]=='THEFT')
        self.assertEqual(theft,('THEFT',2,1,0.5))

    def test_complete_year_season_and_time(self):
        self.assertEqual(self.query('season'),[('Autumn',2)])
        self.assertEqual(sum(r[2] for r in self.query('time')),3)

if __name__ == '__main__':
    unittest.main()
