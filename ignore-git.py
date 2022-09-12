import json

direc = "/home/ardian/vlr/autonomous-fund/"
files = ["leak_report"]

for j in files:
    print(direc+j)
    print("-------")
    with open(direc+j, "r") as fil:
        con = json.load(fil)
        for i in con:
            print(i["Fingerprint"])
    print()