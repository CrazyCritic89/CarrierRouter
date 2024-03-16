import requests
import math
import sys

# Configure
source = input("Enter Source System: ")
destin = input("Enter Destination System: ")
capc = int(input("Enter Used Capacity [0]: ").strip() or "0")
split = 480
radius = 500-split-1
if radius > 100:
    radius = 100

jumps = []
apdat = []

ses = requests.Session()

# Get Data
data ={"systemName" : source,
       "showCoordinates" : "1"}

res1 = ses.get('https://www.edsm.net/api-v1/system', params=data)
res1j = res1.json()

data ={"systemName" : destin,
       "showCoordinates" : "1"}

res2 = ses.get('https://www.edsm.net/api-v1/system', params=data)
res2j = res2.json()

if len(res1j) == 0:
    print("Received empty response. Source system", '"'+source+'"', "may be invalid.")
    sys.exit(0)
    
apdat = [res1j["name"], 0, 0]
jumps.append(apdat)

x1 = res1j["coords"]["x"]
y1 = res1j["coords"]["y"]
z1 = res1j["coords"]["z"]

if len(res2j) == 0:
    print("Received empty response. Destination system", '"'+destin+'"', "may be invalid.")
    sys.exit(0)

x2 = res2j["coords"]["x"]
y2 = res2j["coords"]["y"]
z2 = res2j["coords"]["z"]

# Get distance between source and destination

dist = math.dist([x1,y1,z1], [x2,y2,z2])

# Get the differences of xyz between them
xdif = x2 - x1
ydif = y2 - y1
zdif = z2 - z1

ptpd = math.floor(dist/split)

# Remove portition less than the split distance
xdfp = xdif * split / dist
ydfp = ydif * split / dist
zdfp = zdif * split / dist

# Set previous to source
xprv = x1
yprv = y1
zprv = z1

tfuel = 0

# Run through splits
print("Routing...", end='')
if ptpd > 0:
    for i in range(1,ptpd+1):
        xcur = x1 + xdfp * i
        ycur = y1 + ydfp * i
        zcur = z1 + zdfp * i

        data ={"x" : xcur,
               "y" : ycur,
               "z" : zcur,
               "radius" : radius,
               "showCoordinates" : "1"}

        res = ses.get("https://www.edsm.net/api-v1/sphere-systems", params=data)
        resj = res.json()

        if res.status_code == 429:
            print("\nToo many requests. Please try again later.")
            sys.exit(1)
        
        
        if len(resj) == 0:
            print("\nReceived empty response. This may be caused by a too small split value making it unable to find a system.")
            sys.exit(0)

        xsys = resj[0]["coords"]["x"]
        ysys = resj[0]["coords"]["y"]
        zsys = resj[0]["coords"]["z"]

        jdist = math.dist([xprv,yprv,zprv],[xsys,ysys,zsys])

        fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))

        apdat = [resj[0]["name"], jdist, fuel]
        jumps.append(apdat)

        tfuel = tfuel + fuel

        xprv = xsys
        yprv = ysys
        zprv = zsys

        print("\rRouting...",str(round(i/(ptpd)*100))+"%", end='')
        sys.stdout.flush()

    jdist = math.dist([xsys,ysys,zsys],[x2,y2,z2])
    fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))
    tfuel = tfuel + fuel
    apdat = [res2j["name"], jdist, fuel]
else:
    fuel = math.ceil(5+(dist * (capc + 25000) / 200000))
    tfuel = fuel
    apdat = [res2j["name"], dist, fuel]

jumps.append(apdat)

#print(jumps)
print("\nSystem                        Jump Dist  Fuel")

for i in jumps:
    print(str(i[0]).ljust(30)+str(round(i[1],2)).ljust(11)+str(i[2]))

print("Total Jumps:", ptpd+1)
print("Total Fuel: ", tfuel)
