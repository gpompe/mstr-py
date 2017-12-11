from enum import IntEnum
from numbers import Number


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self) -> object:
        return self.items.pop()

    def lookback(self, n=1):
        if len(self.items) - n < 0:
            return None
        else:
            return self.items[len(self.items) - n]

    def size(self):
        return len(self.items)


class BinaryTree:
    """
    A recursive implementation of Binary Tree
    Using links and Nodes approach.
    Modified to allow for trees to be constructed from other trees rather than always creating
    a new tree in the insertLeft or insertRight
    """

    def __init__(self, rootObj):
        self.key = rootObj
        self.leftChild = None
        self.rightChild = None

    def insertLeft(self, newNode):

        if isinstance(newNode, BinaryTree):
            t = newNode
        else:
            t = BinaryTree(newNode)

        self.leftChild = t

    def insertRight(self, newNode):
        if isinstance(newNode, BinaryTree):
            t = newNode
        else:
            t = BinaryTree(newNode)

        self.rightChild = t

    def isLeaf(self):
        return (not self.leftChild) and (not self.rightChild)

    def getRightChild(self):
        return self.rightChild

    def getLeftChild(self):
        return self.leftChild

    def setRootVal(self, obj):
        self.key = obj

    def getRootVal(self, ):
        return self.key


    def todict(self):
        if self.isLeaf():
            return self.key.todict()
        else:
            operands = []
            if self.leftChild is not None:
                operands.append(self.leftChild.todict())
            if self.rightChild is not None:
                operands.append(self.rightChild.todict())
            return dict(operator=self.key, operands=operands)



class MSTRConstant:
    """ Represents a constant in MSTR
        The available typer are: Date, Time, TimeStamp, Real, Char
    """
    _value = None
    _dataType = None

    def __init__(self, rootObj, dataType=None):
        self._value = rootObj
        self._dataType = self._detectdatatype(dataType)

    def _detectdatatype(self, dataType=None):
        if dataType is None:
            if isinstance(dataType, Number):
                return 'Real'
            else:
                return 'Char'   # TODO: logic to detect Date and Datetime type needs to be implemented
        else:
            return dataType

    @property
    def _tomstrstr(self):
        return str(self._value)

    def todict(self):
        return dict(type="constant", dataType=self._dataType, value=self._tomstrstr)


class MSTROperator:
    _symbols = None
    _expression = None
    _arity = 2
    
    def __init__(self, symbol, expression, arity=2):
        # super(MSTROperator, self).__init__(symbol)
        self._symbols = symbol
        self._expression = expression
        self._arity = arity

    @property
    def Expression(self):
        return self._expression

    # def todict(self,leftChild=None,rightChild=None):
    #     operands = []
    #     if leftChild is not None:
    #         operands.append(leftChild.todict())
    #     if rightChild is not None:
    #         operands.append(rightChild.todict())
    #     return dict(operator=self._expression, operands=operands)


class MSTRUnaryOperator(MSTROperator):

    def __init__(self, symbol, expression):
        super(MSTRUnaryOperator, self).__init__(symbol, expression, 1)


class MSTRBinaryOperator(MSTROperator):

    def __init__(self, symbol, expression):
        super(MSTRBinaryOperator, self).__init__(symbol, expression, )


class MSTROperatorBeginsWith(MSTRBinaryOperator):
    
    def __init__(self, symbol='bw'):
        super(MSTROperatorBeginsWith, self).__init__(symbol, 'BeginsWith')


class MSTROperatorEquals(MSTRBinaryOperator):

    def __init__(self, symbol='=='):
        super(MSTROperatorEquals, self).__init__(symbol, 'Equals')


class MSTROperatorContains(MSTRBinaryOperator):

    def __init__(self, symbol='cn'):
        super(MSTROperatorContains, self).__init__(symbol, 'Contains')


