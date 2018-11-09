from models import Weight
from .combinedVideoGen import *
from .videoSummarizer import *

def combined(videoName,subtitleName,dummyTxt,summTypes):
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


    subtitleBasePath = videonamepart
    results = []
    for summType in summarizers:
        results.append(createSubtitleObj(summType,subtitleBasePath))

    w=Weight.object.get(id=1)
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
            print("sent ",sent[4:])
            MainSubtitle.append(sent[4:])
            MainSubtitileFrequency.append(0)


    for i in range(0,len(results)):
        # for each result increase the frequency with the multiple of weight corresponding to summType
        for obj in results[i]:
            # if this sentence is there then find its location in Main sub and store in loc
            for i in range(len(MainSubtitle)):
                if(MainSubtitle[i]==obj.content[0]):
                    loc=i
                    MainSubtitileFrequency[loc]=MainSubtitileFrequency+weights[i]

    type_freq=[]
    for _ in summarizers:
        type_freq.append(0)

    index=0
    for frequency in MainSubtitileFrequency:
        if(frequency!=0):
            for i in range(len(results)):
                #check if that index is present in result[i]
                for j in i:
                    if(MainSubtitle[index]==j.content[0]):
                        type_freq[i]=type_freq[i]+1
        index=index+1

    max_weight_index=type_freq.index(max(type_freq))

    ## update weight accordingly
    weights[max_weight_index]=weights[max_weight_index]+0.1
    if(max_weight_index==0):
        w.LR=weights[max_weight_index]
    elif(max_weight_index==1):
        w.LS=weights[max_weight_index]
    elif(max_weight_index==2):
        w.LU=weights[max_weight_index]
    else:
        w.TR=weights[max_weight_index]
    w.save()
