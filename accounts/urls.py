from django.urls import path
from .views import RegisterView, BanUserView, UnbanUserView, UserListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/ban/", BanUserView.as_view(), name="ban-user"),
    path("users/<int:pk>/unban/", UnbanUserView.as_view(), name="unban-user"),
]