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
        print(form)
        videoURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES['videoFile'])
        subtutleURL='.'+str(settings.MEDIA_URL)+'documents/'+str(request.FILES['subtitleFile'])
        
        if form.is_valid():
            summType = form.cleaned_data['summarizeType']
            summarizationTime = form.cleaned_data['summarizationTime']
            downloadURL=summarizeVideo(videoURL,subtutleURL,summType,summarizationTime)
            print(downloadURL)
            return render(request,'download.html',{ 'downloadURL' : downloadURL })
    else:
        form = DocumentForm()
    return render(request, 'main.html', {
        'form': form
    })
