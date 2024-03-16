import requests
import math
import sys

# Configure
source = "Sol"
destin = "Colonia"
split = 495
radius = 500-split-1
if radius > 100:
    radius = 100
capc = 0

jumps = []
apdat = []

s = requests.Session()

# Get Data
data ={"systemName" : source,
       "showCoordinates" : "1"}

res1 = s.get('https://www.edsm.net/api-v1/system', params=data)
res1j = res1.json()

data ={"systemName" : destin,
       "showCoordinates" : "1"}

res2 = s.get('https://www.edsm.net/api-v1/system', params=data)
res2j = res2.json()

print(res1)

print(res1j)


if len(res1j) == 0:
    print("Recieved empty response, source system", source, "may be invalid")
    sys.exit(0)
    

apdat = [res1j["name"], 0, 0]
jumps.append(apdat)

x1 = res1j["coords"]["x"]
y1 = res1j["coords"]["y"]
z1 = res1j["coords"]["z"]

print(x1, y1, z1)

print(res2j)

if len(res2j) == 0:
    print("Recieved empty response, destination system", destin, "may be invalid")
    sys.exit(0)

x2 = res2j["coords"]["x"]
y2 = res2j["coords"]["y"]
z2 = res2j["coords"]["z"]

print(x2, y2, z2)

# Get distance between source and destination
p = [x1,y1,z1]
q = [x2,y2,z2]

dist = math.dist(p, q)

print(dist)

# Get the differences of xyz between them
xdif = x2 - x1
ydif = y2 - y1
zdif = z2 - z1

print(xdif, ydif, zdif)

print(dist/split)

ptpd = math.floor(dist/split)

# Remove portition less than the split distance
xdfp = xdif * split / dist
ydfp = ydif * split / dist
zdfp = zdif * split / dist

print(xdfp, ydfp, zdfp)

xprv = x1
yprv = y1
zprv = z1


tfuel = 0

if ptpd > 0:
    for i in range(1,ptpd+1):
        xcur = x1 + xdfp * i
        ycur = y1 + ydfp * i
        zcur = z1 + zdfp * i
        print(i)
        print("Current Step Pos", math.floor(xcur), math.floor(ycur), math.floor(zcur))
        
        #print(math.dist([xprv,yprv,zprv],[xcur,ycur,zcur]))

        data ={"x" : xcur,
               "y" : ycur,
               "z" : zcur,
               "radius" : radius,
               "showCoordinates" : "1"}

        res = s.get("https://www.edsm.net/api-v1/sphere-systems", params=data)
        resj = res.json()

        if len(resj) == 0:
            print("Recieved empty response. This may be caused by a too small split value making it unable to find a system.")
            sys.exit(0)

        print("System", resj[0]["name"])


        xsys = resj[0]["coords"]["x"]
        ysys = resj[0]["coords"]["y"]
        zsys = resj[0]["coords"]["z"]

        jdist = math.dist([xprv,yprv,zprv],[xsys,ysys,zsys])

        print("Jump Distance", jdist)

        fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))

        print("Fuel", fuel)

        # apdat = [ resj[0]["name"], fuel ]

        apdat = [resj[0]["name"], jdist, fuel]
        jumps.append(apdat)

        tfuel = tfuel + fuel

        xprv = xsys
        yprv = ysys
        zprv = zsys

    print("Final Jump")
    print(ptpd+1)
    jdist = math.dist([xsys,ysys,zsys],[x2,y2,z2])
    print("Jump Distance", jdist)
    fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))
    print("Fuel", fuel)
    tfuel = tfuel + fuel
    print("Total Fuel", tfuel)
    apdat = [res2j["name"], jdist, fuel]
else:
    print("Final Jump")
    print(ptpd+1)
    print("Jump Distance", dist)
    fuel = math.ceil(5+(dist * (capc + 25000) / 200000))
    print("Total Fuel", fuel)
    apdat = [res2j["name"], dist, fuel]

jumps.append(apdat)

print(jumps)

for i in jumps:
    print(str(i[0]).ljust(30)+str(round(i[1],2))+"\t"+str(i[2]))
