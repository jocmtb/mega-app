
from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^nx/$', views.index3, name='index3'),
    url(r'^example-q/$', views.example_q),
    url(r'^get-collections/$', views.get_collections),
    url(r'^list-collections/$', views.list_collections, name='list_collections'),
    url(r'^nxos/$', views.index_nxos, name='index_nxos'),
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^logout/$', views.logout_user, name='logout_user'),
	# ex: /polls/
    url(r'^d3_graph/$', views.d3_graph, name='d3_graph'),
    url(r'^d3_graph2/$', views.d3_graph2, name='d3_graph2'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/(?P<hostname>[]\w\.\d]+)/$', views.dashboard2, name='dashboard2'),
    # ex: /polls/5/
    url(r'^ajax_hostnames/$', views.hostnames, name='hostnames'),
    # ex:API /hosts/5/
    url(r'^api/hosts/(?P<stat_id>\w+)/$', views.api_host_stats, name='api_host_stats'),
    # ex:API /hosts/5/ trafico de interfaces
    url(r'^api/traffic2/(?P<hostname>[]\w\.\d]+)/$', views.api_traffic_table, name='api_traffic_table'),
    url(r'^api/traffic/(?P<hostname>[]\w\.\d]+)/$', views.api_traffic, name='api_traffic'),
    url(r'^api/arp/data/(?P<hostname>[]\w\.\d]+)/$', views.api_arp, name='api_arp'),
    url(r'^api/join/igmp/(?P<hostname>[]\w\.\d]+)/$', views.api_join_igmp, name='api_join_igmp'),
    url(r'^traffic_interface/$', views.traffic_interface, name='traffic_interface'),
    url(r'^arp_info/$', views.arp_info, name='arp_info'),
    url(r'^join_igmp/$', views.join_igmp, name='join_igmp'),
    # ex:API /hosts/5/Sesion Logs
    url(r'^session_logs/$', views.session_logs, name='session_logs'),
    url(r'^ajax_mcast_flows/$', views.ajax_mcast_flows, name='ajax_mcast_flows'),
    url(r'^script_logs/$', views.script_logs, name='script_logs'),
    url(r'^script_logs/(?P<hostname>[]\w\.\d]+)/$', views.script_logs_by_host, name='script_logs_by_host'),
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
    url(r'^download/(?P<path>.*)$', views.download, name='download'),
]
