from django.http import HttpResponse
from django.shortcuts import render
from observer import tasks
from models import Target
from utils import get_global_status, get_latest_logs


def check_global_status(request):
    s = tasks.global_status.delay()
    return HttpResponse('{0}'.format(s.get()))


def status(request):
    return render(request, 'status.html', {'global_status': get_global_status(),
                                           'latest_logs': get_latest_logs()
                                           })
