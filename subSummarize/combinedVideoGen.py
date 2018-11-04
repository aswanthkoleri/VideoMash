import os
from itertools import groupby
from collections import namedtuple
from .videoSummarizer import *

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
    minimum = len(results[0])
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

def createComVideo(videoDwldURL,dummyTxt,summTypes):
    summarizers=[]
    for item in summTypes:
        if(item):
            print(item)
            summarizers.append(item)

    print(summarizers)
    #summarizers = ["LR","LS","LU","TR"]

    # dstPathVideo = [] #currently not used
    #create all videos
    # for summType in summarizers:
    #     dstPathVideo.append(summarizeVideo(videoName,subtitleName,summType,summTime,dummyTxt,dummyTxt))
    [videoName,subtitleName]=dwldVideo(videoDwldURL)

    videoTotSubtile=pysrt.open(subtitleName)
    clipList=list(map(srt_item_to_range,videoTotSubtile))
    summTime=total_duration_of_regions(clipList)/1.5 #taking half of subtitle's time of a video

    temp=[]
    for summType in summarizers:
        temp.append(find_summary_regions(subtitleName,summType,int(summTime),'english',dummyTxt,dummyTxt))

    subtitleBasePath = "./media/documents/"
    results = []
    for summType in summarizers:
        results.append(createSubtitleObj(summType,subtitleBasePath))

    minIndex = findMin(results)
    combSubs = combineSubs(results,minIndex)

    print("*******************")
    print(combSubs)
    print("*******************")

    pathCom = os.path.join(subtitleBasePath,"combinedSubtitle.srt")
    with open(pathCom,"w+") as f:
        for obj in combSubs:
            f.write(obj.number+"\n")
            f.write(obj.start+" --> "+obj.end+"\n")
            for line in obj.content:
                f.write(line+"\n")
            f.write("\n")
    f.close()

    #converting video into seperate clips using combined subtitles
    regions=[]
    srt_file = pysrt.open(pathCom)
    for item in srt_file:
        regions.append(srt_item_to_range(item))

    print("combined subtitles, regiosummarizersns : ")
    print(regions)
    if(regions):
        print((regions[-1])[1])
        if((regions[-1])[1]==0):
            regions = regions[:-1]

    if(regions):
        summary = create_summary(videoName,regions)

        #Converting to video
        base, ext = os.path.splitext(videoName)
        dst = "{0}_".format(base)
        dst = dst+"ComSummarized.mp4"
        print("dst : "+str(dst))
        summary.to_videofile(
            dst,
            codec="libx264",
            temp_audiofile="temp.m4a",
            remove_temp=True,
            audio_codec="aac",
        )
        return dst
    else:
        print("cannot extract any regions!")
