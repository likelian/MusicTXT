
import subprocess
import sys
import argparse
import os


def readLines(fileName):
    file = open(fileName)
    lines = file.read().split('\n')
    file.close()
    return lines


def printLines(lines):
    for line in lines:
        print(line)


def loadTitleAndArtist(line):
    words = line.split(':')
    title = words[0]
    artists = words[1].split(';')
    return [title,  list(filter(lambda artist: ("#" not in artist), artists))]


headerCodeEnd = """
  tagline = \\markup {{
   \\column {{
   	  "{}"
	  " "
      "Created by MusicTXT and LilyPond"
    }}
  }}
}}
"""

scoreCode = """
\\score {{
  {0}
  \\chords {1}
  \\new Staff = "up" \\melody
  \\addlyrics {2}
  {3}
  >>\\layout {{ }}
}}
"""

midiCode = """
\\score {{
  \\new PianoStaff \with {{midiInstrument = #"acoustic grand"}} <<
  \\new Staff = "up" \\melody
  {0}
  >>\\midi {{ }}
}}
\\version "2.20.0-1"  % necessary for upgrading to future LilyPond versions.
"""


numerator = '4'


def getNumber(string, startIndex):
    number = ""
    for i in range(startIndex, len(string)):
        if '0' <= string[i] and string[i] <= '9':
            number += string[i]
        else:
            break
    return number


def getHeaderCode(title, artists):
    return "\header{\n  title="+"\""+title+"\"\n  composer="+"\""+artists[0]+"\""+headerCodeEnd


#########################################
isMajor = True
key = ""


def hasKeySigniture(line):
    return "1=" in line.replace("\n", "")


def getKeySigniture(line):
    global isMajor
    global key
    line1 = line.replace(" ", "")
    index = line1.find("=")
    if line1[index-1] == "1":
        isMajor = True
    else:
        isMajor = False
    key = line1[index+1].lower()
    try:
        if line1[index+2] == "#":
            key += "is"
            index += 1
        if line1[index+2] == "b":
            key += "es"
            index += 1
        if line1[index+2] == 'm':
            isMajor = False
    except IndexError:
        pass
    if isMajor:
        return "\\key "+key+" \\major"
    else:
        return "\\key "+key+" \\minor"
#########################################


#########################################
def hasTempoSigniture(line):
    return "T=" in line.replace("\n", "")


def getTempoSigniture(line):
    line1 = line.replace(" ", "")
    index = line1.find("T=")
    tempo = getNumber(line1, index+2)
    return "\\tempo "+str(beatValue)+"="+tempo
#########################################


#########################################
beatsNum = 4  # default 4/4 meter
beatValue = 4
stdDur = "1"  # default whole note for chords
stdDurDivided = "2"  # default half note for two chords attached


def hasTimeSigniture(line):
    return "/" in line.replace("\n", "")


def getTimeSigniture(line):
    line1 = line.replace(" ", "")
    index = line1.find("/")
    numerator = line1[index-1]
    denominator = line1[index+1]
    global beatsNum, beatValue, stdDur, stdDurDivided
    beatsNum = int(numerator)
    beatValue = int(denominator)
    if beatValue == 4:
        if beatsNum == 4:
            stdDur = "1"
            stdDurDivided = "2"
        elif beatsNum == 3:
            stdDur = "2."
            stdDurDivided = "4 "
        elif beatsNum == 2:
            stdDur = "2"
            stdDurDivided = "4"
    elif beatValue == 8:
        if beatsNum == 6:
            stdDur = "2."
            stdDurDivided = "4."
        elif beatsNum == 3:
            stdDur = "4."
            stdDurDivided = "8 "
    return "\\time "+numerator+"/"+denominator
#########################################


whiteKeyList = ["c", "d", "e", "f", "g", "a", "b"]
whiteKeyList_upper = ["C", "D", "E", "F", "G", "A", "B"]
#########################################
# determine whether a line contains melody


def hasChords(line):
    global whiteKeyList_upper
    return any(c in line for c in whiteKeyList_upper)


