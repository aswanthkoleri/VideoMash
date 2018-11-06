# Imports
import argparse
import os
import pysrt
import re
import subprocess
import sys
import math
import pytube

from moviepy.editor import VideoFileClip, TextClip, ImageClip, concatenate_videoclips

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer

SUMMARIZERS = {
    'LU': LuhnSummarizer,
    'ED': EdmundsonSummarizer,
    'LS': LsaSummarizer,
    'TR': TextRankSummarizer,
    'LR': LexRankSummarizer
}

def progress_check(stream = None, chunk = None, file_handle = None, remaining = None):
    #Gets the percentage of the file that has been downloaded.
    percent = (100*(file_size-remaining))/file_size
    print("{:00.0f}% downloaded".format(percent))

def dwldVideo(videoDwldURL):
    path = './media/documents/'
    subtitlePath = path+"sampleSubtitle.srt"
    videoPath = path+"sampleVideo.mp4"
    
    yt = pytube.YouTube(videoDwldURL,on_progress_callback=progress_check)
    #fetch subtitle
    caption = yt.captions.get_by_language_code('en')
    subtitle = caption.generate_srt_captions()
    regex=re.compile(r'<.*?>')
    subtitle=regex.sub('',subtitle)
    print("*************")
    print(subtitle)
    print("*************")

    with open(subtitlePath,"w+") as f:
        f.write(subtitle)
    #fetch video
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    global file_size
    file_size = stream.filesize
    stream.download(output_path=path, filename="sampleVideo")
    return videoPath,subtitlePath

# Function to concatenate the video to obtain the summary
def create_summary(filename, regions):
    subclips = []
    # obtain video
    input_video = VideoFileClip(filename)
    # Scan through video and store the subclips in an array
    last_end = 0
    for (start, end) in regions:
        subclip = input_video.subclip(start, end)
        subclips.append(subclip)
        last_end = end

    # return the concatenated videoclip to the 
    return concatenate_videoclips(subclips)

# Function to find the range of the subtitles in seconds 
def srt_item_to_range(item):
    start_s = item.start.hours*60*60 + item.start.minutes*60 + item.start.seconds + item.start.milliseconds/1000.
    end_s = item.end.hours*60*60 + item.end.minutes*60 + item.end.seconds + item.end.milliseconds/1000.
    return start_s, end_s

# Function to convert srt file to document in such a way that each sentence starts with '(sentence no)'
# It also removes all the unwanted stray elements in the srt file 
def srt_to_doc(srt_file):
    text = ''
    for index, item in enumerate(srt_file):
        ##print(item.text)
        if item.text.startswith("["): continue
        text += "(%d) " % index
        text += item.text.replace("\n", "").strip("...").replace(".", "").replace("?", "").replace("!", "")
        text += ". "
    return text

def total_duration_of_regions(regions):
    totalT=0
    for i in range(len(regions)):
        if(((regions[i])[1]-(regions[i])[0]) > 0):
            totalT=totalT+(regions[i])[1]-(regions[i])[0]
    return totalT
    #return sum(list(map(lambda rangeValue : rangeValue[1]-rangeValue[0] , regions)))

def summarize(srt_file, summarizer, n_sentences, language, bonusWords, stigmaWords):
    # Converting the srt file to a plain text document and passing in to Sumy library(The text summarization library) functions.
    ##print(srt_to_doc(srt_file))
    parser = PlaintextParser.from_string(srt_to_doc(srt_file), Tokenizer(language))
    
    if(summarizer == 'ED'):
        summarizer = EdmundsonSummarizer()

        with open(bonusWords,"r+") as f:
            bonus_wordsList = f.readlines()
            bonus_wordsList = [x.strip() for x in bonus_wordsList]
            f.close()
        with open(stigmaWords,"r+") as f:
            stigma_wordsList = f.readlines()
            stigma_wordsList = [x.strip() for x in stigma_wordsList]
            f.close()

        summarizer.bonus_words = (bonus_wordsList)
        summarizer.stigma_words = (stigma_wordsList)
        summarizer.null_words = get_stop_words(language)
    else:
        stemmer = Stemmer(language)
        summarizer = SUMMARIZERS[summarizer](stemmer)
        summarizer.stop_words = get_stop_words(language)

    ret = []
    summarizedSubtitles = []
    print()
    # Now the the document passed is summarized and we can access the filtered sentences along with the no of sentence
    for sentence in summarizer(parser.document, n_sentences):
        #print(sentence)
        # Index of the sentence
        index = int(re.findall("\(([0-9]+)\)", str(sentence))[0])
        # Using the index we determine the subtitle to be selected
        item = srt_file[index]

        summarizedSubtitles.append(item)

        # add the selected subtitle to the result array
        ret.append(srt_item_to_range(item))

    return ret,summarizedSubtitles

def find_summary_regions(srt_filename, summarizer, duration, language ,bonusWords,stigmaWords):
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
    
    directory = "./media/documents/"+str(summarizer)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory,"summarizedSubtitle.srt")
    with open(path,"w+") as sf:
        for i in range(0,len(summarizedSubtitles)):
            sf.write(str(summarizedSubtitles[i]))
            sf.write("\n")
    sf.close()

    # return the resulant summarized subtitle array
    return summary


def summarizeVideo(summType,summTime,bonusWords,stigmaWords,videoDwldURL):

    item = dwldVideo(videoDwldURL)
    # print("Enter the video filename")
    video=item[0]
    # print("Enter the subtitle name ")
    subtitle=item[1]

    # print("Enter summarizer name ")
    summarizerName=summType
    duration=int(summTime)
    language='english'
    regions = find_summary_regions(subtitle,
                                   summarizer=summarizerName,
                                   duration=duration,
                                   language=language,
                                   bonusWords=bonusWords,
                                   stigmaWords=stigmaWords
                                   )
    print((regions[-1])[1])
    if((regions[-1])[1]==0):
        regions = regions[:-1]
    summary = create_summary(video,regions)
    # Converting to video 
    base, ext = os.path.splitext(video)
    dst = "{0}_".format(base)
    dst = dst+str(summarizerName)+"_summarized.mp4"
    summary.to_videofile(
        dst,
        codec="libx264", 
        temp_audiofile="temp.m4a",
        remove_temp=True,
        audio_codec="aac",
    )
    return dst