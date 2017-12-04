import requests
import logging as log
from datetime import datetime
from urllib.parse import urljoin
import re
import json
import mstr.mstrenum as enum
from mstr.helpers import BinaryTree, Stack


class MSTRSession:
    """  This class manages the MSTR session and is the entry point to MSTR
        Limitations: Standard authentication only, does not handle session expire date
    """

    # Constants
    ContentType = "application/json"  # To be added in each request as a request header
    # Configuration
    REQ_TIMEOUT = 30  # Requests timeout      TODO: Add to configuration
    TOKEN_LIFE = 300  # Time between token validations in seconds TODO: Add to configuration

    # Properties
    @property
    def isValid(self):
        """  Check if the session is valid
            The check is local now, but probably needs to be remote and cached. Local unless # of secs passed
            since last remote check
            Use /sessions remote method
        """
        if self._authToken.isValid:
            if self._authToken.validFor > self.TOKEN_LIFE:
                req = self.request('GET', urljoin(self._mstr_url, "sessions"), raiseError=False)
                if req.status_code == 204:
                    self._authToken.validate()
                else:
                    # self.open(self._user, self._passw,autoload=False)
                    self._valid = False
        else:
            # self.open(self._user, self._passw,autoload=False)
            self._valid = False

        return self._valid

    @property
    def AuthToken(self):
        return self._authToken

    @staticmethod
    def getProjectHeader(pMstrProjectId):
        return ({"X-MSTR-ProjectID": pMstrProjectId}
                if pMstrProjectId is not None and re.fullmatch("^[A-Z0-9]{32}$", pMstrProjectId, re.IGNORECASE) else {})

    @property
    def projectCount(self):
        return len(self._projects)

    def __init__(self, mstr_api_url, username=None, userpassword=None, autoopen=True, autoload=True):
        """ MSTRSession Constructor
            mstr_api_url: full URL for MicroStrategy API (ex. https://demo.microstrategy.com/MicroStrategyLibrary/api/)
        """
        log.debug("MSTR Session creation for %s", username)
        # Add final slash in case is missing, double slash is handled by the urljoin
        self._mstr_url = mstr_api_url + '/'
        self._user = username
        self._passw = userpassword

        # Initialize private fields
        # Create web Session
        self._session = requests.Session()
        # Add default headers to the session
        self._session.headers.update(
            {"ContentType": MSTRSession.ContentType, "Accept": MSTRSession.ContentType})  # Default Headers
        self._valid = False
        # Create token struct
        self._authToken = AuthorizationToken()
        # Project List
        self._projects = []
        # Default Project
        self.currentProject = None

        if autoopen and self._user is not None and self._passw is not None:
            self.open(self._user, self._passw, autoload)
        log.debug("MSTR Session created for %s", self._user)

    def open(self, username, userpassword, autoload=True):
        """  Open a connection to MSTR Server and get the list of projects available for the user"""
        log.debug("MSTR Session opening for %s", username)
        self._user = username
        self._passw = userpassword

        # JSON Body Open Session
        open_body = {"username": self._user,
                     "password": self._passw,
                     "loginMode": 1}
        try:
            # Get the authentication token
            req = self.request('POST', urljoin(self._mstr_url, "auth/login"), {}, open_body)
            self._authToken.token = req.headers['X-MSTR-AuthToken']
            # Add the auth token to the session headers to be included in all future requests
            self._session.headers.update({"X-MSTR-AuthToken": self._authToken.token} if self._authToken.isValid else {})
            # Make the session valid
            self._valid = True
            if autoload:
                # Only use projects with Status = Active (0)
                self._projects = [elem for elem in self.getProjectList() if elem['status'] == 0]
        except MSTRError:
            raise
        except KeyError as e:
            log.error("X-MSTR-AuthToken does not exist in the the header. %s", e)
            raise MSTRError("X-MSTR-AuthToken does not exist in the the header.", e)

        log.debug("MSTR Session created for %s", self._user)

    def close(self):
        """  Close MSTR Session
        """
        log.debug("MSTR Session closing for %s", self._user)
        if self.isValid:

            self.request('POST', urljoin(self._mstr_url, "auth/logout"))
            self._valid = False

            log.debug("MSTR Session closed for %s", self._user)
        else:
            log.debug("MSTR Session closing failed. Invalid session for %s", self._user)

    def getProjectList(self):
        """  Get the list of projects available for the session"""
        log.debug("MSTR Session Project List for %s", self._user)
        if self.isValid:

            r = self.request('GET', urljoin(self._mstr_url, "projects"))

            log.debug("MSTR Session Project List for %s", self._user)
            return list(r.json())
        else:
            log.debug("MSTR Session Project List failed. Invalid session for %s", self._user)
            return None

    def getObjectInformation(self, pMstrObject, pMstrProjectId=None):
        """  Get information for an specific object"""
        log.debug("MSTR Session Object Info for %s", self._user)
        if self.isValid:

            r = self.request('GET', urljoin(self._mstr_url, "objects") + "/" + pMstrObject.ID,
                             pHeaders=self.getProjectHeader(pMstrProjectId), pParams={"type": pMstrObject.Type.value})

            log.debug("MSTR Session Object Info for %s", self._user)
            pMstrObject.update(r.json())
            return pMstrObject
        else:
            log.debug("MSTR Session Object Info failed. Invalid session for %s", self._user)
            return None

    def searchForProject(self, pProject):
        """ 
        Searches for project in ID, Alias and Name (in this order until find first ocurrence)
        Need to check if multiple IS ar connected
        """
        log.debug("MSTR Session Default Project searching for %s", pProject)
        # Search by ID
        _lcurProject = next((elem for elem in self._projects if elem['id'] == pProject), None)
        log.debug("MSTR Session Default Project searched by ID = %s", _lcurProject)

        if _lcurProject == None:
            # Search by Alias if there is an alias for the project
            _lcurProject = next(
                (elem for elem in self._projects if elem['alias'] == pProject and len(elem['alias']) > 0), None)
            log.debug("MSTR Session Default Project searched by Alias = %s", _lcurProject)

        if _lcurProject == None:
            # Search by Name
            _lcurProject = next((elem for elem in self._projects if elem['name'] == pProject), None)
            log.debug("MSTR Session Default Project searched by Name = %s", _lcurProject)

        return _lcurProject

    def quickSearchProject(self, pSearchString=None, pRootFolderId=None,
                           pSearchType=enum.EnumDssXmlSearchType.DSSXMLSEARCHTYPECONTAINS,
                           pObjectTypes=[enum.EnumDSSObjectType.DSSTYPEREPORTDEFINITION], pMstrProjectId=None):
        """  Get the list of projects available for the session"""
        log.debug("MSTR Session Quick Search for %s", self._user)
        if self.isValid:
            payload = {"pattern": pSearchType.value, "getAncestors": True}
            if pSearchString is not None:
                payload.update({"name": str(pSearchString)})

            if pRootFolderId is not None:
                payload.update({"root": str(pRootFolderId)})

            if isinstance(pObjectTypes, list):
                payload.update({"type": list(map((lambda x: x.value), pObjectTypes))})

            r = self.request('GET', urljoin(self._mstr_url, "searches/results"),
                             pHeaders=self.getProjectHeader(pMstrProjectId), pParams=payload)

            log.debug("MSTR Session Quick Search for %s", self._user)
            return MSTRSearchResults(r.json())
        else:
            log.debug("MSTR Session Quick Search failed. Invalid session for %s", self._user)
            return None

    def setDefaultProject(self, pProject):
        """  Set the default project to be used if none is selected.
        """
        # Try to set the current project
        self.currentProject = self.searchForProject(pProject)

        # If there is a current project, set the header globally
        if self.currentProject is not None:
            self._session.headers.update(self.getProjectHeader(self.currentProject["id"]))
            log.debug("MSTR Session Set Header Project ID = %s", self.currentProject["id"])

    def getDatasetDefinition(self, pMstrObject, pMstrProjectId=None):
        """  Get Object definition from metadata
             Reports
             DssSubTypeReportGrid = 0x0300 = 768, DssSubTypeReportGraph = 0x0301, DssSubTypeReportEngine = 0x0302, DssSubTypeReportText = 0x0303,
             DssSubTypeReportGridAndGraph = 0x0306, DssSubTypeReportNonInteractive = 0x0307,

             Cubes
             DssSubTypeReportCube = 0x0308 = 776

        """
        log.debug("MSTR Session Dataset Definition for %s", self._user)
        if self.isValid:

            if pMstrObject.Subtype == enum.EnumDSSSubTypes.DSSSUBTYPEREPORTCUBE:
                _lmethod = "cubes"
            else:
                _lmethod = "reports"
            try:
                r = self.request('GET', urljoin(self._mstr_url, _lmethod + "/" + pMstrObject.ID),
                                 pHeaders=self.getProjectHeader(pMstrProjectId))

                log.debug("MSTR Session Dataset Definition for %s", self._user)
                return MSTRDatasetDefinition(r.json())
            except MSTRError as err:
                log.debug("MSTR Session Dataset Definition failed. HTTP Error: %s", err)
                return None
        else:
            log.debug("MSTR Session Dataset Definition failed. Invalid session for %s", self._user)
            return None

    def request(self, pVerb, pURL, pHeaders={}, pBody=None, pParams={}, raiseError=True):
        """  Runs request request        """
        try:
            log.debug("Session Headers: %s", self._session.headers)
            log.debug("Request Headers: %s", pHeaders)
            log.debug("Request Content: %s", pBody)
            r = self._session.request(method=pVerb, url=pURL, headers=pHeaders, timeout=MSTRSession.REQ_TIMEOUT,
                                      json=pBody, params=pParams)
            # r.raise_for_status()
            log.info("Open session Status code:" + str(r.status_code))
            log.debug("Response Headers: %s", r.headers)
            log.debug("Response Content: %s", r.content)

            if (r.status_code < 200 or r.status_code >= 300) and raiseError:
                raise MSTRError(pjson=r.json())
        except ValueError as err:
            log.error(err)
            raise
        except requests.exceptions.RequestException as e:
            raise MSTRError("Details: %s" % r.text, e)

        return r


