from django.http import HttpResponse
from django.shortcuts import render
from observer import tasks
from models import GlobalStatusMessage
from utils import get_global_status, get_latest_logs
from django.core.cache import cache
import time


def check_global_status(request):
    if (time.time() - cache.get('last_global_check', 0)) > 10:
        s = tasks.global_status.delay()
        cache.set('last_global_check', time.time())
        return HttpResponse('{0}'.format(s))
    return HttpResponse('slow down!')


def global_statuses_history(request):
    return render(
        request,
        'history.html', {
            'statuses': GlobalStatusMessage.objects.all().order_by('time')
                        .reverse()[:50]
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
