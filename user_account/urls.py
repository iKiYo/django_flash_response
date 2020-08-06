from django.urls import path

from .views import SignupPageView, DashboardView


urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('', DashboardView.as_view(), name='dashboard'),
]