class MSTRObjDefinition:

    def __init__(self, pJsonObjDefinition):
        self._json = pJsonObjDefinition

    def __str__(self):
        return json.dumps(self._json)


class MSTRDatasetResults(MSTRObjDefinition):
    """  Parses the JSON object into a dataset result
        TODO: This class is imcomplete
    """
    _attributes = []
    _metrics = []

    def __init__(self, pJsonObjDefinition):
        super(MSTRDatasetDefinition, self).__init__(pJsonObjDefinition)
        # print(pJsonObjDefinition)
        try:
            pass
        except KeyError as e:
            log.error("Error parsing objects dataset definition")
            raise MSTRError(msg="Error parsing dataset definition", original_exception=e)

    def getQueryResults(self, pJsonObjDefinition):
        def getChildrenResults(pchildren, attrNames=[], pbase=[], pparent={}):
            """ Recursive function to normalize the results """

            for x in pchildren:

                # Get attribute definition. Removes the key attributeForms for the initial version. Might be needed later...
                t = {(attrNames[x["element"]["attributeIndex"]] if len(attrNames) > x["element"][
                    "attributeIndex"] else "element" + str(x["depth"])): {k: x["element"][k] for k in x["element"] if
                                                                          k != 'formValues'}}
                t.update(pparent)

                if "children" in x:
                    getChildrenResults(x["children"], attrNames, pbase, t)
                else:
                    pbase.append({"attributes": t, "metrics": x["metrics"]})

            return pbase

        try:

            rows = getChildrenResults(pJsonObjDefinition["result"]["data"]["root"]["children"],
                                      [x["name"] for x in pJsonObjDefinition["result"]["definition"]["attributes"]])
        except KeyError as e:
            log.error("Error parsing dataset results")
            raise MSTRError(msg="Error parsing dataset results", original_exception=e)

    def getDataframeResults(self, pJsonObjDefinition):
        def getChildrenResults(pchildren, attrNames=[], pbase=[], pparent={}):
            """ Recursive function to normalize the results """

            for x in pchildren:

                # Get attribute definition. 
                t = {(attrNames[x["element"]["attributeIndex"]] if len(attrNames) > x["element"][
                    "attributeIndex"] else "element" + str(x["depth"])): x["element"]["name"]}
                t.update(pparent)

                if "children" in x:
                    getChildrenResults(x["children"], attrNames, pbase, t)
                else:
                    t.update({g: x["metrics"][g]["rv"] for g in x["metrics"].keys()})
                    pbase.append(t)

            return pbase

        try:

            rows = getChildrenResults(pJsonObjDefinition["result"]["data"]["root"]["children"],
                                      [x["name"] for x in pJsonObjDefinition["result"]["definition"]["attributes"]])
        except KeyError as e:
            log.error("Error parsing dataset results")
            raise MSTRError(msg="Error parsing dataset results", original_exception=e)


