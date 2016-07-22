import sys
from opendrivecli.opendriveapi import OpenDriveAPI


class OpenDriveClient:
    """
    OpenDrive Client Class
    """

    def __init__(self, args, username, password):
        """
        Create a new OpenDrive Client Class
        :param args: Command Line arguments
        :param username: Username
        :param password: Password
        """
        self.__args = args
        self.__username = username
        self.__password = password
        self.__od = OpenDriveAPI(self.__args.v)

    def run(self):
        """
        Run the program
        """
        self.__od.log("Starting OpenDrive Client", 3)
        # Login
        if not self.__od.login(self.__username, self.__password):
            sys.exit(1)
        # Select Action Handler
        functions = {
            "put": self.__put
        }
        func = functions.get(self.__args.func, lambda: False)
        success = func()
        if success:
            self.__od.log("Action completed successfully", 2)
            sys.exit(0)
        else:
            self.__od.log("Action completed with errors", 0)
            sys.exit(1)

    def __login(self):
        """
        Login to OpenDrive
        """

    def __convertPathToId(self, path):
        """
        Convert a Path to an ID
        :param path: Absolute Path or ID
        :return: ID for Path, return input when its an ID, None on invalid path
        """

    def __put(self):
        """
        Upload a file
        :return: true on success, false on error
        """
        self.__od.log("Uploading " + self.__args.local_file + " to " + self.__args.remote_dir)
