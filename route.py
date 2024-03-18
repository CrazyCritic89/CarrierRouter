import requests
import math
import sys
import time

# Configure
source = input("Enter Source System: ")
destin = input("Enter Destination System: ")
capc = int(input("Enter Used Capacity [0]: ").strip() or "0")

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

xv = res1j["coords"]["x"]
yv = res1j["coords"]["y"]
zv = res1j["coords"]["z"]

if len(res2j) == 0:
    print("Received empty response. Destination system", '"'+destin+'"', "may be invalid.")
    sys.exit(0)

xe = res2j["coords"]["x"]
ye = res2j["coords"]["y"]
ze = res2j["coords"]["z"]

flag = True

size = 60
sinc = 10

tfuel = 0

acsys = []

retrycount = 0

xs = 0
ys = 0
zs = 0

print("Routing... 0%", end='')

while True:
    # Get distance between source and destination
    dist = math.dist([xv,yv,zv], [xe,ye,ze])

    if dist <= 500:
        print("Routing... 100%", end='')
        break

    # Get the differences of xyz between them
    xd = xe - xv
    yd = ye - yv
    zd = ze - zv

    # Get step
    xp = xd * 500 / dist
    yp = yd * 500 / dist
    zp = zd * 500 / dist

    data ={"x" : xv+xp,
           "y" : yv+yp,
           "z" : zv+zp,
           "size" : size,
           "showCoordinates" : "1"}

    res = ses.get("https://www.edsm.net/api-v1/cube-systems", params=data)
    resj = res.json()

    if res.status_code == 429:
        if retrycount == 10:
            print("\nRetry count exceeded. Exiting...")
            sys.exit(1)
        print("\nToo many requests. Trying again in 30 seconds...")
        time.sleep(30)
        retrycount += 1
        ses = requests.Session()
        continue

    if len(resj) == 0:
        size += sinc
        continue
    else:
        hold = 0
        holc = 0
        holi = -1
        tmpi = 0
        for i in resj:
            xc = i["coords"]["x"]
            yc = i["coords"]["y"]
            zc = i["coords"]["z"]
            jc = math.dist([xv,yv,zv],[xc,yc,zc])
            dc = math.dist([xv+xp,yv+yp,zv+zp],[xc,yc,zc])
            # Find longest distance from prev but shortest distance to split
            if jc > hold:
                if jc <= 500:
                    if dc > holc:
                        hold = jc
                        holc = dc
                        holi = tmpi
            tmpi += 1
        if holi == -1 or hold > 500:
            size += sinc
            continue

    xs = resj[holi]["coords"]["x"]
    ys = resj[holi]["coords"]["y"]
    zs = resj[holi]["coords"]["z"]

    jdist = math.dist([xv,yv,zv],[xs,ys,zs])

    fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))

    apdat = [resj[holi]["name"], jdist, fuel]
    jumps.append(apdat)

    tfuel += fuel

    xv = xs
    yv = ys
    zv = zs

    size = 1

    acsys = []

    print("\rRouting...",str(round(xs/xe*100))+"%", end='')
    
jdist = math.dist([xs,ys,zs],[xe,ye,ze])
fuel = math.ceil(5+(jdist * (capc + 25000) / 200000))
tfuel = tfuel + fuel
apdat = [res2j["name"], jdist, fuel]

jumps.append(apdat)

# Find longest string
hold = ""
for i in jumps:
    if len(i[0]) > len(hold):
        hold = i[0]

fitto = len(hold)

print("\n"+"System".ljust(fitto+2)+"Jump Dist   Fuel")

for i in jumps:
    print(str(i[0]).ljust(fitto+2)+str(round(i[1],2)).ljust(12)+str(i[2]))

print("Total Jumps:", len(jumps)-1)
print("Total Fuel: ", tfuel)
