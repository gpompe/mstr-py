import requests, sys
import logging as log
import logging.config
from datetime import datetime
from urllib.parse import urlparse,urljoin
import re
import json

# def getCubeDefinition(_pSession,poToken,pCubeId):
#     ''' Retrieves the cube definition '''
#     if poToken.isValid:
#         log.debug("Token param: "+str(poToken))
#         log.debug("Cube ID param: "+pCubeId)
#         try:
#             hdrs = {"X-MSTR-AuthToken": poToken.token,
#                     "Accept": ContentType}

#             log.debug("Request URL: "+BASE_URL + "cubes/" + pCubeId)
#             r = _pSession.get(url=BASE_URL + "cubes/" + pCubeId, headers=hdrs,timeout=REQ_TIMEOUT)
#             r.raise_for_status()
#             log.info("Get cube definition Status code:"+str(r.status_code))
#             return r.text

#         except requests.exceptions.HTTPError as err:
#             log.error("HTTP Error: %s\nDetails: %s",err,r.text)
#         except:
#             log.error("Error "+str(sys.exc_info())+"occured.")




class MSTRSession:
    ''' This class manages the MSTR session and is the entry point to MSTR
        Limitations: Standard authentication only, does not handle session expire date
    '''

    # Constants
    ContentType = "application/json" # To be added in each request as a request header

    REQ_TIMEOUT = 30    # Requests timeout      TODO: Add to configuration

    @property
    def isValid(self):
        ''' Check if the session is valid
            The check is local now, but probably needs to be remote and cached. Local unless # of secs passed since last remote check
            Use /sessions remote method
        '''
        return self._valid

    def getProjectHeader(self, pMstrProjectId):
        return ({"X-MSTR-ProjectID": pMstrProjectId} if pMstrProjectId != None and  re.fullmatch("^[A-Z0-9]{32}$",pMstrProjectId,re.IGNORECASE) else {})


    @property
    def projectCount(self):
        return len(self._projects)

    def __init__(self,mstr_api_url,username=None,userpassword=None,autoopen=True):
        '''MSTRSession Constructor
            mstr_api_url: full URL for MicroStrategy API (ex. https://demo.microstrategy.com/MicroStrategyLibrary/api/)
        '''
        log.debug("MSTR Session creation for %s",username)
        self._mstr_url = mstr_api_url + '/'     # Add final slash in case is missing, double slash is handled by the urljoin
        self._user = username
        self._passw = userpassword

        # Initialize private fields
        # Create web Session
        self._session = requests.Session()
        # Add default headers to the session
        self._session.headers.update({"ContentType": MSTRSession.ContentType,"Accept": MSTRSession.ContentType})     # Default Headers
        self._valid = False
        # Create token struct
        self._authToken = AuthorizationToken()
        # Project List
        self._projects=[]
        # Default Project
        self.currentProject=None

        if autoopen and self._user != None and self._passw != None:
            self.open(self._user, self._passw)
        log.debug("MSTR Session created for %s", self._user)


    def open(self,username,userpassword,autoload=True):
        ''' Open a connection to MSTR Server and get the list of projects available for the user'''
        log.debug("MSTR Session opening for %s",username)
        self._user = username
        self._passw = userpassword

        # JSON Body Open Session
        open_body = {"username": self._user,
                "password": self._passw,
                "loginMode": 1}
        try:
            # Get the authentication token
            self._authToken.token = self.request('POST',urljoin(self._mstr_url, "auth/login"),{},open_body).headers['X-MSTR-AuthToken']
            # Add the auth token to the session headers to be included in all future requests
            self._session.headers.update( {"X-MSTR-AuthToken": self._authToken.token} if self._authToken.isValid else {})
            # Make the session valid
            self._valid = True
            if autoload:
                # Only use projects with Status = Active (0)
                self._projects = [elem for elem in self.getProjectList() if elem['status']==0]

        except KeyError as e:
            log.error("X-MSTR-AuthToken does not exist in the the header.",e)
            raise MSTRError("X-MSTR-AuthToken does not exist in the the header.",e)

        log.debug("MSTR Session created for %s", self._user)


    def close(self):
        ''' Close MSTR Session
        '''
        log.debug("MSTR Session closing for %s", self._user)
        if self.isValid:

            self.request('POST',urljoin(self._mstr_url, "auth/logout"))
            self._valid = False

            log.debug("MSTR Session closed for %s", self._user)
        else:
            log.debug("MSTR Session closing failed. Invalid session for %s", self._user)


    def getProjectList(self):
        ''' Get the list of projects available for the session'''
        log.debug("MSTR Session Project List for %s", self._user)
        if self.isValid:

            r = self.request('GET',urljoin(self._mstr_url, "projects"))

            log.debug("MSTR Session Project List for %s", self._user)
            return list(r.json())
        else:
            log.debug("MSTR Session Project List failed. Invalid session for %s", self._user)
            return None


    def searchProject(self,pProject):
        ''' 
        Searches for project in ID, Alias and Name (in this order until find first ocurrence)
        Need to check if multiple IS ar connected
        '''
        log.debug("MSTR Session Default Project searching for %s", pProject )
        # Search by ID
        _lcurProject = next((elem for elem in self._projects if elem['id']==pProject),None)
        log.debug("MSTR Session Default Project searched by ID = %s", _lcurProject )

        if _lcurProject == None:
            # Search by Alias if there is an alias for the project
            _lcurProject = next((elem for elem in self._projects if elem['alias']==pProject and len(elem['alias'])>0),None)
            log.debug("MSTR Session Default Project searched by Alias = %s", _lcurProject )

        if _lcurProject == None:
            # Search by Name
            _lcurProject = next((elem for elem in self._projects if elem['name']==pProject),None)
            log.debug("MSTR Session Default Project searched by Name = %s", _lcurProject )

        return _lcurProject


    def setDefaultProject(self,pProject):
        ''' Set the default project to be used if none is selected.
        '''
        # Try to set the current project
        self.currentProject = self.searchProject(pProject)

        # If there is a current project, set the header globally
        if self.currentProject != None:
            self._session.headers.update(self.getProjectHeader(self.currentProject["id"]))
            log.debug("MSTR Session Set Header Project ID = %s", self.currentProject["id"])


    def getDatasetDefinition(self,pMstrObjectId,pObjectType=776,pMstrProjectId=None):
        ''' Get Object definition from metadata
             Reports
             DssSubTypeReportGrid = 0x0300 = 768, DssSubTypeReportGraph = 0x0301, DssSubTypeReportEngine = 0x0302, DssSubTypeReportText = 0x0303,
             DssSubTypeReportGridAndGraph = 0x0306, DssSubTypeReportNonInteractive = 0x0307, 

             Cubes
             DssSubTypeReportCube = 0x0308 = 776

        '''
        log.debug("MSTR Session Dataset Definition for %s", self._user)
        if self.isValid:

            if pObjectType == 776:
                _lmethod = "cubes"
            else:
                _lmethod = "reports"
            try:
                r = self.request('GET',urljoin(self._mstr_url, _lmethod + "/" + pMstrObjectId),pHeaders=self.getProjectHeader(pMstrProjectId))

                log.debug("MSTR Session Dataset Definition for %s", self._user)
                return MSTRObjDefinition(r.json())
            except MSTRError as err:
                log.debug("MSTR Session Dataset Definition failed. HTTP Error: %s",err)
                return None
        else:
            log.debug("MSTR Session Dataset Definition failed. Invalid session for %s", self._user)
            return None

    def request(self,pVerb,pURL,pHeaders={},pBody=None):
        ''' Runs request request
        '''
        try:
            r = self._session.request(method=pVerb,url=pURL, headers=pHeaders,timeout=MSTRSession.REQ_TIMEOUT,json=pBody)
            r.raise_for_status()
            log.info("Open session Status code:"+str(r.status_code))
            log.debug("Response Headers: %s",r.headers)
            log.debug("Response Content: %s",r.content)

        except requests.exceptions.HTTPError as err:
            raise MSTRError("Details: %s" % r.text,err)
        except ValueError as err:
            log.error(err)
            raise
        except requests.exceptions.RequestException as e:
            raise MSTRError("Details: %s" % r.text,err)
        return r


