
from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
	# ex: /polls/
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # ex: /polls/5/
    url(r'^ajax_hostnames/$', views.hostnames, name='hostnames'),
    # ex:API /hosts/5/
    url(r'^api/hosts/(?P<stat_id>\w+)/$', views.api_host_stats, name='api_host_stats'),
    # ex:API /hosts/5/ trafico de interfaces
    url(r'^api/traffic/(?P<hostname>[]\w\.\d]+)/$', views.api_traffic, name='api_traffic'),
    url(r'^traffic_interface/$', views.traffic_interface, name='traffic_interface'),
    # ex:API /hosts/5/Sesion Logs
    url(r'^session_logs/$', views.session_logs, name='session_logs'),
    url(r'^ajax_mcast_flows/$', views.ajax_mcast_flows, name='ajax_mcast_flows'),
    url(r'^script_logs/$', views.script_logs, name='script_logs'),
    url(r'^compare_mcast/$', views.compare_mcast, name='compare_mcast'),
    # ex: DEfs Routing
    url(r'^backup/$', views.backup, name='backup'),
    url(r'^get_name/$', views.get_name, name='get_name'),
    url(r'^delete_device/$', views.delete_device, name='delete_device'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^show_logs/$', views.show_logs, name='show_logs'),
    # ex: /polls/5/
    url(r'^(?P<option_id>[0-9]+)/$', views.script_type, name='script_type'),
    # ex: /polls/5/results/
    #url(r'<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    url(r'/about/', views.about, name='about'),
]
