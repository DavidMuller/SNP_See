from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SNP_See.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^SNP_Feature_View/', include('SNP_Feature_View.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
