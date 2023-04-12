import sys
from subprocess import check_output

# parameter is the output of masscan. The IP address and port number of each device is parsed into into a list 
def outParser(out):
    outputList = out.split("\n")
    outputList.remove("")
    deviceList = []
    for item in outputList:
        outputInfo = item.split(" ")
        port = (outputInfo[3].split("/"))[0]
        deviceInfo = [port, outputInfo[5]]
        deviceList.append(deviceInfo)
    return deviceList

ip = str(sys.argv[1])

out = check_output(["masscan", ip, "-p80,443,8080", "--banners"])

deviceList = outParser(out.decode("utf-8"))

f = open("output.csv", "w")
for item in deviceList:
    f.write(item[1] + "," + item[0] + "\n")
