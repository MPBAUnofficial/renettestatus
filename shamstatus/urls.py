from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from observer.views import celery_test, check_global_status, just_another_test, \
    status

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shamstatus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'celery_test', celery_test),
    url(r'asd', just_another_test),
    url(r'test', check_global_status),
    url(r'^status', status),

    url(r'^admin/', include(admin.site.urls)),
)
