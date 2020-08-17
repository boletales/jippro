import sys,os,re,hashlib,json,codecs,numpy,math

bmsexts = [".bms",".bme",".bml"]

mirrorable_break = 2000 #鍵盤間がこれだけ開いたらその前後で正規↔鏡になってても元譜面と同難度であると仮定する
max_breaks = 4 #ただし1曲あたりmax_breaks回を超えてはならない
interval=100
timemax =200*1000
#chartshape1=(1,int(timemax/interval),8,1)
chartshape=(1,int(timemax/interval),8)

def load_models():
    from keras.models import load_model
    return [
        #(1,load_model('prototype2_cdll.h5'))
        (1,load_model('model.h5'))
    ]

def load_dai2():
    with open("第2通常難易度表_略.json",encoding="utf-8") as f:
        return json.load(f)

def load_dai2_insane():
    with open("第2発狂難易度表_略.json",encoding="utf-8") as f:
        return json.load(f)

def convertBMS(fname,dai2_data,dai2_insane_data,convertall,useinsane):
    print(fname)
    with open(fname, "rb") as f:
        binary = f.read()
        md5 = hashlib.md5(binary).hexdigest()

    with codecs.open(fname, "r", "Shift-JIS", "ignore") as f:
        bms_str =  f.read()
        

    dai2_diff = ""
    dai2_diff_str = ""
    dai2_insane_diff = ""
    dai2_insane_diff_str = ""
    dai2_song = [d for d in dai2_data if d["md5"]==md5]
    dai2_insane_song = [d for d in dai2_insane_data if d["md5"]==md5]
    if len(dai2_song)==0 and (not useinsane or len(dai2_insane_song)==0) and not convertall:
        return
    
    if len(dai2_song)>0:
        dai2_diff = (dai2_song[0]["level"])
        dai2_diff_str = "▽"+str(dai2_diff)

    if len(dai2_insane_song)>0:
        dai2_insane_diff = (dai2_insane_song[0]["level"])
        dai2_insane_diff_str = "▼"+str(dai2_insane_diff)

    rank = "0"
    player = "1"
    title = ""
    genre = ""
    artist = ""

    measures = [] #notes(channel,data,position)
    initialbpm = 130
    bpms = {} # "#BPM00"系命令のBPM

    isbpm_id = re.compile(r"#BPM[A-Z0-9]{2}")
    ismeasure = re.compile(r"#\d{5}")
    isobject = re.compile(r"[A-Z0-9]*")

    for line in bms_str.splitlines():
        if line.startswith("#BPM "):
            initialbpm = float(line[len("#BPM "):])
        elif line.startswith("#GENRE "):
            genre = line[len("#GENRE "):]
        elif line.startswith("#TITLE "):
            title = line[len("#TITLE "):]
        elif line.startswith("#ARTIST "):
            artist = line[len("#ARTIST "):]
        elif line.startswith("#RANK "):
            rank = line[len("#RANK "):]
        elif line.startswith("#PLAYER "):
            player = line[len("#PLAYER "):]
        elif re.match(isbpm_id,line):
            bpms[line[4:6]] = float(line[len("#BPM00 "):])
        elif re.match(ismeasure,line):
            measureid = int(line[1:4])
            channel = int(line[4:6])
            if len(measures)<=measureid:
                for i in range(len(measures),measureid+1):
                    measures.append([])
            
            data = line[len("#00000:"):]
            if re.fullmatch(isobject,data):
                data_obj = [data[i: i+2] for i in range(0, len(data), 2)]
                data_len = len(data_obj)
                for i in range(data_len):
                    measures[measureid].append((i/data_len,channel,data_obj[i]))
            else:
                measures[measureid].append((0,channel,data))
    if player!="1":
        return

    bpms["00"] = initialbpm

    measurelength=[]

    for m in measures:
        mlencommand = [c for c in m if c[1]==2]
        if len(mlencommand)>0:
            measurelength.append(float(mlencommand[-1][2]))
        else:
            measurelength.append(1)
        m.append((1,-1,"00"))
        m.sort()

    notes = []
    measurelines = []
    bpm = initialbpm
    time = 0
    for m in zip(measurelength,measures):
        count_inmeasure = 0
        for note in m[1]:
            timing = note[0]
            channel = note[1]
            data = note[2]
            time += (timing-count_inmeasure)*m[0]*60*1000/bpm*4
            count_inmeasure = timing
            if channel == 3 and data!="00":
                bpm = int(data,16)
            elif channel == 8:
                bpm = bpms[data]
            elif 11<=channel and channel<=15 and data!="00":
                notes.append((int(time),channel-11))
            elif channel == 16 and data!="00":
                notes.append((int(time),7))
            elif 18<=channel and channel<=19 and data!="00":
                notes.append((int(time),channel-13))
            elif channel==-1:
                measurelines.append(int(time))
    
    if len(notes)==0:
        return

    lastnote = notes[0][0]
    longestbreaks = [] #(timing,length)
    for n in notes:
        if n[1]==7:
            continue #皿は鏡に関係なし

        if n[0]-lastnote >= mirrorable_break:
            longestbreaks.append((n[0],n[0]-lastnote))

        longestbreaks.sort(key=lambda b: b[1])

        if len(longestbreaks) > max_breaks:
            longestbreaks.pop(0)
        
        lastnote = n[0]

    longestbreaks.append((notes[0][0],0))


    #print([n[1] for n in notes])
    #print(md5)
    print(dai2_diff_str+" "+genre+" / "+title+" (written by: "+artist+")")
    print(str(len(notes))+" notes, "+format(len(notes)/(notes[-1][0]-notes[0][0])*1000, ".2f")+" notes/s")

    return {
        "genre":genre,
        "title":title,
        "artist":artist,
        "bpm":initialbpm,
        "dai2":dai2_diff_str,
        "dai2insane":dai2_insane_diff_str,
        "md5":md5,
        "notes":notes,
        "measurelines":measurelines,
        "breaks":sorted(list(map(lambda b:b[0],longestbreaks))),
    }

