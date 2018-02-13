import unittest
import gedParser
import datetime

class TestGedParser(unittest.TestCase):

  #US03
  def test_birthBeforeDeath(self):
    today = datetime.datetime.today()
    date2003 = datetime.datetime(2003, 8, 4, 12, 30, 45)
    date1960 = datetime.datetime(1960, 3, 3, 11, 45, 30)

    self.assertEqual(gedParser.birthBeforeDeath('indi', date2003, today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('indi', today, date2003), 1)
    self.assertEqual(gedParser.birthBeforeDeath('indi', date1960, today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('indi', today, date1960), 1)
    self.assertEqual(gedParser.birthBeforeDeath('indi', date1960, date2003), 0)
    self.assertEqual(gedParser.birthBeforeDeath('indi', date2003, date1960), 1)
    self.assertEqual(gedParser.birthBeforeDeath('indi', date2003, "N/A"), 0)
    self.assertEqual(gedParser.birthBeforeDeath('indi', "N/A", today), 0)
    self.assertEqual(gedParser.birthBeforeDeath('indi', "N/A", "N/A"), 0)

  #US06
  def test_divorceBeforeDeath(self):
    today = datetime.datetime.today()
    date1987 = datetime.datetime(1987, 8, 4, 12, 30, 45)
    date1979 = datetime.datetime(1979, 3, 3, 11, 45, 30)
    date1985 = datetime.datetime(1985, 2, 3, 10, 15, 20)

    #divorce after death
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1987, 'husbandId', date1979, 'wifeId', date1985), 1)
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1987, 'husbandId', date1979, 'wifeId', "N/A"), 1)
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1987, 'husbandId', "N/A", 'wifeId', date1979), 1)

    #divorce no death
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1987, 'husbandId', "N/A", 'wifeId', "N/A"), 0)

    #divorce before death
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1979, 'husbandId', date1987, 'wifeId', date1985), 0)
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1979, 'husbandId', "N/A", 'wifeId', date1985), 0)
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1979, 'husbandId', date1987, 'wifeId', "N/A"), 0)
    self.assertEqual(gedParser.divorceBeforeDeath('family', date1979, 'husbandId', "N/A", 'wifeId', "N/A"), 0)

    #didn't divorce
    self.assertEqual(gedParser.divorceBeforeDeath('family', "N/A", 'husbandId', date1979, 'wifeId', date1985), 0)
    self.assertEqual(gedParser.divorceBeforeDeath('family', "N/A", 'husbandId', "N/A", 'wifeId', "N/A"), 0)

if __name__ == '__main__':
    unittest.main()
