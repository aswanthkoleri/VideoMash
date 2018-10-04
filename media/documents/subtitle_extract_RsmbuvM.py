# Imports
import argparse
import os
import pysrt
import re
import subprocess
import sys
import math

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

def foo(n):
    return n*n;

def srt_item_to_range(item):
    print(str(item.start.hours)+" "+ str(item.start.minutes)+" "+str(item.start.seconds) +"---->> "+ str(item.end.hours)+" "+ str(item.end.minutes)+" "+str(item.end.seconds))
    start_s = item.start.hours*60*60 + item.start.minutes*60 + item.start.seconds + item.start.milliseconds/1000.
    end_s = item.end.hours*60*60 + item.end.minutes*60 + item.end.seconds + item.end.milliseconds/1000.
    return start_s, end_s
    
def main():
    subtitleName="sub.srt"
    subFile=pysrt.open(subtitleName)
    no = [1,2,3,4,5]
    result = map(srt_item_to_range,subFile)
    print(list(result))

main()