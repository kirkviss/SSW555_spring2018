import unittest
import gedParser
import datetime

class TestGedParser(unittest.TestCase):

  def test_birthBeforeDeath(self):
    today = datetime.datetime.today()
    date2003 = datetime.datetime(2003, 8, 4, 12, 30, 45)
    date1960 = datetime.datetime(1960, 3, 3, 11, 45, 30)

    self.assertEqual(gedParser.birthBeforeDeath('key', date2003, today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('key', today, date2003), 1)
    self.assertEqual(gedParser.birthBeforeDeath('key', date1960, today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('key', today, date1960), 1)
    self.assertEqual(gedParser.birthBeforeDeath('key', date1960, date2003), 0)
    self.assertEqual(gedParser.birthBeforeDeath('key', date2003, date1960), 1)
    self.assertEqual(gedParser.birthBeforeDeath('key', date2003, "N/A"), 0)
    self.assertEqual(gedParser.birthBeforeDeath('key', "N/A", today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('key', "N/A", "N/A"), 0)

if __name__ == '__main__':
    unittest.main()