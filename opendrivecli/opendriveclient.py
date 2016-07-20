import os
import sys


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

    def __log(self, message, level=3):
        """
        Output Log Message
        :param message: Log Message
        :param level: Log Level (0 = Error, 1 = Warning, 2 = Info, 3 = Debug)
        """
        if level <= self.__args.v:
            if level == 0:
                sys.stderr.write(message + os.linesep)
            else:
                sys.stdout.write(message + os.linesep)

    def run(self):
        """
        Run the program
        """
        self.__log("Starting OpenDrive Client", 3)
        functions = {
            "put": self.__put
        }
        func = functions.get(self.__args.func, lambda: False)
        success = func()
        if success:
            self.__log("Action completed successfully", 2)
            sys.exit(0)
        else:
            self.__log("Action completed with errors", 0)
            sys.exit(1)

    def __put(self):
        """
        Upload a file
        :return: true on success, false on error
        """
        self.__log("Uploading " + self.__args.local_file + " to " + self.__args.remote_dir)
