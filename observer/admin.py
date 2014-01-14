from django.contrib import admin
from models import RequestLog, GlobalStatusMessage, Target, StatusMessages, StatusMessage

# Register your models here.
admin.site.register(RequestLog)
admin.site.register(GlobalStatusMessage)
admin.site.register(Target)
admin.site.register(StatusMessages)
admin.site.register(StatusMessage)