class MSTRDatasetDefinition(MSTRObjDefinition):
    """  Parses the JSON object into a dataset definition
        
    """
    _attributes = []
    _metrics = []

    def __init__(self, pJsonObjDefinition):
        super(MSTRDatasetDefinition, self).__init__(pJsonObjDefinition)
        # print(pJsonObjDefinition)
        try:
            self._attributes = list(map((lambda x: MSTRAttribute(x["id"], x)),
                                        pJsonObjDefinition["result"]["definition"]["availableObjects"]["attributes"]))
            self._metrics = list(map((lambda x: MSTRMetric(x["id"], x)),
                                     pJsonObjDefinition["result"]["definition"]["availableObjects"]["metrics"]))
        except KeyError as e:
            log.error("Error parsing dataset definition")
            raise MSTRError(msg="Error parsing dataset definition", original_exception=e)

    @property
    def Attributes(self):
        return self._attributes

    @property
    def Metrics(self):
        return self._metrics

    def getAttribute(self, attrName):
        return [attr for attr in self._attributes if attr.Name == attrName]

    def __str__(self):
        retvalA = ""
        retvalM = ""
        for x in self._attributes:
            retvalA += str(x)
        for x in self._metrics:
            retvalM += str(x)
        return "Attributes: [{0}]\nMetrics:[{1}]".format(retvalA, retvalM)