class MSTROperatorEndsWith(MSTRBinaryOperator):

    def __init__(self, symbol='ew'):
        super(MSTROperatorEndsWith, self).__init__(symbol, 'EndsWith')


class MSTROperatorGreater(MSTRBinaryOperator):

    def __init__(self, symbol='>'):
        super(MSTROperatorGreater, self).__init__(symbol, 'Greater')


class MSTROperatorGreaterEqual(MSTRBinaryOperator):

    def __init__(self, symbol='>='):
        super(MSTROperatorGreaterEqual, self).__init__(symbol, 'GreaterEqual')


class MSTROperatorLessEqual(MSTRBinaryOperator):

    def __init__(self, symbol='<='):
        super(MSTROperatorLessEqual, self).__init__(symbol, 'LessEqual')


class MSTROperatorLess(MSTRBinaryOperator):

    def __init__(self, symbol='<'):
        super(MSTROperatorLess, self).__init__(symbol, 'Less')


class MSTROperatorLike(MSTRBinaryOperator):

    def __init__(self, symbol='lk'):
        super(MSTROperatorLike, self).__init__(symbol, 'Like')


class MSTROperatorNotBeginsWith(MSTRBinaryOperator):

    def __init__(self, symbol='!bw'):
        super(MSTROperatorNotBeginsWith, self).__init__(symbol, 'NotBeginsWith')


class MSTROperatorNotContains(MSTRBinaryOperator):

    def __init__(self, symbol='!cn'):
        super(MSTROperatorNotContains, self).__init__(symbol, 'NotContains')


class MSTROperatorNotEndsWith(MSTRBinaryOperator):

    def __init__(self, symbol='!ew'):
        super(MSTROperatorNotEndsWith, self).__init__(symbol, 'NotEndsWith')


class MSTROperatorNotEquals(MSTRBinaryOperator):

    def __init__(self, symbol='!='):
        super(MSTROperatorNotEquals, self).__init__(symbol, 'NotEquals')


class MSTROperatorNotLike(MSTRBinaryOperator):

    def __init__(self, symbol='!lk'):
        super(MSTROperatorNotLike, self).__init__(symbol, 'NotLike')


class MSTROperatorAnd(MSTRBinaryOperator):

    def __init__(self, symbol='and'):
        super(MSTROperatorAnd, self).__init__(symbol, 'And')


class MSTROperatorOr(MSTRBinaryOperator):

    def __init__(self, symbol='or'):
        super(MSTROperatorOr, self).__init__(symbol, 'Or')


class MSTROperatorNot(MSTRUnaryOperator):

    def __init__(self, symbol='not'):
        super(MSTROperatorNot, self).__init__(symbol, 'Not')


class BaseMSTREnum(IntEnum):

    @property
    def prefix(self):
        return ""

    @classmethod
    def searchName(cls, searchString):
        localElem = None
        for x in cls:
            if x.prefix.upper() + searchString.upper() == x.name:
                localElem = x
                break

        return localElem

    def __str__(self):
        return "{0}: {1} ({2})".format(self.name, self.value, hex(self.value))


class EnumDssXmlSearchType(BaseMSTREnum):

    @property
    def prefix(self):
        return "DSSXMLSEARCHTYPE"

    DSSXMLSEARCHTYPEBEGINWITH = 1
    DSSXMLSEARCHTYPEBEGINWITHPHRASE = 3
    DSSXMLSEARCHTYPECONTAINS = 4
    DSSXMLSEARCHTYPECONTAINSANYWORD = 0
    DSSXMLSEARCHTYPEENDWIDTH = 5
    DSSXMLSEARCHTYPEEXACTLY = 2
    DSSXMLSEARCHTYPENOTUSED = -1


