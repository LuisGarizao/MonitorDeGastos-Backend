from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from tracker import views

urlpatterns = [
    path("users/all", views.UsersView.as_view()),
    path("plans/all", views.PlanList.as_view()),
    path("signup", views.Register.as_view()),
    
    path("user/plans", views.UserPlansList.as_view()),
    
    path("user/<uuid:pk>", views.UserDetail.as_view()),
    path("plan/<int:pk>", views.PlanDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)