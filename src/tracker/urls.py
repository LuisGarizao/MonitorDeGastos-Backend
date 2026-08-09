from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from tracker import views

urlpatterns = [
    path("signup", views.Register.as_view()),
    path("users/all", views.UsersView.as_view()),
    path("user/<uuid:pk>", views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)