from models import RequestLog, GlobalStatusMessage
from targets import TARGETS_LIST


def get_latest_logs():
    return [RequestLog.objects.filter(target=t.get_target_model())
            .latest('time') for t in TARGETS_LIST]


def get_global_status():
    return GlobalStatusMessage.objects.latest('time')