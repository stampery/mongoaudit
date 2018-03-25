import unittest

from .testers.cve import alerts_dec012015, alerts_mar272015, alerts_mar252015, alerts_feb252015, \
    alerts_jun172014, alerts_may052014, alerts_jun202013, alerts_jun052013, alerts_mar062014, \
    alerts_oct012013, alerts_aug152013


class MongoauditTest(unittest.TestCase):
    @staticmethod
    def create_type(**kwargs):
        return type("mock", (object,), kwargs)

    def info_obj(self, info):
        return self.create_type(tester=self.create_type(info=info))

    def ver_obj(self, ver):
        return self.info_obj({"version": ver})

    def test_alert1(self):
        self.assertFalse(
            alerts_dec012015(self.info_obj({"version": "3.0.3", "modules": ["enterprise"]}))[0])

    def test_alert1_1(self):
        self.assertTrue(alerts_dec012015(self.info_obj({"version": "3.0.2", "modules": ["rock"]})))

    def test_alert2(self):
        self.assertFalse(alerts_mar272015(self.ver_obj("3.0.0"))[0])

    def test_alert3(self):
        self.assertFalse(alerts_mar252015(self.ver_obj("2.4.0"))[0])

    def test_alert4(self):
        self.assertFalse(alerts_feb252015(self.ver_obj("2.6.0"))[0])

    def test_alert5(self):
        self.assertFalse(alerts_jun172014(self.ver_obj("2.6.0"))[0])

    def test_alert6(self):
        self.assertFalse(alerts_may052014(self.ver_obj("2.6.0"))[0])

    def test_alert7(self):
        self.assertFalse(alerts_jun202013(self.ver_obj("2.4.2"))[0])

    def test_alert8(self):
        self.assertFalse(alerts_jun052013(self.ver_obj("2.4.4"))[0])

    def test_alert9(self):
        self.assertFalse(alerts_mar062014(self.ver_obj("2.3.1"))[0])

    def test_alert10(self):
        self.assertFalse(alerts_oct012013(self.ver_obj("2.2.1"))[0])

    def test_alert11(self):
        self.assertFalse(alerts_aug152013(self.ver_obj("2.5.1"))[0])

    
