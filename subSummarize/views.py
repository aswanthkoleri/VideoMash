from django.shortcuts import render,redirect
from .models import Document
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import DocumentForm
from django.conf import settings
from .videoSummarizer import summarizeVideo
from .combinedVideoGen import createComVideo
from .learning import *
# Create your views here.

def main(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        #if bonusWordsFile and stigmaWordsFile aren't uploaded, default files will be chosen.
        bonusWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('bonusWordsFile','dummy.txt'))
        stigmaWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('stigmaWordsFile','dummy.txt'))

        if form.is_valid():
            videoDwldURL = form.cleaned_data['videoDwldURL']
            summType = form.cleaned_data['summarizeType']
            summarizationTime = form.cleaned_data['summarizationTime']
            form.save()
            # print(videoURL)
            if 'combinedVideo' in request.POST:
                lexRank=request.POST.get('lexRank')
                lsa=request.POST.get('lsa')
                luhn=request.POST.get('luhn')
                textRank=request.POST.get('textRank')
                summTypes=[lexRank,lsa,luhn,textRank]
                best="none"
                worst="none"
                if(request.POST.get('weights')=='weights'):
                    [downloadURL,subURL,best,worst]=combined(videoDwldURL,bonusWordsURL,summTypes)
                else:
                    [downloadURL,subURL]=createComVideo(videoDwldURL,bonusWordsURL,summTypes)
                return render(request,'subdownload.html',{ 'downloadURL' : downloadURL,'best':best,'worst':worst})
            else:
                downloadURL=summarizeVideo(summType,summarizationTime,bonusWordsURL,stigmaWordsURL,videoDwldURL)
                # print(downloadURL)
                return render(request,'subdownload.html',{ 'downloadURL' : downloadURL })
    else:
        print("=========================================")
        form = DocumentForm()
        return render(request, 'subSummarize.html', {
            'form': form
        })
