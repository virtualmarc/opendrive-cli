import sys
import os
import json
from hashlib import md5
import urllib.request


class OpenDriveAPI:
    """
    OpenDrive API Class
    """
    BASEURL = "https://dev.opendrive.com/api/v1/"

    def __init__(self, loglevel):
        self.__sessionId = None
        self.__loglevel = loglevel

    def log(self, message, level=3):
        """
        Output Log Message
        :param message: Log Message
        :param level: Log Level (0 = Error, 1 = Warning, 2 = Info, 3 = Debug)
        """
        if level <= self.__loglevel:
            if level == 0:
                sys.stderr.write("[ERROR] " + message + os.linesep)
            else:
                if level == 1:
                    message = "[WARN] " + message
                elif level == 2:
                    message = "[INFO] " + message
                else:
                    message = "[DEBUG] " + message
                sys.stdout.write(message + os.linesep)

    def __decodejson(self, data):
        """
        Decode a JSON Object
        :param data: Byte Data
        :return: JSON Object
        """
        strdata = data.decode('utf8')
        return json.loads(strdata)

    def __md5(self, fname):
        """
        Generate MD5 Hash of file
        :param fname: Filename and -path
        :return: MD5 Hash
        """
        hash_md5 = md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def __dopost(self, url, postobject):
        """
        Do a Post Request
        :param url: URL to POST to
        :param postobject: Object to POST (will be encoded as JSON)
        :return: Response Object
        """
        postdata = json.dumps(postobject).encode('utf8')

        req = urllib.request.Request(url, data=postdata, headers={'content-type': 'application/json'})
        req.get_method = lambda: 'POST'
        return urllib.request.urlopen(req)

    def __doget(self, url):
        """
        Go a Get Request
        :param url: URL to GET
        :return: Response Object
        """
        return urllib.request.urlopen(url)

    def login(self, username, password):
        """
        Login to OpenDrive
        :param username: Username
        :param password: Password
        :return: true on successful login, false on error
        """
        if not username or not password:
            self.log("Username or password not set")
            return False
        if self.__sessionId:
            self.logout()
        try:
            self.log("Logging in to OpenDrive with Username " + username, 3)
            resp = self.__dopost(self.BASEURL + "session/login.json", {"username": username, "passwd": password})
            status = resp.getcode()
            if status != 200:
                self.log("Error logging in to OpenDrive, got HTTP Status %d: %s" % (status, status.read()), 0)
                return False

            userinfo = self.__decodejson(resp.read())
            self.__sessionId = userinfo["SessionID"]
            return True
        except urllib.request.HTTPError as e:
            self.log("Error logging in to OpenDrive, got HTTP Status %d: %s" % (e.code, e.msg), 0)
            return False

    def logout(self):
        """
        Logout from OpenDrive
        """
        # @TODO Logout API Call
        self.__sessionId = None
