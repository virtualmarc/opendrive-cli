import sys
import os
import json
from hashlib import md5
import urllib.request
from opendrivecli.odloglevel import ODLogLevel
from opendrivecli.odaccessperm import ODAccessPerm


class OpenDriveAPI:
    """
    OpenDrive API Class
    """
    BASEURL = "https://dev.opendrive.com/api/v1/"
    ACCESS_PRIVATE = 0
    ACCESS_PUBLIC = 1
    ACCESS_HIDDEN = 2

    def __init__(self, loglevel):
        self.__sessionId = None
        self.__loglevel = loglevel

    def log(self, message, level=ODLogLevel.DEBUG):
        """
        Output Log Message
        :param message: Log Message
        :param level: Log Level (0 = Error, 1 = Warning, 2 = Info, 3 = Debug)
        """
        if level <= self.__loglevel:
            if level == ODLogLevel.ERROR:
                sys.stderr.write("[ERROR] " + message + os.linesep)
            elif level == ODLogLevel.WARN:
                message = "[WARN] " + message
            elif level == ODLogLevel.INFO:
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
            self.log("Username or password not set", ODLogLevel.ERROR)
            return False
        if self.__sessionId:
            self.logout()
        try:
            self.log("Logging in to OpenDrive with Username " + username, ODLogLevel.DEBUG)
            resp = self.__dopost(self.BASEURL + "session/login.json", {"username": username, "passwd": password})
            status = resp.getcode()
            if status != 200:
                self.log("Error logging in to OpenDrive, got HTTP Status %d: %s" % (status, resp.read()), ODLogLevel.ERROR)
                return False

            userinfo = self.__decodejson(resp.read())
            self.__sessionId = userinfo["SessionID"]
            return True
        except urllib.request.HTTPError as e:
            self.log("Error logging in to OpenDrive, got HTTP Status %d: %s" % (e.code, e.msg), ODLogLevel.ERROR)
            return False

    def logout(self):
        """
        Logout from OpenDrive
        """
        if self.__sessionId:
            try:
                self.__dopost(self.BASEURL + "session/logout.json", {"session_id": self.__sessionId})
            except urllib.request.HTTPError as e:
                self.log("Error logging out, got HTTP Status %d: %s" % (e.code, e.msg), ODLogLevel.ERROR)
            self.__sessionId = None

    def loggedin(self):
        """
        Check if still logged in
        :return: true if logged in, false if not
        """
        if not self.__sessionId:
            return False
        try:
            resp = self.__dopost(self.BASEURL + "session/exists.json", {"session_id": self.__sessionId})
            status = resp.getcode()
            if status != 200:
                self.log("Error checking session exists, got HTTP Status %d: %s" % (status, resp.read()), ODLogLevel.ERROR)
                return False

            sessioninfo = self.__decodejson(resp.read())
            return sessioninfo["result"]
        except urllib.request.HTTPError as e:
            self.log("Error checking session exists, got HTTP Status %d: %s" % (e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_trash(self, fileid):
        """
        Move a file to the trash
        :param fileid: File ID to be deleted
        :return: true on success, false on error
        """
        if not self.loggedin():
            return False
        try:
            resp = self.__dopost(self.BASEURL + "file/trash.json", {"session_id": self.__sessionId, "file_id": fileid})
            status = resp.getcode()
            if status != 200:
                self.log("Error deleting file %s, got HTTP Status %d: %s" % (fileid, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error deleting file %s, got HTTP Status %d: %s" % (fileid, e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_restore(self, fileid):
        """
        Restore a file from the trash
        :param fileid: File ID to be restored
        :return: true on success, false on error
        """
        if not self.loggedin():
            return False
        try:
            resp = self.__dopost(self.BASEURL + "file/restore.json", {"session_id": self.__sessionId, "file_id": fileid})
            status = resp.getcode()
            if status != 200:
                self.log("Error restoring file %s from trash, got HTTP Status %d: %s" % (fileid, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error restoring file %s from trash, got HTTP Status %d: %s" % (fileid, e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_sendbyemail(self, fileid, rcpt, subject=None, body=None):
        """
        Send one or more files by email
        :param fileid: File ID
        :param rcpt: One or more email addresses, separated by comma
        :param subject: Subject of the email
        :param body: Body of the email
        :return: true on success, false on error
        """
        if not self.loggedin():
            return False
        try:
            req = {"session_id": self.__sessionId, "file_id": fileid, "recipient_emails": rcpt}
            if subject:
                req["message_subject"] = subject
            if body:
                req["message_body"] = body
            resp = self.__dopost(self.BASEURL + "file/sendbyemail.json", req)
            status = resp.getcode()
            if status != 200:
                self.log("Error sending file %s to %s, got HTTP Status %d: %s" % (fileid, rcpt, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error sending file %s to %s, got HTTP Status %d: %s" % (fileid, rcpt, e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_rename(self, fileid, name):
        """
        Rename a file
        :param fileid: File ID
        :param name: New Name
        :return: true on success, false on error
        """
        if not self.loggedin():
            return False
        try:
            resp = self.__dopost(self.BASEURL + "file/rename.json", {"session_id": self.__sessionId, "file_id": fileid, "new_file_name": name})
            status = resp.getcode()
            if status != 200:
                self.log("Error renaming file %s to %s, got HTTP Status %d: %s" % (fileid, name, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error renaming file %s to %s, got HTTP Status %d: %s" % (fileid, name, e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_movecopy(self, fileid, folderid, move=True, override=False, name=None):
        """
        Move or copy a file
        :param fileid: Source File ID
        :param folderid: Destination Folder ID
        :param move: true = Move, false = Copy
        :param override: true = Override if destination exists, false = do not override
        :param name: If set change the file name
        :return: true on success, false on error
        """
        if not self.loggedin():
            return False
        try:
            req = {"session_id": self.__sessionId, "src_file_id": fileid, "dst_folder_id": folderid}
            if move:
                req["move"] = "true"
            else:
                req["move"] = "false"
            if override:
                req["overwrite_if_exists"] = "true"
            else:
                req["overwrite_if_exists"] = "false"
            if name:
                req["new_file_name"] = name
            resp = self.__dopost(self.BASEURL + "file/move_copy.json", req)
            status = resp.getcode()
            if status != 200:
                self.log("Error moving/copying file %s to folder %s, got HTTP Status %d: %s" % (fileid, folderid, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error moving/copying file %s to folder %s, got HTTP Status %d: %s" % (fileid, folderid, e.code, e.msg), ODLogLevel.ERROR)
            return False

    def file_idbypath(self, path):
        """
        Get a File ID by it's path
        :param path: Path to the file (not starting with /)
        :return: File ID, or None if not found
        """
        if not self.loggedin():
            return None
        try:
            resp = self.__dopost(self.BASEURL + "file/idbypath.json", {"session_id": self.__sessionId, "path": path})
            status = resp.getcode()
            if status != 200:
                self.log("Error getting file id by path %s, got HTTP Status %d: %s" % (path, status, resp.read()), ODLogLevel.ERROR)
                return None

            fileinfo = self.__decodejson(resp.read())
            return fileinfo["FileId"]
        except urllib.request.HTTPError as e:
            self.log("Error getting file id by path %s, got HTTP Status %d: %s" % (path, e.code, e.msg), ODLogLevel.ERROR)
            return None

    def file_setaccess(self, fileid, access=ODAccessPerm.PRIVATE):
        """
        Set the Access permissions for a file
        :param fileid: File ID
        :param access: Access Permissions
        :return: true on success, false on error
        """
        if not self.loggedin():
            return None
        try:
            resp = self.__dopost(self.BASEURL + "file/access.json", {"session_id": self.__sessionId, "file_id": fileid, "file_ispublic": access.value})
            status = resp.getcode()
            if status != 200:
                self.log("Error setting access permissions for file %s to %d, got HTTP Status %d: %s" % (fileid, access.value, status, resp.read()), ODLogLevel.ERROR)
                return False

            return True
        except urllib.request.HTTPError as e:
            self.log("Error setting access permissions for file %s to %d, got HTTP Status %d: %s" % (fileid, access.value, e.code, e.msg), ODLogLevel.ERROR)
            return False
