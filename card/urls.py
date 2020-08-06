from django.urls import path

from .views import (
    CardImport, UploadSuccessedView,
    CardCreateView, CardUpdateView, CardListView,
    CardDetailView, CardDeleteView, SearchResultListView
)

urlpatterns = [
    path('search/', SearchResultListView.as_view(), name='search_results'),
    path('card_new', CardCreateView.as_view(), name='card_new'),
    path('card_delete/<uuid:pk>',
         CardDeleteView.as_view(), name='card_delete'),
    path('card_edit/<uuid:pk>',
         CardUpdateView.as_view(), name='card_edit'),
    path('card_detail/<uuid:pk>',
         CardDetailView.as_view(), name='card_detail'),
    path('card_list',
         CardListView.as_view(), name='card_list'),
    path('card_upload_successed',
         UploadSuccessedView.as_view(), name='card_upload_successed'),
    path('card_upload', CardImport.as_view(), name='card_upload'),
]
