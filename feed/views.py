from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import Storage

from .models import Photo

from .email_handler import readmail



# Create your views here.

def index(request):
    latest_photo_list = Photo.objects.order_by("uploaded")
    context = {
        'latest_photo_list': latest_photo_list
    }
    mail()
    return render(request, 'feed/index.html', context)


def mail():
    readmail()
    return None