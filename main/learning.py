from .models import Weight
from .combinedVideoGen import *
from .videoSummarizer import *

def combined(videoName,subtitleName,dummyTxt,summTypes):
    print("Weighted Algorithm")
    summarizers=[]
    for item in summTypes:
        if(item):
            print(item)
            summarizers.append(item)

    print(summarizers)

    videoTotSubtile=pysrt.open(subtitleName)
    clipList=list(map(srt_item_to_range,videoTotSubtile))
    summTime=total_duration_of_regions(clipList)

    base, ext = os.path.splitext(videoName)
    print("base : "+str(base))
    videonamepart = "{0}_".format(base)

    summarizeList=[]
    for summType in summarizers:
        obj=find_summary_regions_selected(subtitleName,summType,int(summTime),'english',dummyTxt,dummyTxt,videonamepart)
        node=Summary(summType,obj[0],obj[1])
        summarizeList.append(node)

    for summObj in summarizeList:
        makeCorrectTime(summObj,videonamepart)

    minIndex = findMin(summarizeList)
    [combSubs,combRegions] = combineSubs(summarizeList,minIndex)

    node=Summary("Combined",combRegions,combSubs)
    makeCorrectTime(node,videonamepart)

    combSubtitleName=videonamepart+"Combined_summarized.srt"

    print("combined subtitles, regiosummarizersns : ")
    print(combRegions)
    if(combRegions):
        print((combRegions[-1])[1])
        if((combRegions[-1])[1]==0):
            combRegions = combRegions[:-1]



    subtitleBasePath = videonamepart
    results = []
    # for summType in summarizers:
    #     results.append(createSubtitleObj(summType,subtitleBasePath))

    w=Weight.objects.get(id=1)
    weights=[]
    #summarizers = ["LR","LS","LU","TR"]
    for type in summarizers:
        if(type=="LR"):
            weights.append(w.LR)
        elif(type=="LS"):
            weights.append(w.LS)
        elif(type=="LU"):
            weights.append(w.LU)
        elif(type=="TR"):
            weights.append(w.TR)

    MainSubtitileFrequency=[]
    MainSubtitle=[]
    for ob in videoTotSubtile:
        sent=srt_to_doc([ob])
        print("sentence ",sent[4:])
        MainSubtitle.append(sent[4:])
        MainSubtitileFrequency.append(0)

    print(MainSubtitle)


    #for i in range(0,len(results)):
    #for i in range(0,len(summarizeList)):
        # for each result increase the frequency with the multiple of weight corresponding to summType
        #for obj in results[i]:
    #print(summarizeList)
    type_index=0
    for obj in summarizeList:
        #print(obj)
        summarizedSubtitles=obj.summarizedSubtitles
        print(summarizedSubtitles)
        # if this sentence is there then find its location in Main sub and store in loc
        for i in range(len(MainSubtitle)):
            for index,item in enumerate(summarizedSubtitles):
                MainSubtitle[i] = "".join("".join(item.text.split(" ")).split("\n"))
                item.text = "".join("".join(item.text.split(" ")).split("\n"))
                if(MainSubtitle[i]==str(item.text)):
                    loc=i
                    MainSubtitileFrequency[loc]=MainSubtitileFrequency[loc]+weights[type_index]
        type_index=type_index+1

    type_freq=[]
    for _ in summarizers:
        type_freq.append(0)
    # print("--------------")
    # print(MainSubtitileFrequency)
    # print("--------------")
    index=0
    for frequency in MainSubtitileFrequency:
        if(frequency!=0):
            ind=0
            for obj in summarizeList:
                summarizedSubtitles=obj.summarizedSubtitles
                #check if that index is present in result[i]
                for index,item in enumerate(summarizedSubtitles):
                    if(MainSubtitle[index]==item.text):
                        type_freq[ind]=type_freq[ind]+1
                ind=ind+1
        index=index+1



    max_weight_index=type_freq.index(max(type_freq))
    min_weight_index=type_freq.index(min(type_freq))
    ## update weight accordingly
    weights[max_weight_index]=weights[max_weight_index]+0.005
    weights[min_weight_index]=weights[min_weight_index]-0.005
    best=""
    worst=""
    if(max_weight_index==0):
        w.LR=weights[max_weight_index]
        best="Lex Rank"
    elif(max_weight_index==1):
        w.LS=weights[max_weight_index]
        best="Latent Semantic"
    elif(max_weight_index==2):
        w.LU=weights[max_weight_index]
        best="Luhn"
    else:
        w.TR=weights[max_weight_index]
        best="Text Rank"

    if(min_weight_index==0):
        worst="Lex Rank"
        w.LR=weights[min_weight_index]
    elif(min_weight_index==1):
        w.LS=weights[min_weight_index]
        worst="Latent Semantic"
    elif(min_weight_index==2):
        w.LU=weights[min_weight_index]
        worst="Luhn"
    else:
        worst="Text Rank"
        w.TR=weights[min_weight_index]
    w.save()

    if(combRegions):
        summary = create_summary(videoName,combRegions)

        #Converting to video
        base, ext = os.path.splitext(videoName)
        dst = "{0}_".format(base)
        dst = dst+"_combined.mp4"
        print("dst : "+str(dst))
        summary.to_videofile(
            dst,
            codec="libx264",
            temp_audiofile="temp.m4a",
            remove_temp=True,
            audio_codec="aac",
        )
        return dst,combSubtitleName,best,worst
    else:
        print("cannot extract any regions!")