chords = ""


def getChords(line):
    global whiteKeyList_upper, stdDur, stdDurDivided

    for c in whiteKeyList_upper:
        vb = ""
        if c in ["G", "A", "B"]:
            vb += ","
        line = line.replace(c, " "+c+","+vb+stdDur)
    line = line.replace("0", " r"+stdDur)

    line = line.replace(","+stdDur+"#", "is,"+stdDur)
    line = line.replace(","+stdDur+"b", "es,"+stdDur)
    line = line.replace(",es", "es")
    line = line.replace(",is", "is")

    if line.find("_") != -1:
        while line.find("__") != -1:
            line = line.replace("__", "_")
        _idx = [i for i in range(len(line)) if line.find(
            '_', i) == i]  # index of _
        DurIdx = []
        for i in _idx:  # find the two nearby duration numbers
            DurIdx.append(line.rfind(stdDur, 0, i))
            DurIdx.append(line.find(stdDur, i, len(line)))
        for i in DurIdx:
            line = line[:i] + stdDurDivided + \
                line[i+len(stdDur):]  # change the duration numbers
        line = line.replace("_", " ")

    line = line.replace("7", ":7")
    line = line.replace("m", ":m")
    line = line.replace("M:7", ":maj7")
    line = line.lower()
    line = line.replace("m:7", "m7")
    line = line.replace("+:7", ":aug7")
    line = line.replace("+", ":aug")
    line = line.replace("o:7", ":dim7")
    line = line.replace("o", ":dim")
    line = line.replace("sus", ":sus")

    global chords
    chords += line
#########################################

#########################################
# determine whether a line contains lyrics


def hasLyrics(line):
    return "：" in line or ":" in line


lyrics = ""


def getLyrics(line):
    global lyrics
    line = line.replace("：", ":")
    line = line[line.find(":")+1:]
    space = 0
    for i in range(len(line)):
        if u'\u4e00' <= line[i+space] <= u'\u9fff':  # if the character is Chinese
            line = line[:i+space] + " " + line[i+space:]  # add a space
            space += 1
    lyrics += " " + line
#########################################

#########################################
# determine whether a line contains melody


voiceDict = {}


def hasBarline(line):
    global voiceDict, currentVoice, keyTimeTempo
    alphaList = list(map(chr, range(97, 123)))
    voiceCount = 0
    if "|" in line:
        for i, c in enumerate(line):
            if c == "|":
                voiceCount += 1
            if c.isdigit():
                break
        currentVoice = "melody_" + alphaList[voiceCount-1]
        if currentVoice not in voiceDict:
            voiceDict[currentVoice] = "\n {\clef treble" + keyTimeTempo
    return "|" in line


def getRawMeasure(line, measureNum):
    measures = []

    StartIndex = -1
    while True:
        StartIndex = line.find("|", StartIndex+1)
        if line[StartIndex+1] != "|":
            break

    while StartIndex >= 0:
        EndIndex = line.find("|", StartIndex+1)
        measure = line[StartIndex+1: EndIndex] + " "
        StartIndex = EndIndex
        measures.append(measure)
    return measures[measureNum]


