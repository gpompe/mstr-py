import testtools
import mstr


class TestMSTR(testtools.TestCase):

    def test_mstrobject(self):
        """testing MSTRObject Class"""
        m = {"name": "string", "id": "string", "type": 0, "abbreviation": "string", "description": "string",
             "hidden": True, "subtype": 0, "extType": 0, "dateCreated": "2017-11-23T15:16:56.589Z",
             "dateModified": "2017-11-23T15:16:56.589Z", "version": "string", "acg": 0, "iconPath": "string",
             "viewMedia": 0, "comments": ["Comment 1", "Comment 2"]}

        c = mstr.MSTRObject('FFFFFFFFFFFFFFFFFFFFFFFF', m)
        self.assertEqual(c.ID, "FFFFFFFFFFFFFFFFFFFFFFFF", "Reading property ID failed")
        self.assertEqual(c.Name, "string", "Reading property Name failed")
        self.assertEqual(c.Type, mstr.EnumDSSObjectType(0), "Reading property Type failed")
        self.assertEqual(c.Abbreviation, "string", "Reading property Abbreviation failed")
        self.assertEqual(c.Description, "string", "Reading property Description failed")
        self.assertEqual(c.Hidden, True, "Reading property Hidden failed")
        self.assertEqual(c.Subtype, mstr.EnumDSSSubTypes(0), "Reading property Subtype failed")
        self.assertEqual(c.ExtType, 0, "Reading property ExtType failed")
        self.assertEqual(c.DateCreated, "2017-11-23T15:16:56.589Z", "Reading property DateCreated failed")
        self.assertEqual(c.DateModified, "2017-11-23T15:16:56.589Z", "Reading property DateModified failed")
        self.assertEqual(c.Version, "string", "Reading property Version failed")
        self.assertEqual(c.Acg, 0, "Reading property Acg failed")
        self.assertEqual(c.IconPath, "string", "Reading property IconPath failed")
        self.assertEqual(c.ViewMedia, 0, "Reading property ViewMedia failed")
        self.assertEqual(c.Comments, ["Comment 1", "Comment 2"], "Reading property Comments failed")

        m = {"name": "string", "id": "string", "type": "something invalid", "abbreviation": "string",
             "description": "string", "hidden": True, "subtype": 0, "extType": 0,
             "dateCreated": "2017-11-23T15:16:56.589Z", "dateModified": "2017-11-23T15:16:56.589Z", "version": "string",
             "acg": 0, "iconPath": "string", "viewMedia": 0, "comments": ["Comment 1", "Comment 2"]}

        c = mstr.MSTRObject('FFFFFFFFFFFFFFFFFFFFFFFF', m)
        self.assertEqual(c.Type, None, "Reading property Type failed. Should be None")

    def test_mstrattribute(self):
        """ Testing MSTRAttribute class"""
        m = {"name": "Region", "id": "8D679D4B11D3E4981000E787EC6DE8A4", "type": "Attribute",
             "forms": [{"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC", "dataType": "Char"},
                       {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID", "dataType": "Real"}]}
        a = mstr.MSTRAttribute(m["id"], m)
        self.assertEqual(a.ID, "8D679D4B11D3E4981000E787EC6DE8A4", "Reading property ID failed")
        self.assertEqual(a.Name, "Region", "Reading property Name failed")
        self.assertEqual(a.Type, mstr.EnumDSSObjectType.DSSTYPEATTRIBUTE,
                         "Reading property Type failed. Should be None")
        self.assertEqual(a.todict(), {"type": "attribute", "id": "8D679D4B11D3E4981000E787EC6DE8A4", "name": "Region"},
                         "Error converting to dict")
        self.assertEqual(len(a.Forms), 2, "Error reading Forms length")
        self.assertEqual(a.Forms["DESC"].ID, "CCFBE2A5EADB4F50941FB879CCF1721C", "Error reading Forms list elements")
        self.assertEqual(a.Forms["DESC"].Name, "DESC", "Error reading Forms list elements")
        self.assertEqual(a.Forms["DESC"].todict(), {"type": "form",
                                                    "attribute": {"id": "8D679D4B11D3E4981000E787EC6DE8A4",
                                                                  "name": "Region"},
                                                    "form": {"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC"}},
                         "Error reading Forms list elements")

    def test_mstrmetric(self):
        """ Testing MSTRmetric class"""
        m = {"name": "Discount", "id": "381980B211D40BC8C000C8906B98494F", "type": "Metric", "isDerived": "true"}
        a = mstr.MSTRMetric(m["id"], m)
        self.assertEqual(a.ID, "381980B211D40BC8C000C8906B98494F", "Reading property ID failed")
        self.assertEqual(a.Name, "Discount", "Reading property Name failed")
        self.assertEqual(a.Type, mstr.EnumDSSObjectType.DSSTYPEMETRIC, "Reading property Type failed. Should be None")
        self.assertEqual(a.isDerived, True, "Reading property isDerived failed")

    def test_mstrconstant(self):
        """ Testing MSTRConstant class"""
        m = mstr.MSTRConstant(3)
        self.assertEqual(m.todict(), {"type": "constant", "dataType": "Char", "value": "3"},
                         "Reading property ID failed")

    def test_mstroperator(self):
        """ Testing MSTROperator class
        """

        m = mstr.MSTROperatorEquals()

        self.assertEqual(m.Expression, "Equals", "Reading operator expression failed")

    def test_mstrviewfilter(self):
        """ Testing MSTRViewFilter class
        """
        d = {"name": "Region", "id": "8D679D4B11D3E4981000E787EC6DE8A4", "type": "Attribute",
             "forms": [{"id": "CCFBE2A5EADB4F50941FB879CCF1721C", "name": "DESC", "dataType": "Char"},
                       {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID", "dataType": "Real"}]}
        a = mstr.MSTRAttribute(d["id"], d)

        explist = ['(', a.Forms["ID"], mstr.MSTROperatorEquals(),mstr.MSTRConstant(1, 'Real'), ')']

        m = mstr.MSTRViewFiler(explist)

        self.assertEqual(m.todict(), {"viewFilter": {"operator": "Equals", "operands": [{
            "type": "form",
            "attribute": {"id": "8D679D4B11D3E4981000E787EC6DE8A4", "name": "Region"},
            "form": {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID"},
        }, {
            "type": "constant", "dataType": "Real", "value": "1"
        }]}}, "Reading dict expression failed")

        explist = ['(', mstr.MSTROperatorNot(), '(', a.Forms["ID"], mstr.MSTROperatorEquals(),
                   mstr.MSTRConstant(1, 'Real'), ')', ')']

        m = mstr.MSTRViewFiler(explist)

        self.assertEqual(m.todict(), {"viewFilter": {"operator": "Not", "operands": [
            {"operator": "Equals", "operands": [{
            "type": "form",
            "attribute": {"id": "8D679D4B11D3E4981000E787EC6DE8A4", "name": "Region"},
            "form": {"id": "45C11FA478E745FEA08D781CEA190FE5", "name": "ID"},
        }, {
            "type": "constant", "dataType": "Real", "value": "1"
        }]}]}}, "Reading dict expression failed")