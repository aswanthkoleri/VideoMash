from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess
import os
import wave
import math
import audioop
import speech_recognition as sr
import pysrt
import six


def subtitle_gen(source,filename):
    print("filename :",filename) #"video."
    print("source :",source)
    # source="video.mp4"
    output="./media/documents/output.wav"
     # Extracting audio first
    # command = "ffmpeg -i " + source +" -c:a aac -b:a 128k output.wav"
    rate=16000
    command = ["ffmpeg", "-y", "-i", source,
               "-ac", str(1), "-ar", str(rate),
               "-loglevel", "error", output]
    # subprocess.call(command, shell=True)
    use_shell = True if os.name == "nt" else False
    subprocess.check_output(command, stdin=open(os.devnull), shell=use_shell)
    # splitAudio("output.wav")
    # Finding the speech regions based on silence
    regions=find_speech_regions(output)
    print(regions)
    # Now Convert this regions to text
    subtitles=speechToText(output,regions)
    # Now create srt file
    formattedSrt=srt_formatter(subtitles)
    # save as example "video.srt"
    dest="./media/documents/"+filename+"srt"
    with open(dest, 'wb') as output_file:
        output_file.write(formattedSrt.encode("utf-8"))

def main():
    source="video.mp4"
    output="output.wav"
     # Extracting audio first
    # command = "ffmpeg -i " + source +" -c:a aac -b:a 128k output.wav"
    rate=16000
    command = ["ffmpeg", "-y", "-i", source,
               "-ac", str(1), "-ar", str(rate),
               "-loglevel", "error", output]
    # subprocess.call(command, shell=True)
    use_shell = True if os.name == "nt" else False
    subprocess.check_output(command, stdin=open(os.devnull), shell=use_shell)
    # splitAudio("output.wav")
    # Finding the speech regions based on silence
    regions=find_speech_regions(output)
    print(regions)
    # Now Convert this regions to text
    subtitles=speechToText(output,regions)
    # Now create srt file
    formattedSrt=srt_formatter(subtitles)
    # save as example "video.srt"
    dest="video.srt"
    with open(dest, 'wb') as output_file:
        output_file.write(formattedSrt.encode("utf-8"))

def speechToText(output,regions):
    r=sr.Recognizer()
    subtitles=[]
    audioFile = sr.AudioFile(output)
    for region in regions:
        duration=region[1]-region[0]
        offset=region[0]
        start=region[0]
        end=region[1]
        print(duration)
        print(offset)
        with audioFile as source:
            audio = r.record(source,duration=duration,offset=offset)
        WIT_API_KEY="BAVSMY4FFLS6JWCUTML7JYGVOZWA5Q4E"
        result=r.recognize_wit(audio,WIT_API_KEY)
        print("Generated Subtitle")
        print(result)
        subtitle=((start,end),result)
        subtitles.append(subtitle)
    return subtitles


# print(result)
def srt_formatter(subtitles, padding_before=0, padding_after=0):
    """
    Serialize a list of subtitles according to the SRT format, with optional time padding.
    """
    sub_rip_file = pysrt.SubRipFile()
    for i, ((start, end), text) in enumerate(subtitles, start=1):
        item = pysrt.SubRipItem()
        item.index = i
        item.text = six.text_type(text)
        print(item.text)
        if(item.text):
            item.start.seconds = max(0, start - padding_before)
            item.end.seconds = end + padding_after
            sub_rip_file.append(item)
    return '\n'.join(six.text_type(item) for item in sub_rip_file)


def splitAudio(audioFile):
    audio=AudioSegment.from_wav(audioFile)
    chunks = split_on_silence(audio,
    silence_thresh=-16
    )
    for i, chunk in enumerate(chunks):
        #Normalize each audio chunk
        normalized_chunk = match_target_amplitude(chunk, -20.0)
        #Export audio chunk with new bitrate
        print("exporting chunk{0}.mp3".format(i))
        normalized_chunk.export("./chunk{0}.wav".format(i), bitrate='128k', format="wav")

def percentile(arr, percent):
    arr = sorted(arr)
    index = (len(arr) - 1) * percent
    floor = math.floor(index)
    ceil = math.ceil(index)
    if floor == ceil:
        return arr[int(index)]
    low_value = arr[int(floor)] * (ceil - index)
    high_value = arr[int(ceil)] * (index - floor)
    return low_value + high_value

def find_speech_regions(filename, frame_width=4096, min_region_size=0.5, max_region_size=6): # pylint: disable=too-many-locals
    reader = wave.open(filename)
    sample_width = reader.getsampwidth()
    rate = reader.getframerate()
    n_channels = reader.getnchannels()
    chunk_duration = float(frame_width) / rate

    n_chunks = int(math.ceil(reader.getnframes()*1.0 / frame_width))
    energies = []

    for _ in range(n_chunks):
        chunk = reader.readframes(frame_width)
        energies.append(audioop.rms(chunk, sample_width * n_channels))

    threshold = percentile(energies, 0.2)

    elapsed_time = 0

    regions = []
    region_start = None

    for energy in energies:
        is_silence = energy <= threshold
        max_exceeded = region_start and elapsed_time - region_start >= max_region_size

        if (max_exceeded or is_silence) and region_start:
            if elapsed_time - region_start >= min_region_size:
                regions.append((region_start, elapsed_time))
                region_start = None

        elif (not region_start) and (not is_silence):
            region_start = elapsed_time
        elapsed_time += chunk_duration
    return regions


# main()
