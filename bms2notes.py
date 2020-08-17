import sys,os,re,hashlib,json,codecs,numpy
from util import *
#第2通常難易度表収録曲のみ
#Rでミュージックバー hist(data["notes"][[1]][,1],breaks=,data["measurelines"][[1]],freq=F)



olddir = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
dai2_data = load_dai2()
dai2_insane_data = load_dai2_insane()

os.chdir(olddir)
convertall = (len(sys.argv)>2 and "all" in sys.argv[2:]) #第二通常難易度表に掲載されていない曲も変換するか
#convertall = True
makesample = (len(sys.argv)>2 and "sample" in sys.argv[2:]) #第二通常難易度表に掲載されていない曲も変換するか
useinsane = (len(sys.argv)>2 and "insane" in sys.argv[2:]) #第二通常難易度表に掲載されていない曲も変換するか

songdata_all=[]

def recursiveConvert(path):
    if os.path.isfile(path) and os.path.splitext(path)[1] in bmsexts:
        songdata = convertBMS(path,dai2_data,dai2_insane_data,convertall,useinsane)
        if songdata:
            songdata_all.append(songdata)
            with open("./result/"+os.path.basename(path)+"_"+songdata["md5"][0:6]+".notes.json",encoding="utf-8",mode="w") as f:
                json.dump(songdata,f, ensure_ascii=False)
    elif os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            recursiveConvert(path+"/"+file)



#############################

olddir = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

path=sys.argv[1]
recursiveConvert(path)
os.chdir(olddir)
print("max song length: "+str(max(songdata_all,key=(lambda d:d["notes"][-1][0]))["notes"][-1][0])+" ms")
print("max notes: "+str(len(max(songdata_all,key=(lambda d:len(d["notes"])))["notes"])))


if makesample:
    answers=[]
    samples=[]
    hashs=[]
    keycounts=[]
    keycounts_persec=[]
    dai2_diffs = ["▽1","▽2","▽3","▽4","▽5","▽6","▽7","▽8","▽9","▽10","▽11","▽11+","▽12-","▽12","▽12+"]
    dai2_insane_diffs = ['▼0-','▼0','▼1','▼2','▼3','▼4','▼5','▼6','▼7','▼8','▼9','▼10','▼11','▼12','▼13','▼14','▼15','▼16','▼17','▼18','▼19','▼20','▼21','▼22','▼23','▼24']
    for song in songdata_all:

        flg = False
        if song["dai2"] in dai2_diffs:
            diffindex = dai2_diffs.index(song["dai2"])
            flg = True
        elif useinsane and song["dai2insane"] in dai2_insane_diffs:
            diffindex = dai2_insane_diffs.index(song["dai2insane"])+11
            flg = True

        if flg:
            notes = song["notes"]
            breaks = song["breaks"]
            offset = timemax - notes[-1][0] -1
            for i in range(2**len(breaks)):
                print(song["title"]+"("+str(i+1)+")")
                counts = numpy.zeros(8,numpy.int32)
                chart = numpy.zeros((int(timemax/interval),8),numpy.int32)
                ismirror=False

                nextbreakindex=0
                nextbreak=breaks[0]
                for n in notes:
                    if n[0] == nextbreak:
                        ismirror = 1&(i >> nextbreakindex)
                        if len(breaks)-1 > nextbreakindex:
                            nextbreakindex += 1
                            nextbreak=breaks[nextbreakindex]
                    
                    if n[1]==7:
                        key = 7
                    else:
                        if ismirror:
                            key = 6-n[1]
                        else:
                            key = n[1]
                    
                    counts[key] += 1
                    chart[int((n[0]+offset)/interval)][key] += 1
                
                answers.append(diffindex)
                samples.append(chart.tolist())
                hashs.append(song["md5"])
                keycounts.append(counts.tolist())
                keycounts_persec.append((counts/(notes[-1][0]-notes[0][0])*1000).tolist())

    olddir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    samplename = str(len(answers))
    with open("./samples/"+samplename+"_answers.json",encoding="utf-8",mode="w") as f:
        json.dump(answers,f, ensure_ascii=False)

    with open("./samples/"+samplename+"_keycounts.json",encoding="utf-8",mode="w") as f:
        json.dump(keycounts,f, ensure_ascii=False)

    with open("./samples/"+samplename+"_kps.json",encoding="utf-8",mode="w") as f:
        json.dump(keycounts_persec,f, ensure_ascii=False)

    with open("./samples/"+samplename+"_samples.json",encoding="utf-8",mode="w") as f:
        json.dump(samples,f, ensure_ascii=False)

    with open("./samples/"+samplename+"_hashs.json",encoding="utf-8",mode="w") as f:
        json.dump(hashs,f, ensure_ascii=False)
    os.chdir(olddir)