class MSTRSearchResults:
    _results = []

    def __init__(self, pJsonSearchResult):
        self._results = list(map((lambda x: MSTRObject(x["id"], x)), pJsonSearchResult.get("result", [])))

    @property
    def Results(self):
        return self._results

    def __str__(self):
        retval = ""
        for x in self._results:
            retval += str(x)
        return retval


class MSTRViewFiler:

    def buildParseTree(self, fplist):

        # if isinstance(fpexp,(list,tuple)):
        #     fplist = fpexp
        # else:
        #     splitter = re.compile(
        #         "([0-9]+|\bAND\b|\bOR\b|\bNOT\b|\bIN\b|\bBETWEEN\b|\b[0-9A-Z]+\b|\(|\)|>=|<=|!=|<>|<|>|=|\+|\-)|\s", re.I)
        #     fplist = [x.upper() for x in splitter.split(fpexp) if x is not None and len(x) > 0]

        pstack = Stack()
        etree = BinaryTree('')
        pstack.push(etree)
        currenttree = etree
        for n, i in enumerate(fplist):
            if i == '(':
                if fplist[n + 1] != 'NOT':
                    currenttree.insertLeft('')
                    pstack.push(currenttree)
                    currenttree = currenttree.getLeftChild()
            elif i not in ['+', '-', '*', '/', 'AND', 'OR', 'NOT', '=', ')']:
                currenttree.setRootVal(i)
                parent = pstack.pop()
                currenttree = parent
            elif i in ['+', '-', '*', '/', '=', 'AND', 'OR']:
                currenttree.setRootVal(i)
                currenttree.insertRight('')
                pstack.push(currenttree)
                currenttree = currenttree.getRightChild()
            elif i == ')':
                currenttree = pstack.pop()
            elif i == 'NOT':
                currenttree.setRootVal(i)
                currenttree.insertLeft('')
                pstack.push(currenttree)
                currenttree = currenttree.getLeftChild()
            else:
                raise ValueError

        return etree


