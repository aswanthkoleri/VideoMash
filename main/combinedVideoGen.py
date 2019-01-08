import os
from itertools import groupby
from collections import namedtuple
from .videoSummarizer import *

class Summary(object):
    def __init__(self, name, summary, summarizedSubtitles):
        self.name = name
        self.summary = summary
        self.summarizedSubtitles = summarizedSubtitles

def combineSubs(summarizeList,minIndex):
    combSubs=[] #combined video subtitles
    combRegions=[]
    for index,item in enumerate(summarizeList[minIndex].summarizedSubtitles):
        hit=1
        for i in range(0,len(summarizeList)):
            if(i==minIndex):
                continue
            if(item not in summarizeList[i].summarizedSubtitles):
                hit=0
                break
        if(hit):
            combSubs.append(item)
            combRegions.append(srt_item_to_range(item))
    return combSubs,combRegions

def findMin(summarizeList):
    minimum = len(summarizeList[0].summary)
    minIndex = 0
    for i in range(1,len(summarizeList)):
        if(len(summarizeList[i].summary) < minimum):
            minimum = len(summarizeList[i].summary)
            minIndex = i
    return minIndex

def makeCorrectTime(summaryObj,videonamepart):
    summarizedSubtitles=summaryObj.summarizedSubtitles
    summary=summaryObj.summary

    starting=0
    sub_rip_file = pysrt.SubRipFile()
    for index,item in enumerate(summarizedSubtitles):
        newSubitem=pysrt.SubRipItem()
        newSubitem.index=index
        newSubitem.text=item.text
        # First find duration
        duration=summary[index][1]-summary[index][0]
        # Then find the ending time
        ending=starting+duration
        newSubitem.start.seconds=starting
        newSubitem.end.seconds=ending
        sub_rip_file.append(newSubitem)
        starting=ending

    print(sub_rip_file)

    path = videonamepart+str(summaryObj.name)+"_summarized.srt"
    with open(path,"w+") as sf:
        for i in range(0,len(sub_rip_file)):
            sf.write(str(sub_rip_file[i]))
            sf.write("\n")
    sf.close()

def find_summary_regions_selected(srt_filename, summarizer, duration, language ,bonusWords, stigmaWords, videonamepart):
    srt_file = pysrt.open(srt_filename)
    # Find the average amount of time required for each subtitle to be showned

    clipList = list(map(srt_item_to_range,srt_file))

    avg_subtitle_duration = total_duration_of_regions(clipList)/len(srt_file)

    # Find the no of sentences that will be required in the summary video
    n_sentences = duration / avg_subtitle_duration
    print("nsentance : "+str(n_sentences))

    # get the summarize video's subtitle array
    [summary,summarizedSubtitles] = summarize(srt_file, summarizer, n_sentences, language, bonusWords, stigmaWords)
    # Check whether the total duration is less than the duration required for the video
    total_time = total_duration_of_regions(summary)
    print("total_time : "+str(total_time))
    try_higher = total_time < duration
    prev_total_time = -1
    # If the duration which we got is higher than required
    if try_higher:
        # Then until the resultant duration is higher than the required duration run a loop in which the no of sentence is increased by 1
        while total_time < duration:
            if(prev_total_time==total_time):
                print("1 : Maximum summarization time reached")
                break
            print("1 : total_time : duration "+str(total_time)+" "+str(duration))
            n_sentences += 1
            [summary,summarizedSubtitles] = summarize(srt_file, summarizer, n_sentences, language, bonusWords, stigmaWords)
            prev_total_time=total_time
            total_time = total_duration_of_regions(summary)
    else:
        # Else if  the duration which we got is lesser than required
        # Then until the resultant duration is lesser than the required duration run a loop in which the no of sentence is increased by 1
        while total_time > duration:
            if(n_sentences<=2):
                print("2 : Minimum summarization time reached")
                break
            print("2 : total_time : duration "+str(total_time)+str(duration))
            n_sentences -= 1
            [summary,summarizedSubtitles] = summarize(srt_file, summarizer, n_sentences, language, bonusWords, stigmaWords)
            total_time = total_duration_of_regions(summary)


    path=videonamepart+str(summarizer)+"_summarized.srt"
    with open(path,"w+") as sf:
        for i in range(0,len(summarizedSubtitles)):
            sf.write(str(summarizedSubtitles[i]))
            sf.write("\n")
    sf.close()

    #test file for finding emotions
    # path = "./media/documents/summarizedSubtitleText.txt"
    # with open(path,"w+") as stf:
    #     for i in range(0,len(summarizedSubtitles)):
    #         stf.write(str(summarizedSubtitles[i].text))
    #         stf.write("\n")
    # stf.close()

    # return the resulant summarized subtitle array
    return summary,summarizedSubtitles

def createComVideo(videoName,subtitleName,dummyTxt,summTypes):
    print("Non Weighted Algorithm")
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

    videoTotSubtile=pysrt.open(subtitleName)
    clipList=list(map(srt_item_to_range,videoTotSubtile))
    summTime=total_duration_of_regions(clipList)/1.7 #taking half of subtitle's time of a video

    base, ext = os.path.splitext(videoName)
    print("base : "+str(base))
    videonamepart = "{0}_".format(base)
    #commonName = videonamepart +str(summarizerName)+"_summarized"

    summarizeList=[]
    for summType in summarizers:
        obj=find_summary_regions_selected(subtitleName,summType,int(summTime),'english',dummyTxt,dummyTxt,videonamepart)
        print("------------------")
        print(obj[1])
        print("------------------")
        node=Summary(summType,obj[0],obj[1])
        summarizeList.append(node)

    for summObj in summarizeList:
        makeCorrectTime(summObj,videonamepart)

    minIndex = findMin(summarizeList)
    [combSubs,combRegions] = combineSubs(summarizeList,minIndex)

    print("*******************")
    print(combSubs)
    print("*******************")

    node=Summary("Combined",combRegions,combSubs)
    makeCorrectTime(node,videonamepart)

    #converting video into seperate clips using combined subtitles
    combSubtitleName=videonamepart+"Combined_summarized.srt"

    print("combined subtitles, regiosummarizersns : ")
    print(combRegions)
    if(combRegions):
        print((combRegions[-1])[1])
        if((combRegions[-1])[1]==0):
            combRegions = combRegions[:-1]

    if(combRegions):
        summary = create_summary(videoName,combRegions)

        # #Converting to video
        # base, ext = os.path.splitext(videoName)
        # dst = "{0}_".format(base)
        # dst = dst+"_combined.mp4"
        # print("dst : "+str(dst))
        # summary.to_videofile(
        #     dst,
        #     codec="libx264",
        #     temp_audiofile="temp.m4a",
        #     remove_temp=True,
        #     audio_codec="aac",
        # )
        dst="blah"
        return dst,combSubtitleName
    else:
        print("cannot extract any regions!")
