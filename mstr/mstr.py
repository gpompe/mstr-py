import requests, sys
import logging as log
import logging.config
from datetime import datetime
from urllib.parse import urlparse,urljoin

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
            log.error(e)

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

    def setDefaultProject(self,pProject):
        ''' Set the default project to be used in none is selected.
        Searches in ID, Alias and Name (in this order until find first ocurrence)
        Need to check if multiple IS ar connected
        '''
        log.debug("MSTR Session Default Project searching for %s", pProject )
        # Search by ID
        self.currentProject = next((elem for elem in self._projects if elem['id']==pProject),None)
        log.debug("MSTR Session Default Project searched by ID = %s", self.currentProject )

        if self.currentProject == None:
            # Search by Alias if there is an alias for the project
            self.currentProject = next((elem for elem in self._projects if elem['alias']==pProject and len(elem['alias'])>0),None)
            log.debug("MSTR Session Default Project searched by Alias = %s", self.currentProject )

        if self.currentProject == None:
            # Search by Name
            self.currentProject = next((elem for elem in self._projects if elem['name']==pProject),None)
            log.debug("MSTR Session Default Project searched by Name = %s", self.currentProject )

        # If there is a current project, set the header globally
        if self.currentProject != None:
            self._session.headers.update({"X-MSTR-ProjectID": self.currentProject["id"]})



    def request(self,pVerb,pURL,pHeaders={},pBody=None):
        ''' Runs request request
        '''

        try:
            r = self._session.request(method=pVerb,url=pURL, headers=pHeaders,timeout=MSTRSession.REQ_TIMEOUT,json=pBody)
            r.raise_for_status()
            log.info("Open session Status code:"+str(r.status_code))
            log.debug("Response Headers: %s",r.headers)
            log.debug("Response Content: %s",r.content)

            # self._authToken.token = r.headers['X-MSTR-AuthToken']

        except requests.exceptions.HTTPError as err:
            log.error("HTTP Error: %s\nDetails: %s",err,r.text)
        except ValueError as err:
            log.error(err)
        except requests.exceptions.RequestException as e:
            log.error(e)


        return r



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



if __name__ == '__main__':
    main()