class EnumDSSObjectType(BaseMSTREnum):

    @property
    def prefix(self):
        return "DSSTYPE"

    DSSTYPEUNKNOWN = -1
    DSSTYPERESERVED = 0
    DSSTYPEFILTER = 1
    DSSTYPETEMPLATE = 2

    DSSTYPEREPORTDEFINITION = 3
    DSSTYPEMETRIC = 4
    DSSTYPESTYLE = 6
    DSSTYPEAGGMETRIC = 7

    DSSTYPEFOLDER = 8
    DSSTYPEDEVICE = 9
    DSSTYPEPROMPT = 10
    DSSTYPEFUNCTION = 11

    DSSTYPEATTRIBUTE = 12
    DSSTYPEFACT = 13
    DSSTYPEDIMENSION = 14
    DSSTYPETABLE = 15

    DSSTYPEDATAMARTREPORT = 16
    DSSTYPEFACTGROUP = 17
    DSSTYPESHORTCUT = 18
    DSSTYPERESOLUTION = 19

    DSSTYPEMONITOR = 20
    DSSTYPEATTRIBUTEFORM = 21
    DSSTYPESCHEMA = 22
    DSSTYPEFORMAT = 23

    DSSTYPECATALOG = 24
    DSSTYPECATALOGDEFN = 25
    DSSTYPECOLUMN = 26
    DSSTYPEPROPERTYGROUP = 27

    DSSTYPEPROPERTYSET = 28
    DSSTYPEDBROLE = 29
    DSSTYPEDBLOGIN = 30
    DSSTYPEDBCONNECTION = 31

    DSSTYPEPROJECT = 32
    DSSTYPESERVERDEF = 33
    DSSTYPEUSER = 34
    DSSTYPETRANSMITTER = 35

    DSSTYPECONFIGURATION = 36
    DSSTYPEREQUEST = 37
    DSSTYPESCRIPT = 38
    DSSTYPESEARCH = 39

    DSSTYPESEARCHFOLDER = 40
    DSSTYPEDATAMART = 41
    DSSTYPEFUNCTIONPACKAGEDEFINITION = 42
    DSSTYPEROLE = 43

    DSSTYPESECURITYROLE = 44
    DSSTYPELOCALE = 45
    DSSTYPECONSOLIDATION = 47
    DSSTYPECONSOLIDATIONELEMENT = 48

    DSSTYPESCHEDULEEVENT = 49
    DSSTYPESCHEDULEOBJECT = 50
    DSSTYPESCHEDULETRIGGER = 51
    DSSTYPELINK = 52

    DSSTYPEDBTABLE = 53
    DSSTYPETABLESOURCE = 54
    DSSTYPEDOCUMENTDEFINITION = 55
    DSSTYPEDRILLMAP = 56

    DSSTYPEDBMS = 57
    DSSTYPEMDSECURITYFILTER = 58
    DSSTYPEPROMPTANSWER = 59
    DSSTYPEPROMPTANSWERS = 60

    DSSTYPEGRAPHSTYLE = 61
    DSSTYPECHANGEJOURNALSEARCH = 62
    DSSTYPEBLOB = 63
    DSSTYPEDASHBOARDTEMPLATE = 64

    DSSTYPEFLAG = 65
    DSSTYPECHANGEJOURNAL = 66
    DSSTYPEEXTERNALSHORTCUT = 67
    DSSTYPEEXTERNALSHORTCUTTARGET = 68

    DSSTYPERECONCILIATION = 69
    DSSTYPELAYER = 70
    DSSTYPEPALETTE = 71
    DSSTYPETHRESHOLDS = 72

    DSSTYPEPERSONALVIEW = 73
    DSSTYPEFEATUREFLAG = 74
    DSSTYPEBOOKMARK = 75
    DSSTYPENCSOBJECTS = 0xFF

    DSSTYPERESERVEDLASTONE = 76


