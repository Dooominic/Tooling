# sshfinder.py by Dominic Hartman. Finds machines with SSH open on the network and checks if you can auth into them with your account.
# Requires masscan.

import sys
from subprocess import check_output
import shlex
import paramiko
from bigSecrets import logins

# Converts masscan standard output into a list of IPs
def masscanParser(out):
    outputList = out.split("\n")
    try:
        outputList.remove("")
    except:
        Exception
    deviceList = []
    for item in outputList:
        outputInfo = item.split(" ")
        deviceInfo = outputInfo[5]
        deviceList.append(deviceInfo)
    return deviceList

# Performs SSH Authentication on list of IPs. When theres a successfull connection to a machine, it will
# write or append said machine to an 'outfile' depending on if one already exists or not.
def sshAuth(ipList):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    name = logins[login]["user"]
    pwd = logins[login]["pass"]
    for ip in ipList:
        try:
            sshClient.connect(ip, username=name, password=pwd, auth_timeout=1, timeout=1)
            successMessage = f"Successfully authenticated into {ip} with user {name}\n"
            try:
                f = open(outfile, "x")
                f.write(successMessage)
                f.close()
            except:
                f = open(outfile, "a")
                f.write(successMessage)
                f.close()

            print(successMessage)
            sshClient.close()
        except:
            print(f"Was unable to authenticate into {ip} with user {name}")

# This function is called if there is an -i command line argument. Iterates through all  /16 subnets on network
def ipManager(netspace):
    print("in ipman")
    for net in range(int(netspace[1]), 255):
        ipaddr = f"{netspace[0]}.{net}.{netspace[2]}.{netspace[3]}"
        outfile = f"sshOut-{ipaddr}.txt"
        core(ipaddr)

def core(ipaddr):
    print("in core")
    args = shlex.split(f"sudo masscan {ipaddr}/16 -p22")
    print(args)
    scanOutput = check_output(args).decode("utf-8")
    ipList = masscanParser(scanOutput)
    sshAuth(ipList)

inc = False
subnet = sys.argv[1]
login = sys.argv[2]

# Checks if there is a -i tag as a commandline parameter and if so, it will increment through all /16 subnets
# on the network.
try:
    if len(sys.argv) > 3:
        if sys.argv[3] == "-i":
            inc = True
        else:
            raise
except: 
    print("Usage: python3 sshfinder.py [ip-address] [login] \n\
           OR python3 sshfinder.py masscan-output.txt\n\
           -i ~ increments through all /16 subnets beginning from IP Address entered.\n\
           Requires masscan on PATH.\n\
           This script currently only increments through the /16 subnet ranges.")
    exit()

scanOutput = ""
outfile = ""

# Checks if subnet commandline argument is masscan-output.txt
if (subnet == "masscan-output.txt"):
    with open('masscan-output.txt', 'r') as file:
        scanOutput = file.read()
    outfile = "masscan-ssh"
else:
    netspace = subnet.split('.')
    increment = int(netspace[1])
    outfile = f"sshOut-{netspace[0]}.{netspace[1]}.{netspace[2]}.{netspace[3]}.txt"
if inc == True:
    ipManager(netspace)
else:
    core(subnet)