import unittest
import requests_mock
from requests_mock.contrib import fixture
import testtools
import time
import datetime
import mstr


class TestMSTRSession(testtools.TestCase):

    # ...     def test_method(self):
    # ...         self.requests_mock.register_uri('POST', self.TEST_URL, headers={"X-MSTR-AuthToken": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"})
    # ...         resp = requests.get(self.TEST_URL)
    # ...         self.assertEqual('respA', resp.text)
    # ...         self.assertEqual(self.TEST_URL, self.requests_mock.last_request.url)

    BASE_URL = 'http://demo.pxltd.ca:8080/MicroStrategyLibrary/api'
    LOGIN_URL = BASE_URL + '/auth/login'
    SESSION_URL = BASE_URL + '/sessions'

    def setUp(self):
        super(TestMSTRSession, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())

        # self.requests_mock.register_uri('GET', self.TEST_URL, text='respA')

    def test_mstrsessionopen(self):
        """testing MSTRSession Class open method"""
        with testtools.ExpectedException(mstr.MSTRError):
            self.requests_mock.register_uri('POST', self.LOGIN_URL, headers={"X-MSTR-AuthToken-invalid": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"})
            mstr.MSTRSession('http://demo.pxltd.ca:8080/MicroStrategyLibrary/api/', 'user', 'password', autoopen=True, autoload=False)

        self.requests_mock.register_uri('POST', self.LOGIN_URL, headers={"X-MSTR-AuthToken": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"})
        mstrsession = mstr.MSTRSession('http://demo.pxltd.ca:8080/MicroStrategyLibrary/api/', 'user', 'password', autoopen=True, autoload=False)
        self.assertEqual(mstrsession.isValid, True)

    def test_authorizationtoken(self):
        """ Testing AuthorizationToken class"""
        m = mstr.AuthorizationToken("ji7ilqelnud37kpjkofgori17r")

        self.assertEqual(m.isValid, True, "Failed to check if token is valid")
        self.assertEqual(m.token, "ji7ilqelnud37kpjkofgori17r", "Failed to store token")
        time.sleep(3)
        self.assertGreaterEqual(m.validFor, 3, "Failed to return validity period")
        with testtools.ExpectedException(ValueError, msg="Failed to raise error on short token"):
            m.token = "shorttoken"

    def test_mstrsessionvalid(self):
        """testing MSTRSession Class IsValid method"""

        self.requests_mock.register_uri('POST', self.LOGIN_URL, headers={"X-MSTR-AuthToken": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"}, status_code=204)
        self.requests_mock.register_uri('GET', self.SESSION_URL, headers={"X-MSTR-AuthToken": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"}, status_code=204)
        mstrsession = mstr.MSTRSession('http://demo.pxltd.ca:8080/MicroStrategyLibrary/api/', 'user', 'password', autoopen=False, autoload=False)
        self.assertEqual(mstrsession.isValid, False, "Validation after creation failed")
        # forced token invalidation for testing
        mstrsession.open("user", "password", autoload=False)
        self.assertEqual(mstrsession.isValid, True, "Validation after open failed")
        # Force aging of token for testing
        mstrsession.AuthToken.issuedOn = datetime.datetime.now() - datetime.timedelta(seconds=500)
        self.assertEqual(mstrsession.isValid, True, "Revalidation after expiration failed")
        self.requests_mock.register_uri('GET', self.SESSION_URL, headers={"X-MSTR-AuthToken": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"}, status_code=404, json={"code": "ERR009", "message": "The users session has expired, please reauthenticate"})
        # Force aging of token for testing
        mstrsession.AuthToken.issuedOn = datetime.datetime.now() - datetime.timedelta(seconds=500)
        self.assertEqual(mstrsession.isValid, False, "Revalidation after expiration failed")
