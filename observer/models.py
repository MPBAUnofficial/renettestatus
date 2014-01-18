from django.core.exceptions import ValidationError
from django.db import models


def validate_status_code(code):
    if not code in range(5):
        raise ValidationError('{0} is not a valid code'.format(code))


class GlobalStatusMessage(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    code = models.IntegerField(validators=[validate_status_code])
    message = models.TextField()

    def get_readable_time(self):
        return '{t.day:02d}/{t.month:02d}/{t.year:02d} -' \
               ' {t.hour:02d}:{t.minute:02d}'.format(t=self.time)

    def __unicode__(self):
        return '{0}: {1}'.format(self.time, self.message)


class RequestLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    target = models.ForeignKey('Target')
    response_time = models.IntegerField(null=True, blank=True)  # in milliseconds
    status_code = models.IntegerField(validators=[validate_status_code])
    status_message = models.TextField()

    def __unicode__(self):
        return '[{0}] {1} -> {2}'.format(self.time, self.target.name, self.status_code)


class StatusMessage(models.Model):
    messages_group = models.ForeignKey('StatusMessages', default=1)
    message = models.TextField()
    code = models.IntegerField()

    def __unicode__(self):
        return '<{0}> "{1}"'.format(self.messages_group, self.message)

    class Meta:
        unique_together = (('code', 'messages_group'),)


class StatusMessages(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_status(self, code):
        try:
            return self.statusmessage_set.get(code=code).message
        except StatusMessage.DoesNotExist:
            return StatusMessages.objects.get(pk=1).get_status(code)


class Target(models.Model):
    name = models.TextField()
    url = models.URLField()
    method = models.CharField(max_length=10)
    status_messages = models.ForeignKey('StatusMessages', default=1)

    def __unicode__(self):
        return '{0}'.format(self.name)

    def get_status_code(self):
        latest_log = RequestLog.objects.filter(target=self).latest('time')
        return latest_log.status_code