def getPitches(measure):
    global isMajor
    global key
    measure = measure.replace("0", "r&")  # 0 to rest
    table1 = measure.maketrans("’", "'")
    # Determine the interval between C and  /do
    measure = measure.translate(table1)

    global whiteKeyList
    for k in whiteKeyList:
        if key[0] == k:
            keyInterval = whiteKeyList.index(k)
            if keyInterval > 2:
                keyInterval -= 0.1
            if key[1:] == "is":
                keyInterval += 0.1
            if key[1:] == "es":
                keyInterval -= 0.1
    if not isMajor:
        keyInterval += 1.9
        if keyInterval-1.9 < 2.5 < keyInterval:
            keyInterval += 0.2
        if keyInterval-1.9 < 6.5 < keyInterval:
            keyInterval += 0.2
    if keyInterval > 6.5:
        keyInterval -= 7

    # Convert to CMajor-based Jianpu numbers
    new_measure = ""
    altDict = {"#": "p", "b": "t"}  # replace # and b with b and f
    while measure.find("#") + measure.find("b") != -2:
        for alt in altDict.keys():
            altIdx = measure.find(alt) + 1
            if altIdx == 0:
                continue
            altNote = measure[altIdx]
            measure = measure[:altIdx-1] + altDict[alt] + measure[altIdx:]
            nextAltIdx = altIdx
            while nextAltIdx != -1:
                nextAltIdx = measure.find(altNote, nextAltIdx+1, len(measure))
                if measure[nextAltIdx-1] in ("b", "#", "]"):
                    break
                elif measure.find(altNote, nextAltIdx, len(measure)) == -1:
                    break
                else:
                    measure = measure[:nextAltIdx] +    \
                        altDict[alt] + measure[nextAltIdx:]
                    nextAltIdx += 1
    measure = measure.replace("[]", "")

    for i, c in enumerate(measure):
        # if c == "#" or c == "b": c = "";
        if c.isdigit():
            int_c = int(c)
            int_c += keyInterval
            if int_c - keyInterval < 3.5 < int_c:
                int_c += 0.1
            if int_c - keyInterval < 10.5 < int_c:
                int_c += 0.1
            if int_c - keyInterval < 7.5 < int_c:
                int_c += 0.1

            while measure[i-1] == "p":
                int_c += 0.1
                i -= 1
            while measure[i-1] == "t":
                int_c -= 0.1
                i -= 1
            Add_Apostrophe = False
            if int_c > 7.5:
                int_c -= 7
                Add_Apostrophe = True
            int_c = round(int_c, 1)
    # Convert CMajor-based Jianpu numbers to alphabet-based pitches
            c = whiteKeyList[round(int_c)-1]
            Add_Accidentals = round((int_c - round(int_c))*10)
            if Add_Accidentals >= 0:
                c = c + "is"*Add_Accidentals
            else:
                c = c + "es"*abs(Add_Accidentals)
            c += "'"
            if Add_Apostrophe:
                c += "'"
            c += "&"  # for note sepratation

        new_measure += c
        new_measure = new_measure.replace("&'", "'&")
        new_measure = new_measure.replace("&,", ",&")
        new_measure = new_measure.replace("',", "")
        new_measure = new_measure.replace("p", "")
        new_measure = new_measure.replace("t", "")
    return new_measure


def getRhythm(measure):
    return getBeat(measure, 0, "")


def getBeat(measure, beatCount, new_measure):
    global beatsNum
    if beatCount == beatsNum:
        return new_measure
    for i, c in enumerate(measure):
        if c.isspace():
            if i == 0:
                break
            beat = measure[:i]
            beatCount += 1
            new_measure = getDuration(beat, new_measure)
            break
    return getBeat(measure[i+1:], beatCount, new_measure)


def getDuration(beat, new_measure):  # calculate each note values
    global beatValue

    while beat.find(")") != -1:
        beat = beat[:beat.find("(")]                                  \
            + "\grace{ "												  \
            + beat[beat.find("(")+1:beat.find(")")].replace("&", " ") \
            + "}"													  \
            + beat[beat.find(")")+1:]                                 \


    divisions = beat.count("&") + beat.count("-") + beat.count("_")
    beat = beat.replace("_", "")
    if divisions not in [1, 2, 4, 8, 16, 32, 64]:
        beat = " \\tuplet " + str(divisions) + "/" + \
            str(beatValue) + "{ " + beat + " }"
        duration = int(beatValue * 4)
    else:
        duration = divisions * beatValue

    if beat[0] == "-":
        if new_measure[-2:] == "~8" and beatValue == 8:
            new_measure = new_measure[:-2] + "."
        if new_measure[-1] == "8":
            new_measure = new_measure[:-1] + "4"
        elif new_measure[-1] == "4" and beatValue == 8:
            new_measure = new_measure[:-1] + "4."
        elif new_measure[-1] == "4" and beatValue == 4:
            new_measure = new_measure[:-1] + "2"
        elif new_measure[-1] == "2" and beatValue == 8:
            new_measure = new_measure + "~8"
        elif new_measure[-1] == "2" and beatValue == 4:
            new_measure = new_measure[:-1] + "2."
        elif new_measure[-1] == "." and beatValue == 8:
            new_measure = new_measure[:-2] + "2"
        elif new_measure[-1] == "." and beatValue == 4:
            new_measure = new_measure[:-1] + "1"
        return new_measure

    beat = beat.replace("--", "-.")
    beat = beat.replace("^", "~")
    beat = beat.replace("&`", str(int(duration*2)))
    beat = beat.replace("&-", str(int(duration/2)))
    beat = beat.replace("&", str(duration))
    new_measure += " " + beat
    return new_measure


