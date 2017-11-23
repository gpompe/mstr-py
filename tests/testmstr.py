import unittest
from unittest.mock import patch, mock_open

import mstr.mstr as mstr


class TestMSTR(unittest.TestCase):
	def setUp(self):
		pass

	def test_mstrobject(self):
		"""testing MSTRObject Class"""
		m = {"name": "string","id": "string","type": 0,"abbreviation": "string","description": "string","hidden": True,"subtype": 0,"extType": 0,"dateCreated": "2017-11-23T15:16:56.589Z","dateModified": "2017-11-23T15:16:56.589Z","version": "string","acg": 0,"iconPath": "string","viewMedia": 0,"comments":["Comment 1","Comment 2"]}

		c = mstr.MSTRObject('FFFFFFFFFFFFFFFFFFFFFFFF',m)
		self.assertEqual(c.ID,"FFFFFFFFFFFFFFFFFFFFFFFF", "Reading porperty ID failed")
		self.assertEqual(c.Name,"string", "Reading porperty Name failed")
		self.assertEqual(c.Type,0, "Reading porperty Type failed")
		self.assertEqual(c.Abbreviation,"string", "Reading porperty Abbreviation failed")
		self.assertEqual(c.Description,"string", "Reading porperty Description failed")
		self.assertEqual(c.Hidden,True, "Reading porperty Hidden failed")
		self.assertEqual(c.Subtype,0, "Reading porperty Subtype failed")
		self.assertEqual(c.ExtType,0, "Reading porperty ExtType failed")
		self.assertEqual(c.DateCreated,"2017-11-23T15:16:56.589Z", "Reading porperty DateCreated failed")
		self.assertEqual(c.DateModified,"2017-11-23T15:16:56.589Z", "Reading porperty DateModified failed")
		self.assertEqual(c.Version,"string", "Reading porperty Version failed")
		self.assertEqual(c.Acg,0, "Reading porperty Acg failed")
		self.assertEqual(c.IconPath,"string", "Reading porperty IconPath failed")
		self.assertEqual(c.ViewMedia,0, "Reading porperty ViewMedia failed")
		self.assertEqual(c.Comments,["Comment 1","Comment 2"], "Reading porperty Comments failed")