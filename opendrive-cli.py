import argparse
import configparser
import os
import os.path
import sys
from opendrivecli.opendriveclient import OpenDriveClient

# Global vars
homedir = os.path.expanduser("~")
cfgfile = homedir + "/.odcli"
if not os.path.isfile(cfgfile):
    cfgfile = "/etc/opendrive-cli.conf"
    if not os.path.isfile(cfgfile):
        cfgfile = None
if cfgfile:
    config = configparser.ConfigParser()
    config.read(cfgfile)
else:
    config = None

# General Arguments
args_parser = argparse.ArgumentParser(description='Command Line client for OpenDrive')
args_parser.add_argument('-v', action='count',
                         help='Log Level (0 = just errors, 1 (v) = warnings, 2 (vv) = info, 3 (vvv) = debug', default=0)
args_parser.add_argument('--user', '-u', help='Username (E-Mailaddress)')
args_parser.add_argument('--password', '-p', help='Password')

# Commands
subparsers = args_parser.add_subparsers(help='Commands')

# Upload File
parser_upload = subparsers.add_parser('put', help='Upload a file')
parser_upload.set_defaults(func='put')
parser_upload.add_argument('local_file', help='Local file to upload')
parser_upload.add_argument('remote_dir', help='Remote Directory (ID or Path)')

args = args_parser.parse_args()

# Username and Password
if args.user:
    username = args.user
elif config and "global" in config and "user" in config["global"]:
    username = config["global"]["user"]
else:
    username = None

if args.password:
    password = args.password
elif config and "global" in config and "password" in config["global"]:
    password = config["global"]["password"]
else:
    password = None

if not username or not password:
    sys.stderr.write("[ERROR] Username or password not set" + os.linesep)
    sys.exit(1)

od = OpenDriveClient(args, username, password)
od.run()