Footer = ""


def getFooter(lines):
    global Footer
    c = [i for i, e in enumerate(lines) if "%%" in e][::-1]
    for i, k in zip(c[0::2], c[1::2]):
        Footer += "\" \"".join(lines[k+1:i])
    lines = list(map(lambda line: line.split("%")[0], lines))
    return lines


def removeComments(lines):
    c = [i for i, e in enumerate(lines) if "%%%" in e][::-1]
    for i, k in zip(c[0::2], c[1::2]):
        del lines[k:i+1]
    return lines


currentVoice = 0


def getMeasures(line):
    global voiceDict, currentVoice
    n = 0
    while True:
        try:
            voiceDict[currentVoice] += "  " + \
                getRhythm(getPitches(getRawMeasure(line, n))) + "\n"
            n += 1
        except UnboundLocalError:
            break


# get value from django -> views.py
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--string", type=str, required=True)
args = parser.parse_args()
# print(args.string)
print(os.path.dirname(os.path.realpath(__file__)))

# oepn the file by here
scoreLines = getFooter(removeComments(
    readLines("media/"+args.string+".txt")))
lineIndex = 0
while scoreLines[lineIndex].strip() == "":
    lineIndex += 1
[title, artists] = loadTitleAndArtist(scoreLines[lineIndex])
lineIndex += 1
headerCodeEnd = headerCodeEnd.format(Footer)
headerCode = getHeaderCode(title, artists)
keyTimeTempo = ""

hasChord = False
while lineIndex < len(scoreLines):
    line = scoreLines[lineIndex]
    lineIndex += 1
    if hasKeySigniture(line):
        keyCode = "  "+getKeySigniture(line)+"\n"
        keyTimeTempo += keyCode
    elif hasLyrics(line):
        getLyrics(line)
    elif hasChords(line):
        hasChord = True
        getChords(line)
    if hasTimeSigniture(line):
        keyTimeTempo += "  "+getTimeSigniture(line)+"\n"
    if hasTempoSigniture(line):
        keyTimeTempo += "  "+getTempoSigniture(line)+"\n"
    if hasBarline(line):
        getMeasures(line)


melodyCode = ""
combineCode = "\nmelody = \partcombine \melody_None \melody_None\n"
for key in voiceDict.keys():
    melodyCode += key + "=" + voiceDict[key] + "}\n"
    combineCode += "melody = \partcombine \melody \\" + key + "\n"

melodyCode += combineCode

lyrics = "{" + lyrics + "}"

pianoCode = ""
downCode = ""
if hasChord:
    chords = "{" + chords + "}"
    chordCode = "\nchord=  { \n  \\clef bass\n" \
        + keyCode \
        + "\n  \\chordmode " + chords + "}"
    pianoCode = "\\new PianoStaff <<"
    downCode = "\\new Staff = \"down\" \\chord"


scoreCode = scoreCode.format(pianoCode, chords, lyrics, downCode)
midiCode = midiCode.format(downCode)

# save the file by here
file = open("media/"+args.string+".ly", "w")
file.write(headerCode)
file.write(melodyCode)
if hasChord:
    file.write(chordCode)
file.write(scoreCode)
file.write(midiCode)
file.close()
