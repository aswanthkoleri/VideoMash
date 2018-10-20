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
        # print(form)
        # print("******************")
        # print(str(request.FILES['videoFile']))
        # print("******************")
        videoURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES['videoFile'])
        subtutleURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES['subtitleFile'])
        # print("Subt url ::: "+str(subtutleURL));
        # print("Video url ::: "+str(videoURL));
        #if bonusWordsFile and stigmaWordsFile aren't uploaded, default files will be chosen.
        bonusWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('bonusWordsFile','defaultBonusWords.txt'))
        stigmaWordsURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES.get('stigmaWordsFile','defaultStigmaWords.txt'))
        
        if form.is_valid():
            summType = form.cleaned_data['summarizeType']
            summarizationTime = form.cleaned_data['summarizationTime']
            form.save()
            # print(videoURL)
            downloadURL=summarizeVideo(videoURL,subtutleURL,summType,summarizationTime,bonusWordsURL,stigmaWordsURL)
            # print(downloadURL)
            return render(request,'download.html',{ 'downloadURL' : downloadURL })
    else:
        form = DocumentForm()
    return render(request, 'main.html', {
        'form': form
    })
