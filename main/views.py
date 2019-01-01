# 1. Make subtitles for videos
# 2. Combine videos in one frame
# 3. Try to do unsupervised algo's

from django.shortcuts import render,redirect
from .models import Document
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import DocumentForm
from django.conf import settings
from .videoSummarizer import summarizeVideo
from .combinedVideoGen import createComVideo
from .learning import combined
from SubtitleGen.subtitle import subtitle_gen
# Create your views here.
def main(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        # print(form)
        videoName=str(request.FILES['videoFile']).replace(' ','_')
        videoURL='.'+str(settings.MEDIA_URL)+'documents/'+videoName
        flag=False
        try:
            if(request.FILES['subtitleFile']):
                print("Subtitles already given")
                subtitleName=str(request.FILES['subtitleFile']).replace(' ','_')
                subtitleURL='.'+str(settings.MEDIA_URL)+'documents/'+subtitleName
        except:
            print("There are no subtitles!We Need to be generated")
            flag=True
        # print("Subt url ::: "+str(subtutleURL));
        # print("Video url ::: "+str(videoURL));
        #if bonusWordsFile and stigmaWordsFile aren't uploaded, default files will be chosen.
        bonusWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('bonusWordsFile','dummy.txt'))
        stigmaWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('stigmaWordsFile','dummy.txt'))
        if form.is_valid():
            summType = form.cleaned_data['summarizeType']
            summarizationTime = form.cleaned_data['summarizationTime']
            form.save()
            if(flag):
                #generate subtitles parameter1 source and parameter2 file name ("video.") and srt file will be video.srt
                subtitle_gen('.'+str(settings.MEDIA_URL)+'documents/'+videoName,videoName[:-3])
                subtitleURL='.'+str(settings.MEDIA_URL)+'documents/'+videoName[:-3]+'srt'
            # print(videoURL)
            if 'combinedVideo' in request.POST:
                lexRank=request.POST.get('lexRank')
                lsa=request.POST.get('lsa')
                luhn=request.POST.get('luhn')
                textRank=request.POST.get('textRank')
                summTypes=[lexRank,lsa,luhn,textRank]
                print("---------------------------------------")
                print(request.POST.get('weights'))
                print("---------------------------------------")
                best="none"
                worst="none"
                if(request.POST.get('weights')=='weights'):
                    [videoURL,subURL,best,worst]=combined(videoURL,subtitleURL,bonusWordsURL,summTypes)
                else:
                    [videoURL,subURL]=createComVideo(videoURL,subtitleURL,bonusWordsURL,summTypes)
                return render(request,'download.html',{ 'videoURL' : videoURL , 'subURL' : subURL ,'best':best,'worst':worst})
            else:

                URL=summarizeVideo(videoURL,subtitleURL,summType,summarizationTime,bonusWordsURL,stigmaWordsURL)
                # print(downloadURL)
                videoURL=URL+".mp4"
                subURL=URL+".srt"
                best="none"
                worst="none"
                return render(request,'download.html',{ 'videoURL' : videoURL , 'subURL' : subURL,'best':best,'worst':worst})
    else:
        form = DocumentForm()
        return render(request, 'main.html', {
            'form': form
        })
