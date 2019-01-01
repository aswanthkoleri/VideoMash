from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings

def index(request):
    return render(request,'index.html')
