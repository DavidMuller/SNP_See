from django.conf.urls import patterns, url

from SNP_Feature_View import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/$', views.about, name='about'),
        url(r'^contact/$', views.contact, name='contact'),
        url(r'^under_construction/$', views.under_construction, name='under_construction'),
        url(r'^feature_view/$', views.feature_view_home, name='feature_view_home'),
        url(r'^data_set_characterization/$', views.data_set_characterization, name='data_set_characterization'),
        url(r'^feature_view/sample_data_selector/$', views.feature_view_sample_data_selector, name='feature_view_sample_data_selector'),
        url(r'^feature_view/select_phenotypes/$', views.feature_view_select_phenotypes, name='feature_view_select_phenotypes'),
        url(r'^feature_view/load_session_data/(?P<file_name>.*)/$', views.feature_view_load_session_data, name='feature_view_load_session_data'),
        url(r'^feature_view/visual_browser/highlight/(?P<chromosome_num>.*)/(?P<highlight>.*)/$', views.visual_browser, name='visual_browser'),
        url(r'^feature_view/visual_browser/(?P<phenotype>.*)/$', views.feature_view_within_visual_browser, name='feature_view_within_visual_browser'),
        url(r'^feature_view/visual_browser/(?P<phenotype>.*)/not_enough_data/$', views.feature_view_within_visual_browser_not_enough_data, name='feature_view_within_visual_browser_not_enough_data'),
        url(r'^feature_view/(?P<phenotype>.*)/$', views.feature_view, name='feature_view'),
        url(r'^feature_view/(?P<phenotype>.*)/not_enough_data/$', views.feature_view_not_enough_data, name='feature_view_not_enough_data'),
)