from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from observer.views import check_global_status, status, global_statuses_history

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shamstatus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^test', check_global_status),
    url(r'^status', status),
    url(r'^history', global_statuses_history),

    url(r'^admin/', include(admin.site.urls)),
)