class EnumDSSSubTypes(BaseMSTREnum):

    @property
    def prefix(self):
        return "DSSSUBTYPE"

    DSSSUBTYPEUNKNOWN = -1
    DSSSUBTYPERESERVED = 0
    DSSSUBTYPEFILTER = 0x0100
    DSSSUBTYPECUSTOMGROUP = 0x0101

    DSSSUBTYPEFILTERPARTITION = 0x0102
    DSSSUBTYPESEGMENT = 0x0103
    DSSSUBTYPETEMPLATE = 0x0200
    DSSSUBTYPEREPORTGRID = 0x0300

    DSSSUBTYPEREPORTGRAPH = 0x0301
    DSSSUBTYPEREPORTENGINE = 0x0302
    DSSSUBTYPEREPORTTEXT = 0x0303
    DSSSUBTYPEREPORTDATAMART = 0x0304

    DSSSUBTYPEREPORTBASE = 0x0305
    DSSSUBTYPEREPORTGRIDANDGRAPH = 0x0306
    DSSSUBTYPEREPORTNONINTERACTIVE = 0x0307
    DSSSUBTYPEREPORTCUBE = 0x0308

    DSSSUBTYPEREPORTINCREMENTREFRESH = 0x0309
    DSSSUBTYPEREPORTTRANSACTION = 0x030A
    DSSSUBTYPEREPORTEMMACUBE = 0x030B
    DSSSUBTYPEREPORTEMMACUBEIRR = 0x030C

    DSSSUBTYPEMETRIC = 0x0400
    DSSSUBTYPESUBTOTALDEFINITION = 0x0401
    DSSSUBTYPESYSTEMSUBTOTAL = 0x0402
    DSSSUBTYPEMETRICDMX = 0x0403

    DSSSUBTYPEMETRICTRAINING = 0x0404
    DSSSUBTYPEMETRICEXTREME = 0x0405
    DSSSUBTYPEMETRICREFERENCELINE = 0x0406
    DSSSUBTYPEMETRICRELATIONSHIP = 0x0407

    DSSSUBTYPESTYLE = 0x0600
    DSSSUBTYPEAGGMETRIC = 0x0700
    DSSSUBTYPEFOLDER = 0x0800
    DSSSUBTYPEFOLDERSYSTEM = 0x0801

    DSSSUBTYPEDEVICE = 0x0900
    DSSSUBTYPEPROMPT = 0x0A00
    DSSSUBTYPEPROMPTBOOLEAN = 0x0A01
    DSSSUBTYPEPROMPTLONG = 0x0A02

    DSSSUBTYPEPROMPTSTRING = 0x0A03
    DSSSUBTYPEPROMPTDOUBLE = 0x0A04
    DSSSUBTYPEPROMPTDATE = 0x0A05
    DSSSUBTYPEPROMPTOBJECTS = 0x0A06

    DSSSUBTYPEPROMPTELEMENTS = 0x0A07
    DSSSUBTYPEPROMPTEXPRESSION = 0x0A08
    DSSSUBTYPEPROMPTEXPRESSIONDRAFT = 0x0A09
    DSSSUBTYPEPROMPTDIMTY = 0x0A0A

    DSSSUBTYPEPROMPTBIGDECIMAL = 0x0A0B
    DSSSUBTYPEFUNCTION = 0x0B00
    DSSSUBTYPEFUNCTIONTHIRDPARTY = 0x0B01
    DSSSUBTYPEATTRIBUTE = 0x0C00

    DSSSUBTYPEATTRIBUTEROLE = 0x0C01
    DSSSUBTYPEATTRIBUTETRANSFORMATION = 0x0C02
    DSSSUBTYPEATTRIBUTEABSTRACT = 0x0C03
    DSSSUBTYPEATTRIBUTERECURSIVE = 0x0C04

    DSSSUBTYPEATTRIBUTEDERIVED = 0x0C05
    DSSSUBTYPEFACT = 0x0D00
    DSSSUBTYPEDIMENSIONSYSTEM = 0x0E00
    DSSSUBTYPEDIMENSIONUSER = 0x0E01

    DSSSUBTYPEDIMENSIONORDERED = 0x0E02
    DSSSUBTYPEDIMENSIONUSERHIERARCHY = 0x0E03
    DSSSUBTYPETABLE = 0x0F00
    DSSSUBTYPETABLEPARTITIONMD = 0x0F01

    DSSSUBTYPETABLEPARTITIONWH = 0x0F02
    DSSSUBTYPEDATAMARTREPORT = 0x1000
    DSSSUBTYPEFACTGROUP = 0x1100
    DSSSUBTYPESHORTCUT = 0x1200

    DSSSUBTYPESHORTCUTWEAKREF = 0x1201
    DSSSUBTYPERESOLUTION = 0x1300
    DSSSUBTYPEATTRIBUTEFORM = 0x1500
    DSSSUBTYPEFORMSYSTEM = 0x1501

    DSSSUBTYPEFORMNORMAL = 0x1502
    DSSSUBTYPESCHEMA = 0x1600
    DSSSUBTYPEFORMAT = 0x1700
    DSSSUBTYPECATALOG = 0x1800

    DSSSUBTYPECATALOGDEFN = 0x1900
    DSSSUBTYPECOLUMN = 0x1A00
    DSSSUBTYPECOLUMNNORMAL = 0x1A01
    DSSSUBTYPECOLUMNCUSTOM = 0x1A02

    DSSSUBTYPEPROPERTYGROUP = 0x1B00
    DSSSUBTYPEPROPERTYSET = 0x1C00
    DSSSUBTYPEDBROLE = 0x1D00
    DSSSUBTYPEDBROLEDATAIMPORT = 0x1D01

    DSSSUBTYPEDBROLEDATAIMPORTPRIMARY = 0x1D02
    DSSSUBTYPEDBROLEOAUTH = 0x1D03
    DSSSUBTYPEDBROLEREMOTEDATASOURCE = 0x1D04
    DSSSUBTYPEDBROLEURLAUTH = 0x1D05

    DSSSUBTYPEDBROLEGENERICDATACONNECTOR = 0x1D06
    DSSSUBTYPEDBLOGIN = 0x1E00
    DSSSUBTYPEDBCONNECTION = 0x1F00
    DSSSUBTYPEPROJECT = 0x2000

    DSSSUBTYPESERVERDEF = 0x2100
    DSSSUBTYPEUSER = 0x2200
    DSSSUBTYPEUSERGROUP = 0x2201
    DSSSUBTYPETRANSMITTER = 0x2300

    DSSSUBTYPECONFIGURATION = 0x2400
    DSSSUBTYPEREQUEST = 0x2500
    DSSSUBTYPESEARCH = 0x2700
    DSSSUBTYPEINDEXEDSEARCH = 0x2701

    DSSSUBTYPERELATIONSHIPSEARCH = 0x2702
    DSSSUBTYPESEARCHFOLDER = 0x2800
    DSSSUBTYPESEARCHFOLDERCROSSPROJECT = 0x2801
    DSSSUBTYPEDATAMART = 0x2900

    DSSSUBTYPEFUNCTIONPACKAGEDEFINITION = 0x2A00
    DSSSUBTYPEROLE = 0x2B00
    DSSSUBTYPEROLETRANSFORMATION = 0x2B01
    DSSSUBTYPESECURITYROLE = 0x2C00

    DSSSUBTYPELOCALE = 0x2D00
    DSSSUBTYPECONSOLIDATION = 0x2F00
    DSSSUBTYPECONSOLIDATIONDERIVED = 0x2F01
    DSSSUBTYPECONSOLIDATIONELEMENT = 0x3000

    DSSSUBTYPESCHEDULEEVENT = 0x3100
    DSSSUBTYPESCHEDULEOBJECT = 0x3200
    DSSSUBTYPESCHEDULETRIGGER = 0x3300
    DSSSUBTYPELINK = 0x3400

    DSSSUBTYPEDBTABLE = 0x3500
    DSSSUBTYPEDBTABLEPMT = 0x3501
    DSSSUBTYPETABLESOURCE = 0x3600
    DSSSUBTYPEDOCUMENTDEFINITION = 0x3700

    DSSSUBTYPEREPORTWRITINGDOCUMENT = 0x3701
    DSSSUBTYPEDOCUMENTTHEME = 0x3702
    DSSSUBTYPEDOSSIER = 0x3703
    DSSSUBTYPEDRILLMAP = 0x3800

    DSSSUBTYPEDBMS = 0x3900
    DSSSUBTYPEMDSECURITYFILTER = 0x3A00
    DSSSUBTYPEMONITORPERFORMANCE = 0x3B00
    DSSSUBTYPEMONITORJOBS = 0x3B01

    DSSSUBTYPEMONITORUSERCONNECTIONS = 0x3B02
    DSSSUBTYPEMONITORDBCONNECTIONS = 0x3B03
    DSSSUBTYPEPROMPTANSWER = 0x3B80
    DSSSUBTYPEPROMPTANSWERBOOLEAN = 0x3B81

    DSSSUBTYPEPROMPTANSWERLONG = 0x3B82
    DSSSUBTYPEPROMPTANSWERSTRING = 0x3B83
    DSSSUBTYPEPROMPTANSWERDOUBLE = 0x3B84
    DSSSUBTYPEPROMPTANSWERDATE = 0x3B85

    DSSSUBTYPEPROMPTANSWEROBJECTS = 0x3B86
    DSSSUBTYPEPROMPTANSWERELEMENTS = 0x3B87
    DSSSUBTYPEPROMPTANSWEREXPRESSION = 0x3B88
    DSSSUBTYPEPROMPTANSWEREXPRESSIONDRAFT = 0x3B89

    DSSSUBTYPEPROMPTANSWERDIMTY = 0x3B8A
    DSSSUBTYPEPROMPTANSWERBIGDECIMAL = 0x3B8B
    DSSSUBTYPEPROMPTANSWERINT64 = 0x3B8C
    DSSSUBTYPEPROMPTANSWERS = 0x3C00

    DSSSUBTYPEGRAPHSTYLE = 0x3D00
    DSSSUBTYPECHANGEJOURNALSEARCH = 0x3E00
    DSSSUBTYPEBLOBUNKNOWN = 0x3F00
    DSSSUBTYPEBLOBOTHER = 0x3F01

    DSSSUBTYPEBLOBIMAGE = 0x3F02
    DSSSUBTYPEBLOBPROJECTPACKAGE = 0x3F03
    DSSSUBTYPEBLOBEXCEL = 0x3F04
    DSSSUBTYPEBLOBHTMLTEMPLATE = 0x3F05

    DSSSUBTYPEDASHBOARDTEMPLATE = 0x4000
    DSSSUBTYPEFLAG = 0x4100
    DSSSUBTYPECHANGEJOURNAL = 0x4200
    DSSSUBTYPEEXTERNALSHORTCUTUNKNOWN = 0x4300

    DSSSUBTYPEEXTERNALSHORTCUTURL = 0x4301
    DSSSUBTYPEEXTERNALSHORTCUTSNAPSHOT = 0x4302
    DSSSUBTYPEEXTERNALSHORTCUTTARGET = 0x4400
    DSSSUBTYPERECONCILIATION = 0x4500

    DSSSUBTYPEPALETTESYSTEM = 0x4600
    DSSSUBTYPEPALETTECUSTOM = 0x4601
    DSSSUBTYPETHRESHOLDS = 0x4800
    DSSSUBTYPESUBSCRIPTIONADDRESS = 0xFF01

    DSSSUBTYPESUBSCRIPTIONCONTACT = 0xFF02
    DSSSUBTYPESUBSCRIPTIONINSTANCE = 0xFF03