def toS(fraction):
    if fraction<=-1:
        return format(fraction, ".2f")
    elif fraction<0:
        return "-"+format(fraction, ".2f")[2:]
    if fraction<=1:
        return ""+format(fraction, ".2f")[1:]
    else:
        return "+"+format(fraction, ".2f")

def toDiffI(index):
    return min(max(0,math.floor(index+0.5)),len(diffs)-1)

def toDiffS(index):
    _i = round(index+0.5,2)
    lv = min(max(0,math.floor(_i)),len(diffs)-2)
    return diffs[lv]+" " + toS(_i-lv)

diffs = ["1","2","3","4","5","6","7","8","9","10","11","11+","12-","12","12+","枠外"]
symbol = "⊿"


def assessDiff(song,models,speed=1):
    dai2 = song["dai2"] if not song["dai2"] == "" else "▽x"

    interval=100
    notes = song["notes"]
    offset = timemax - notes[-1][0]/speed -1
    chart = numpy.zeros((int(200*1000/interval),8),numpy.int32)
    for n in notes:
        if n[0]/speed+offset>=0:
            chart[int((n[0]/speed+offset)/interval)][n[1]] += 1
    
    inlevels = []
    totalweights = 0
    totallevels = 0
    for m in models:
        il = m[1].predict(chart.reshape(chartshape))[0][0]
        inlevels.append(toDiffS(il))
        totallevels += il*m[0]
        totalweights += m[0]
    inlevel = totallevels/totalweights
    #print(inlevels)
    level = diffs[toDiffI(inlevel)]
    fraclv = toDiffS(inlevel)
    return {"md5":song["md5"],"title":song["title"],"level":level,"fraclv":fraclv,"inlevel":inlevel}