class MSTRObject:
    """  Base MSTR Object
    The constructor receives an optional param with json object definition"""

    _name = None
    _type = None
    _abbreviation = None
    _description = None
    _hidden = None
    _subtype = None
    _extType = None
    _dateCreated = None
    _dateModified = None
    _version = None
    _acg = None
    _iconPath = None
    _viewMedia = None
    _comments = []
    _ancestors = []

    def __init__(self, Id, pJsonObjDefinition=None):
        self._ID = Id
        if pJsonObjDefinition is not None:
            self.update(pJsonObjDefinition)

    def update(self, pJsonObjDefinition):

        self._name = pJsonObjDefinition.get("name", None)
        try:
            if isinstance(pJsonObjDefinition.get("type", None), int):
                self._type = enum.EnumDSSObjectType(pJsonObjDefinition.get("type", None))
            else:
                self._type = enum.EnumDSSObjectType.searchName(pJsonObjDefinition.get("type", None))
        except ValueError:
            self._type = None
        self._abbreviation = pJsonObjDefinition.get("abbreviation", None)
        self._description = pJsonObjDefinition.get("description", None)
        self._hidden = pJsonObjDefinition.get("hidden", None)
        try:
            self._subtype = enum.EnumDSSSubTypes(pJsonObjDefinition.get("subtype", None))
        except ValueError:
            self._subtype = None
        self._extType = pJsonObjDefinition.get("extType", None)
        self._dateCreated = pJsonObjDefinition.get("dateCreated", None)
        self._dateModified = pJsonObjDefinition.get("dateModified", None)
        self._version = pJsonObjDefinition.get("version", None)
        self._acg = pJsonObjDefinition.get("acg", None)
        self._iconPath = pJsonObjDefinition.get("iconPath", None)
        self._viewMedia = pJsonObjDefinition.get("viewMedia", None)
        self._comments = pJsonObjDefinition.get("comments", [])
        self._ancestors = pJsonObjDefinition.get("ancestors", [])

    # Read only properties
    @property
    def ID(self):
        return self._ID

    @property
    def Name(self):
        return self._name

    @property
    def Type(self):
        return self._type

    @property
    def Abbreviation(self):
        return self._abbreviation

    @property
    def Description(self):
        return self._description

    @property
    def Hidden(self):
        return self._hidden

    @property
    def Subtype(self):
        return self._subtype

    @property
    def ExtType(self):
        return self._extType

    @property
    def DateCreated(self):
        return self._dateCreated

    @property
    def DateModified(self):
        return self._dateModified

    @property
    def Version(self):
        return self._version

    @property
    def Acg(self):
        return self._acg

    @property
    def IconPath(self):
        return self._iconPath

    @property
    def ViewMedia(self):
        return self._viewMedia

    @property
    def Comments(self):
        return self._comments

    @property
    def Ancestors(self):
        return self._ancestors

    def __repr__(self):
        """ Textual representation of the object """
        return "ID: " + str(self._ID) + " | Name: " + str(self._name) + " | Type: " + str(
            self._type) + " | Abbreviation: " + str(self._abbreviation) + " | Description: " + str(
            self._description) + " | Hidden: " + str(self._hidden) + " | Subtype: " + str(
            self._subtype) + " | ExtType: " + str(self._extType) + " | DateCreated: " + str(
            self._dateCreated) + " | DateModified: " + str(self._dateModified) + " | Version: " + str(
            self._version) + " | Acg: " + str(self._acg) + "  | IconPath: " + str(
            self._iconPath) + " | ViewMedia: " + str(self._viewMedia) + " | Comments: " + str(
            self._comments) + " | Ancestors: " + str(self._ancestors)
        # .format(self._ID,self._name,str(self._type),self._abbreviation,self._description,self._hidden,str(self._subtype),self._extType,self._dateCreated,self._dateModified,self._version,self._acg,self._iconPath,self._viewMedia,self._comments,self._ancestors)

    def __str__(self):
        return "|-> " + self.__repr__() + " <-|"


# TOKEN Class


