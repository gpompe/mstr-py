import testtools
import mstr


class TestMSTR(testtools.TestCase):

    def test_mstrobject(self):
        """testing MSTRObject Class"""
        m = {"name": "string", "id": "string", "type": 0, "abbreviation": "string", "description": "string", "hidden": True, "subtype": 0, "extType": 0, "dateCreated": "2017-11-23T15:16:56.589Z", "dateModified": "2017-11-23T15:16:56.589Z", "version": "string", "acg": 0, "iconPath": "string", "viewMedia": 0, "comments": ["Comment 1", "Comment 2"]}

        c = mstr.MSTRObject('FFFFFFFFFFFFFFFFFFFFFFFF', m)
        self.assertEqual(c.ID, "FFFFFFFFFFFFFFFFFFFFFFFF", "Reading porperty ID failed")
        self.assertEqual(c.Name, "string", "Reading porperty Name failed")
        self.assertEqual(c.Type, mstr.EnumDSSObjectType(0), "Reading porperty Type failed")
        self.assertEqual(c.Abbreviation, "string", "Reading porperty Abbreviation failed")
        self.assertEqual(c.Description, "string", "Reading porperty Description failed")
        self.assertEqual(c.Hidden, True, "Reading porperty Hidden failed")
        self.assertEqual(c.Subtype, mstr.EnumDSSSubTypes(0), "Reading porperty Subtype failed")
        self.assertEqual(c.ExtType, 0, "Reading porperty ExtType failed")
        self.assertEqual(c.DateCreated, "2017-11-23T15:16:56.589Z", "Reading porperty DateCreated failed")
        self.assertEqual(c.DateModified, "2017-11-23T15:16:56.589Z", "Reading porperty DateModified failed")
        self.assertEqual(c.Version, "string", "Reading porperty Version failed")
        self.assertEqual(c.Acg, 0, "Reading porperty Acg failed")
        self.assertEqual(c.IconPath, "string", "Reading porperty IconPath failed")
        self.assertEqual(c.ViewMedia, 0, "Reading porperty ViewMedia failed")
        self.assertEqual(c.Comments, ["Comment 1", "Comment 2"], "Reading porperty Comments failed")

        m = {"name": "string", "id": "string", "type": "something invalid", "abbreviation": "string", "description": "string", "hidden": True, "subtype": 0, "extType": 0, "dateCreated": "2017-11-23T15:16:56.589Z", "dateModified": "2017-11-23T15:16:56.589Z", "version": "string", "acg": 0, "iconPath": "string", "viewMedia": 0, "comments": ["Comment 1", "Comment 2"]}

        c = mstr.MSTRObject('FFFFFFFFFFFFFFFFFFFFFFFF', m)
        self.assertEqual(c.Type, None, "Reading porperty Type failed. Should be None")

    def test_mstrattribute(self):
        ''' Testing MSTRAttribute class'''
        m = {"name": "Region", "id": "8D679D4B11D3E4981000E787EC6DE8A4", "type": "Attribute", "forms": [{"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC", "dataType": "Char"}, {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID", "dataType": "Real"}]}
        a = mstr.MSTRAttribute(m["id"], m)
        self.assertEqual(a.ID, "8D679D4B11D3E4981000E787EC6DE8A4", "Reading porperty ID failed")
        self.assertEqual(a.Name, "Region", "Reading porperty Name failed")
        self.assertEqual(a.Type, mstr.EnumDSSObjectType.DSSTYPEATTRIBUTE, "Reading porperty Type failed. Should be None")
        self.assertEqual(a.Forms, [{"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC", "dataType": "Char"}, {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID", "dataType": "Real"}], "Reading porperty Forms failed.")
        self.assertEqual(len(a.Forms), 2, "Error reading Forms length")
        self.assertEqual(a.Forms[0], {"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC", "dataType": "Char"}, "Error reading Forms list elements")
        self.assertEqual(a.Forms[0]["id"], "CCFBE2A5EADB4F50941FB879CCF1721C", "Error reading Forms list elements")

    def test_mstrmetric(self):
        ''' Testing MSTRmetric class'''
        m = {"name": "Discount", "id": "381980B211D40BC8C000C8906B98494F", "type": "Metric","isDerived": "true"}
        a = mstr.MSTRMetric(m["id"], m)
        self.assertEqual(a.ID, "381980B211D40BC8C000C8906B98494F", "Reading porperty ID failed")
        self.assertEqual(a.Name, "Discount", "Reading porperty Name failed")
        self.assertEqual(a.Type, mstr.EnumDSSObjectType.DSSTYPEMETRIC, "Reading porperty Type failed. Should be None")
        self.assertEqual(a.isDerived, True, "Reading porperty isDerived failed")
