import os
from itertools import groupby
from collections import namedtuple
from main.videoSummarizer import *


def combineSubs(results,minIndex):
    Subtitle = namedtuple('Subtitle', 'number start end content')
    combSubs = [] #combined video subtitles
    for obj in results[minIndex]:
        hit=1
        for i in range(0,len(results)):
            if obj not in results[i]:
                hit=0
                break
        if(hit):
            combSubs.append(obj)
    return combSubs

def findMin(results):
    minimum = len(results[0]) #result[0] contains subtitle obj of LR
    minIndex = 0
    for i in range(1,len(results)):
        if(len(results[i]) < minimum):
            minimum = len(results[i])
            minIndex = i
    return minIndex

def createSubtitleObj(summType,subtitleBasePath):
    subtitleName = os.path.join(summType,"summarizedSubtitle.srt")
    totPath = os.path.join(subtitleBasePath,subtitleName)
    with open(totPath) as f:
        res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
    f.close()
    
    Subtitle = namedtuple('Subtitle', 'number start end content')
    subs = []
    for sub in res:
        if len(sub) >= 3: #not strictly necessary
            sub = [x.strip() for x in sub]
            number, start_end, *content = sub # py3 syntax
            start, end = start_end.split(' --> ')
            subs.append(Subtitle(number, start, end, content))
    print()
    print("Result of "+str(summType)+" : ")
    print(subs)
    return subs

def main():
    
    summarizers = ["LR","LS","LU","TR"]

    summTime = input("Enter Summarization Time : ")
    videoName = input("Enter Video Name : ")
    subtitleName = input("Enter Subtitle filename : ") 
    
    videoName = "./media/documents/"+str(videoName)+".mp4"
    subtitleName = "./media/documents/"+str(subtitleName)+".srt"
    dummyTxt = "./media/documents/dummy.txt"

    dstPathVideo = [] #currently not used
    
    #create all videos
    for summType in summarizers:
        dstPathVideo.append(summarizeVideo(videoName,subtitleName,summType,summTime,dummyTxt,dummyTxt))

    
    subtitleBasePath = "./media/documents/"
    results = []
    for summType in summarizers:
        results.append(createSubtitleObj(summType,subtitleBasePath))

    minIndex = findMin(results)
    combSubs = combineSubs(results,minIndex)

    print("*******************")
    print(combSubs)
    print("*******************")

    path = os.path.join(subtitleBasePath,"combinedSubtitle.srt")
    with open(path,"w+") as f:
        for obj in combSubs:
            f.write(obj.number+"\n")
            f.write(obj.start+" --> "+obj.end+"\n")
            for line in obj.content:
                f.write(line+"\n")
            f.write("\n")
    f.close()

if __name__ == "__main__":
    main()