class MSTRObjDefinition:

    def __init__(self,pJsonObjDefinition):
        self._json = pJsonObjDefinition

    def __str__(self):
        return json.dumps(self._json)


class MSTRObject:
    ''' Base MSTR Object
    The constructor receives an optional param with json object definition'''
    
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
    _comments = None

    def __init__(self,ID,pJsonObjDefinition=None):
        self._ID = ID
        if pJsonObjDefinition != None:
            self._name = pJsonObjDefinition.get("name",None)
            self._type = pJsonObjDefinition.get("type",None)
            self._abbreviation = pJsonObjDefinition.get("abbreviation",None)
            self._description = pJsonObjDefinition.get("description",None)
            self._hidden = pJsonObjDefinition.get("hidden",None)
            self._subtype = pJsonObjDefinition.get("subtype",None)
            self._extType = pJsonObjDefinition.get("extType",None)
            self._dateCreated = pJsonObjDefinition.get("dateCreated",None)
            self._dateModified = pJsonObjDefinition.get("dateModified",None)
            self._version = pJsonObjDefinition.get("version",None)
            self._acg = pJsonObjDefinition.get("acg",None)
            self._iconPath = pJsonObjDefinition.get("iconPath",None)
            self._viewMedia = pJsonObjDefinition.get("viewMedia",None)
            self._comments = pJsonObjDefinition.get("comments",None)

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




# TOKEN Class

class AuthorizationToken:

    def __init__(self):
        self.reset()

    def reset(self):
        self._token=""
        self.isValid=False
        self.issuedOn=None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self,ptoken=""):
        if len(ptoken) == 0:
            self.reset()
        elif len(ptoken) < 20:
            raise ValueError('Invalid token!!')
        else:
            self._token= ptoken
            self.isValid = True
            self.issuedOn = datetime.now()

    def __str__(self):
        return "token:["+self.token+"] - isValid:"+str(self.isValid)+" - issuedOn:"+str(self.issuedOn)



class MSTRError(Exception):
    """Generic exception for MSTR library"""
    def __init__(self, msg, original_exception):
        super(MSTRError, self).__init__(msg + ("Underlying Exception: %s" % original_exception) + msg)
        self.original_exception = original_exception
        log.error(msg + ("Underlying Exception: %s" % original_exception))


if __name__ == '__main__':
    main()
