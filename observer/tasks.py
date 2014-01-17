from __future__ import absolute_import

from celery import shared_task
from celery.task import periodic_task
from celery.schedules import crontab
from django.conf import settings
from .targets import TARGETS_LIST
from .models import RequestLog, GlobalStatusMessage
from shamstatus.settings import SYSTEM_ERROR_MESSAGES, RENETTE_ADMINS
from .utils import get_latest_logs
from django.core.mail import send_mail


@shared_task
def update_status(target, code, force_new_global_status=False):
    t = target.get_target_model()

    try:
        latest_log = RequestLog.objects.filter(target=t).latest('time')
    except RequestLog.DoesNotExist:
        latest_log = None

    # I know, this is _really_ ugly
    if latest_log is None or code > latest_log.status_code or \
            (code == 0 and latest_log.status_code != 0):
        RequestLog. \
            objects.create(target=t, response_time=0, status_code=code,
                           status_message=t.status_messages.get_status(code))
        update_global_status.delay(force_new_global_status)


@shared_task
def update_global_status(force_new=False):
    global_status_code = max([log.status_code for log in get_latest_logs()])
    latest_message = None
    # noinspection PyBroadException
    try:
        latest_message = GlobalStatusMessage.objects.latest('time')
    except:
        force_new = True

    if force_new or latest_message.code != global_status_code:
        GlobalStatusMessage.objects.create(
            code=global_status_code,
            message=SYSTEM_ERROR_MESSAGES[global_status_code]
        )
        send_mail(
            'Renette\'s status changed to {0}'
            .format(SYSTEM_ERROR_MESSAGES[global_status_code]),
            'Baci e abbracci',
            settings.EMAIL_HOST_USER,
            RENETTE_ADMINS,
            fail_silently=True
        )


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


@periodic_task(run_every=crontab(minute="*/30"))
def global_status_periodic():
    # maybe it would be a better idea to set 'periodic_task' on the
    # global_status task?
    global_status.delay()


@periodic_task(run_every=crontab(minute=0, hour=0))
def daily_check():
    update_global_status.delay(force_new=True)
