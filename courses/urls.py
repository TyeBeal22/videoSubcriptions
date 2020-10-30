from django.urls import path
from django.conf.urls import url
from .views import CourseListView, CourseDetailView, LessonDetailView, VideoDetailView, embedded_signing_ceremony, get_access_code, auth_login, sign_complete


app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<slug>', CourseDetailView.as_view(), name='detail'),
    path('<course_slug>/<lesson_slug>',
         LessonDetailView.as_view(), name='lesson-detail'),
    path("<course_slug>/<video_slug>/",
         VideoDetailView.as_view(), name='video-detail'),
    url(r'^get_signing_url/$', embedded_signing_ceremony, name='get_signing_url'),
    url(r'^get_access_code/$', get_access_code, name='get_access_code'),
    url(r'^auth_login/$', auth_login, name='auth_login'),
    url(r'^sign_completed/$', sign_complete, name='sign_completed'),
]
