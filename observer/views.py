from django.http import HttpResponse
from django.shortcuts import render
from observer import tasks
from models import GlobalStatusMessage
from utils import get_global_status, get_latest_logs


def check_global_status(request):
    s = tasks.global_status.delay()
    return HttpResponse('{0}'.format(s.get()))


def global_statuses_history(request):
    return render(
        request,
        'history.html', {
            'statuses': GlobalStatusMessage.objects.all().order_by('time')
        }
    )


def status(request):
    return render(
        request,
        'status.html', {
            'global_status': get_global_status(),
            'latest_logs': get_latest_logs()
        }
    )
