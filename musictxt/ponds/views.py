import http
from http.client import HTTPResponse
from django.shortcuts import render
import subprocess
import sys
from .models import Pond
from django.http import HttpResponse

# for file uploading
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your views here.

def landing(request):
    return render(request, 'ponds/landing.html')


def homepage(request):
    ponds = Pond.objects
    if request.method == 'GET':
        fname = request.GET['fname']
    return render(request, 'ponds/home.html', {'ponds': ponds, 'fname': fname})


def simple_upload(request):
    print(request.FILES)
    fname = str(list(request.FILES.keys())[0])
    if request.method == 'POST' and request.FILES[fname]:
        fs = FileSystemStorage()
        if fs.exists(fname+'.txt'):
            fs.delete(fname+'.txt')
        filename = fs.save(fname+'.txt', request.FILES[fname])
        uploaded_file_url = fs.url(filename)
    return render(request, 'ponds/simple_uploaded.html', {'uploaded_file_url': uploaded_file_url, 'fname': fname})


def update(request):
    ponds = Pond.objects
    if request.method == 'POST' and request.POST['data']:
        data = request.POST['data']
        fname = request.POST['fname']
        file = open("media/"+fname+".txt", "w")
        file.write(data)
        file.close()
        # convert txt to ly
        subprocess.run(["python3", "ponds/static/MusicTXT.py", "-s", fname])
        # convert ly to pdf+midi, then move to the corresponding directory
        # subprocess.run(["lilypond", "media/"+fname+".ly"])
        # subprocess.run(["mv", fname+".pdf", "media"])
        # subprocess.run(["mv", fname+".midi", "media"])
        return HttpResponse("pdf generated")
    else:
        return HttpResponse("pdf failed to generate")


def error_404(request, exception):
    data = {}
    return render(request, 'ponds/404.html', data)
