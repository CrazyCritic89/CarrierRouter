import requests
import json
import math

# Configure
source = "Sol"
destin = "Colonia"
split = 480
radius = 500-split
if radius > 100:
    radius = 100

# Get Data
data ={"systemName" : source,
       "showCoordinates" : "1"}

res1 = requests.get('https://www.edsm.net/api-v1/system', params=data)
res1j = res1.json()

data ={"systemName" : destin,
       "showCoordinates" : "1"}

res2 = requests.get('https://www.edsm.net/api-v1/system', params=data)
res2j = res2.json()

print(res1)

print(res1j)

x1 = res1j["coords"]["x"]
y1 = res1j["coords"]["y"]
z1 = res1j["coords"]["z"]

print(x1, y1, z1)

print(res2j)

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

for i in range(1,ptpd+1):
    xcur = x1 + xdfp * i
    ycur = y1 + ydfp * i
    zcur = z1 + zdfp * i
    print(i)
    print("Current Step Pos", xcur, ycur, zcur)
    
    #print(math.dist([xprv,yprv,zprv],[xcur,ycur,zcur]))

    data ={"x" : xcur,
           "y" : ycur,
           "z" : zcur,
           "radius" : radius,
           "showCoordinates" : "1"}

    res = requests.get("https://www.edsm.net/api-v1/sphere-systems", params=data)
    resj = res.json()

    print("System", resj[0]["name"])

    xsys = resj[0]["coords"]["x"]
    ysys = resj[0]["coords"]["y"]
    zsys = resj[0]["coords"]["z"]

    jdist = math.dist([xprv,yprv,zprv],[xsys,ysys,zsys])

    print("Jump Distance", jdist)

    fuel = 5+(jdist * 25000 / 200000)

    print("Fuel", fuel)

    # apdat = [ resj[0]["name"], fuel ]

    tfuel = tfuel + fuel

    xprv = xsys
    yprv = ysys
    zprv = zsys

print("Total Fuel", tfuel)
