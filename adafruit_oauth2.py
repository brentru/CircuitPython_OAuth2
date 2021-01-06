# SPDX-FileCopyrightText: Copyright (c) 2021 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_oauth2`
================================================================================

CircuitPython helper for OAuth2.0 authorization to access Google APIs.


* Author(s): Brent Rubell

Implementation Notes
--------------------

**Hardware:**


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_OAuth2.git"

# Google's authorization server
DEVICE_AUTHORIZATION_ENDPOINT = "https://oauth2.googleapis.com/device/code"

class OAuth2:
    """Implements OAuth2.0 authorization to access
    Google APIs via the OAuth 2.0 limited-input device application flow.
    https://developers.google.com/identity/protocols/oauth2/limited-input-device

    :param requests: An adafruit_requests object.
    :param str client_id: The client ID for your application.
    :param str client_secret: The client secret obtained from the API Console.
    :param list scopes: Scopes that identify the resources the application
                        can access on the user's behalf.

    """
    def __init__(self, requests, client_id, client_secret, scopes):
        self._requests = requests
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        # empty properties for tokens during auth. process
        self._device_code = None
        # length of time that the codes above are valid, in seconds
        self._expiration_time = None
        # length of time we'll wait between polling the auth. server
        self._interval = None
        # url user must navigate to on a browser
        self._verification_url = None
        # identifies the scopes requested by the application
        self._user_code = None

    def request_codes(self):
        """Identifies your application and access scopes with Google's
        authorization server. Attempts to request device and user codes 
        """
        headers = {"Host": "oauth2.googleapis.com",
                   "Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length":"0"}
        url = DEVICE_AUTHORIZATION_ENDPOINT + \
              "?client_id={0}&scope={1}".format(self._client_id, self._scopes)

        response = self._requests.post(url, headers=headers)
        json_resp = response.json()
        response.close()
        # Handle `quota exceeded` error
        if 'error_code' in json_resp:
            raise RuntimeError('Error, quota exceeded: ', json_resp['error_code'])

        # parse response
        self._device_code = json_resp['device_code']
        self._expiration_time = json_resp['expires_in']
        self._interval = json_resp['interval']
        self._verification_url = json_resp['verification_url']
        self._user_code = json_resp['user_code']
