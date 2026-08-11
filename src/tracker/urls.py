from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from tracker import views

urlpatterns = [
    path("signup", views.Register.as_view()),
    path("me/profile", views.UserDetail.as_view()),
    path("me/expenses", views.ExpenseList.as_view()),
    path("me/expenses/stats", views.ExpenseStats.as_view()),
    path("me/expenses/<int:pk>", views.ExpenseDetail.as_view()),
    
    # path("admin/users/all", views.UsersView.as_view()),
    # path("admin/user/<uuid:pk>", views.UserDetail.as_view()),
    # path("admin/user/<uuid:pk>/expenses", views.ExpenseList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)