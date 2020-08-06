from django.urls import path

from .views import (
    HomePageView, ExerciseView,
)

urlpatterns = [
    path('exercise', ExerciseView.as_view(), name='exercise'),
    path('', HomePageView.as_view(), name='home'),
]
