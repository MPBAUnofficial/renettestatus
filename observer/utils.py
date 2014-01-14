from models import RequestLog, GlobalStatusMessage, Target
from shamstatus.settings import SYSTEM_ERROR_MESSAGES,\
    HIGHER_ERROR_CODE
from targets import TARGETS_LIST
from celery import shared_task

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
        RequestLog.\
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
        # todo: send mail?


def get_latest_logs():
    return [RequestLog.objects.filter(target=t.get_target_model())
            .latest('time') for t in TARGETS_LIST]


def get_global_status():
    return GlobalStatusMessage.objects.latest('time')