class AuthorizationToken:
    _token = None
    isValid = False
    issuedOn = None

    def __init__(self, token=None):
        self.token = token

    def reset(self):
        self._token = None
        self.isValid = False
        self.issuedOn = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token=None):
        if token is None:
            self.reset()
        elif len(token) < 20:  # this validation needs to be checked.
            raise ValueError('Invalid token!!')
        else:
            self._token = token
            self.isValid = True
            self.issuedOn = datetime.now()

    def validate(self):
        self.issuedOn = datetime.now()

    @property
    def validFor(self):
        return (datetime.now() - self.issuedOn).total_seconds() if self.issuedOn is not None else None

    def __str__(self):
        return "token:[{0}] - isValid: {1} - issuedOn: {2}".format(self.token, self.isValid, self.issuedOn)


class MSTRAttributeForm(MSTRObjDefinition):
    _parent = None
    _formID = None
    _formName = None
    _formDataType = None

    def __init__(self, parent, pJsonObjDefinition=None):
        super(MSTRAttributeForm, self).__init__(pJsonObjDefinition)
        self._parent = parent
        if pJsonObjDefinition is not None:
            self.update(pJsonObjDefinition)

    def update(self, pJsonObjDefinition):
        self._formID = pJsonObjDefinition.get("id", None)
        self._formName = pJsonObjDefinition.get("name", None)
        self._formDataType = pJsonObjDefinition.get("dataType", None)

    @property
    def Attribute(self):
        return self._parent

    @property
    def ID(self):
        return self._formID

    @property
    def Name(self):
        return self._formName

    @property
    def DataType(self):
        return self._formDataType

    def todict(self):
        return dict(type="form", attribute=dict(id=self.Attribute.ID, name=self.Attribute.Name),
                    form=dict(id=self.ID, name=self.Name))

    def __repr__(self):
        """ Textual representation of the object """
        return " | Form ID: " + str(self._formID) + " | Form Name: " + str(self._formName) + " | Form DataType: " + \
               str(self._formDataType) + " | Parent ID: " + str(self._parent.ID)


class MSTRAttribute(MSTRObject):
    _forms = []

    def __init__(self, ID, pJsonObjDefinition=None):
        super(MSTRAttribute, self).__init__(ID, pJsonObjDefinition)
        if pJsonObjDefinition is not None:
            self.update(pJsonObjDefinition)

    def update(self, pJsonObjDefinition):
        super(MSTRAttribute, self).update(pJsonObjDefinition)
        self._forms = list(map((lambda x: MSTRAttributeForm(self, x)), pJsonObjDefinition["forms"]))

    @property
    def Forms(self):
        return self._forms

    def todict(self):
        return dict(type="attribute", id=self.ID, name=self.Name)

    def __repr__(self):
        """ Textual representation of the object """
        return super().__repr__() + " | Forms: " + str(self._forms)


class MSTRMetric(MSTRObject):
    _isDerived = False

    def __init__(self, ID, pJsonObjDefinition=None):
        super(MSTRMetric, self).__init__(ID, pJsonObjDefinition)
        if pJsonObjDefinition is not None:
            self.update(pJsonObjDefinition)

    def update(self, pJsonObjDefinition):
        super(MSTRMetric, self).update(pJsonObjDefinition)
        self._isDerived = (str(pJsonObjDefinition.get("isDerived", None)).upper() == 'TRUE')

    @property
    def isDerived(self):
        return self._isDerived

    def todict(self):
        return dict(type="metric", id=self.ID, name=self.Name)

    def __repr__(self):
        """ Textual representation of the object """
        return super().__repr__() + " | isDerived: " + str(self._isDerived)


class MSTRError(Exception):
    """Generic exception for MSTR library"""

    def __init__(self, msg="", original_exception=None, code=None, error=None, pjson=None):
        super(MSTRError, self).__init__((json.dumps(pjson) if pjson is not None else msg) + (
            ("\nUnderlying Exception: %s" % original_exception) if original_exception is not None else ""))
        self.original_exception = original_exception
        if pjson is not None:
            self.code = pjson.get("code", None)
            self.message = pjson.get("message", None)
            self.error = pjson.get("iServerCode", None)
        else:
            self.code = code
            self.message = msg
            self.error = error
        log.error(self.message + (
            ("\nUnderlying Exception: %s" % original_exception) if original_exception is not None else "") + (
                      (" Error: %s" % self.error) if self.error is not None else "") + (
                      (" Code: %s" % self.code) if self.code is not None else ""))


if __name__ == '__main__':
    pass
