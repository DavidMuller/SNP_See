from django.conf.urls import patterns, url

from SNP_Feature_View import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index')
)
