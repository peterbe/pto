from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='dates.home'),
    url(r'^notify/$', views.notify, name='dates.notify'),
    url(r'^(?P<pk>\d+)/hours/$', views.hours, name='dates.hours'),
    url(r'^(?P<pk>\d+)/sent/$', views.emails_sent, name='dates.emails_sent'),
    url(r'^list/$', views.list_, name='dates.list'),
    url(r'^list/csv/$', views.list_csv, name='dates.list_csv'),
    url(r'^list/json/$', views.list_json, name='dates.list_json'),
    url(r'^calendar/events/$', views.calendar_events,
        name='dates.calendar_events'),
    url(r'^following/$', views.following, name='dates.following'),
    url(r'^following/save/$', views.save_following, name='dates.save_following'),
    url(r'^following/save/unfollow/$', views.save_unfollowing, name='dates.save_unfollowing'),
)
