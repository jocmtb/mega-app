
from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', views.index2, name='index2'),
    url(r'^main/$', views.index_xr, name='index_xr'),
    url(r'^add_device/$', views.add_device, name='add_device'),
    url(r'^delete_device/$', views.delete_device_xr, name='delete_device_xr'),
    url(r'^backup/$', views.backup_xr, name='backup_xr'),
    url(r'^session_logs/$', views.session_logs_xr, name='session_logs_xr'),
    url(r'^xr_mcast/$', views.xr_mcast, name='xr_mcast'),
    url(r'^traffic_interface/$', views.traffic_interface_xr, name='traffic_interface_xr'),
    url(r'^dashboard/$', views.dashboard_xr, name='dashboard_xr'),
    url(r'^arp_info/$', views.arp_info_xr, name='arp_info_xr'),
    url(r'^join_igmp/$', views.join_igmp_xr, name='join_igmp_xr'),
    #API Functions defitions URL
    url(r'^ajax_hostnames/$', views.hostnames_xr, name='hostnames_xr'),
    url(r'^api/hosts/(?P<stat_id>\w+)/$', views.api_host_stats_xr, name='api_host_stats_xr'),
    url(r'^script_logs/$', views.script_logs_xr, name='script_logs_xr'),
    url(r'^script_logs/(?P<hostname>[]\w\.\d]+)/$', views.script_logs_by_host_xr, name='script_logs_by_host_xr'),
    url(r'^download/(?P<path>.*)$', views.download_xr, name='download_xr'),
    url(r'^api/traffic2/(?P<hostname>[]\w\.\d]+)/$', views.api_traffic_table_xr, name='api_traffic_table_xr'),
    url(r'^api/traffic/(?P<hostname>[]\w\.\d]+)/$', views.api_traffic_xr, name='api_traffic_xr'),
    url(r'^api/arp/data/(?P<hostname>[]\w\.\d]+)/$', views.api_arp_xr, name='api_arp_xr'),
    url(r'^ajax_mcast_flows/$', views.ajax_mcast_flows_xr, name='ajax_mcast_flows_xr'),
    url(r'^api/join/igmp/(?P<hostname>[]\w\.\d]+)/$', views.api_join_igmp_xr, name='api_join_igmp_xr'),
]
