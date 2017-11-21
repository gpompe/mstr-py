import requests, sys
import logging as log
import logging.config
from datetime import datetime
from urllib.parse import urlparse,urljoin
# from config_private import *

# ContentType = "application/json" # To be added in each request as a request header

# #MicroStrategy Object
# #mstrcubeid = "CC02C5C24AE2803ABF14EDA5038159D4" # unsupported cube
# mstrcubeid = "6C204A564286DEB3E2CACB98762272C0"  # Id of the cube or report used
# itemPerPage = 20                         # Number of items the table will display per page


# # ******** Constants

# BASE_URL = ("https" if isSecureConnection else "http") + "://" + RESTServerIP + ":" + RESTServerPort + "/MicroStrategyLibrary/api/"

# REQ_TIMEOUT = 30    # Requests timeout



# # Entry Point
# def main():
#     #logging.config.fileConfig('logging.conf')

#     # Create token stuct
#     authToken = AuthorizationToken()


#     # Create Session
#     _session = requests.Session()

#     hdrs = {"ContentType": ContentType,
#             "Accept": ContentType}

#     # Open Session
#     bodyopen = {"username": username,
#             "password": password,
#             "loginMode": 1}

#     try:
#         r = _session.post(url=BASE_URL + "auth/login", headers=hdrs,timeout=REQ_TIMEOUT,json=bodyopen)
#         r.raise_for_status()
#         log.info("Open session Status code:"+str(r.status_code))

#         print(r.headers)
#         authToken.token = r.headers['X-MSTR-AuthToken']

#     except requests.exceptions.HTTPError as err:
#         log.error("HTTP Error: %s\nDetails: %s",err,r.text)
#     except ValueError as err:
#         log.error(err)
#     except requests.exceptions.RequestException as e:
#         log.error(e)


#     # Get Project List
#     for x in getProjectList(_session, authToken):
#         print(x)

#     # print(getCubeDefinition(authToken,mstrcubeid))

#     if authToken.isValid:
#         #Close session
#         try:
#             hdrsclose = {"ContentType": ContentType,
#                          "X-MSTR-AuthToken": authToken.token}

#             r = _session.post(url=BASE_URL + "auth/logout", headers=hdrsclose,timeout=REQ_TIMEOUT,data='{}')
#             r.raise_for_status()
#             log.info("Close session Status code:"+str(r.status_code))
#             print(r.headers)
#         except requests.exceptions.HTTPError as err:
#             log.error("HTTP Error: %s\nDetails: %s",err,r.text)
#         except:
#             log.error("Error "+str(sys.exc_info())+"occured.")


# def getProjectList(_pSession,poToken):
#     if poToken.isValid:
#     #
#         try:
#             hdrsplist = {"X-MSTR-AuthToken": poToken.token,
#             "Accept": ContentType}

#             r = _pSession.get(url=BASE_URL + "projects", headers=hdrsplist,timeout=REQ_TIMEOUT)
#             r.raise_for_status()
#             log.info("Close session Status code:"+str(r.status_code))

#         except requests.exceptions.HTTPError as err:
#             log.error("HTTP Error: %s\nDetails: %s",err,r.text)
#         except:
#             log.error("Error "+str(sys.exc_info())+"occured.")

#         return list(r.json())
#     else:
#         return None


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
        Limitations: Standard authentication only
    '''
    ContentType = "application/json" # To be added in each request as a request header

    REQ_TIMEOUT = 30    # Requests timeout      TODO: Add to configuration

    def __init__(self,mstr_api_url,username=None,userpassword=None,autoopen=True):
        '''MSTRSession Constructor
            mstr_api_url: full URL for MicroStrategy API (ex. https://demo.microstrategy.com/MicroStrategyLibrary/api/)
        '''
        log.debug("MSTR Session creation for %s",username)
        self._mstr_url = mstr_api_url
        self._user = username
        self._passw = userpassword
        # Initialize private fields
         # Create Session
        self._session = requests.Session()
        self._valid = False
        # Create token stuct
        self._authToken = AuthorizationToken()
        if autoopen and self._user != None and self._passw != None:
            self.open(self._user, self._passw)
        log.debug("MSTR Session created for %s", self._user)

    def open(self,username,userpassword):
        log.debug("MSTR Session opening for %s",username)
        self._user = username
        self._passw = userpassword

        # Header for Open Session
        open_hdrs = {"ContentType": MSTRSession.ContentType,
                    "Accept": MSTRSession.ContentType}

        # JSON Body Open Session
        open_body = {"username": self._user,
                "password": self._passw,
                "loginMode": 1}

        try:
            r = self._session.post(url=urljoin(self._mstr_url, "auth/login"), headers=open_hdrs,timeout=MSTRSession.REQ_TIMEOUT,json=open_body)
            r.raise_for_status()
            log.info("Open session Status code:"+str(r.status_code))

            self._authToken.token = r.headers['X-MSTR-AuthToken']

        except requests.exceptions.HTTPError as err:
            log.error("HTTP Error: %s\nDetails: %s",err,r.text)
        except ValueError as err:
            log.error(err)
        except requests.exceptions.RequestException as e:
            log.error(e)

        log.debug("MSTR Session created for %s", self._user)

    def close(self):
        ''' Close MSTR Session
        '''
        log.debug("MSTR Session closing for %s", self._user)
        if self._authToken.isValid:
            #Close session
            try:
                close_hdrs = {"ContentType": MSTRSession.ContentType,
                             "X-MSTR-AuthToken": self._authToken.token}

                r = self._session.post(url=urljoin(self._mstr_url, "auth/logout"), headers=close_hdrs,timeout=MSTRSession.REQ_TIMEOUT)
                r.raise_for_status()
                log.info("Close session Status code:"+str(r.status_code))

            except requests.exceptions.HTTPError as err:
                log.error("HTTP Error: %s\nDetails: %s",err,r.text)
            except:
                log.error("Error "+str(sys.exc_info())+"occured.")

            log.debug("MSTR Session closed for %s", self._user)
        else:
            log.debug("MSTR Session closing failed. Invalid session for %s", self._user)



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
