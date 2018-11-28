from django.conf.urls import url
from .views import (
    UserActivateAPIView,
    UserCreateAPIView,
    UserListCreateAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserPasswordChangeAPIView,
    UserPasswordResetAPIView,
    UserPasswordResetTokenAPIView,
    UserRetrieveUpdateAPIView,
)


urlpatterns = [
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'),
    url(r'^logout/$', UserLogoutAPIView.as_view(), name='logout'),
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^user/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        UserActivateAPIView.as_view(), name='user-activate'),
    url(r'^user/password-change/$', UserPasswordChangeAPIView.as_view(), name='password-change'),
    url(r'^user/password-reset/$', UserPasswordResetAPIView.as_view(), name='password-reset'),
    url(r'^user/password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        UserPasswordResetTokenAPIView.as_view(), name='password-reset-token'),
    url(r'^users/$', UserListCreateAPIView.as_view(), name='user-list'),
    url(r'^users/(?P<pk>\d+)/$', UserRetrieveUpdateAPIView.as_view(), name='user-retrieve-update'),
]
