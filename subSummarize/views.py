from django.shortcuts import render,redirect
from .models import Document
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import DocumentForm
from django.conf import settings
from .videoSummarizer import summarizeVideo
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
            downloadURL=summarizeVideo(summType,summarizationTime,bonusWordsURL,stigmaWordsURL,videoDwldURL)
            # print(downloadURL)
            return render(request,'subdownload.html',{ 'downloadURL' : downloadURL })
    else:
        print("=========================================")
        form = DocumentForm()
    return render(request, 'subSummarize.html', {
        'form': form
    })
