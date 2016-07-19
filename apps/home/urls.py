from django.conf.urls import url

from .views import authenticated_home, show_result


urlpatterns = [
    url(r'^output/(?P<srvr>\w+)/(?P<resource>\w+)/(?P<hi_fld>\w+)/$',
        show_result,
        name="output"),
    url(r'^',
        authenticated_home,
        name='home'),
]
