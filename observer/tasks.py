from __future__ import absolute_import
from celery import shared_task
from .targets import TARGETS_LIST
from .models import RequestLog
from .utils import update_status

@shared_task
def celery_test(name):
    from time import sleep
    sleep(5)
    return "hello, " + name


@shared_task
def investigate_error(target, level=0, force_new_global_status=False):
    s = target.status()
    if s == 200:
        # check again in 5 seconds
        status.apply_async(args=[target], countdown=5)
    else:
        if level == 0:
            update_status.delay(target, 2, force_new_global_status)
            investigate_error.apply_async(args=[target, 1], countdown=5)
        if level == 1:
            update_status.delay(target, 3, force_new_global_status)
            investigate_error.apply_async(args=[target, 1], countdown=30)


@shared_task
def status(target, force_new_global_status=False):
    """
    Checks for the status of a service.
    """
    s = target.status()
    if s == 200:
        update_status.delay(target, 0, force_new_global_status)
    else:
        investigate_error.delay(target, 0, force_new_global_status)


@shared_task
def global_status():
    s = []
    for target in TARGETS_LIST:
        s.append(str(status.delay(target)))
    return s