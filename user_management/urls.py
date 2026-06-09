from django.urls import path
from .views import LoginView, TokenRefreshView, LogoutView

urlpatterns = [
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
]
