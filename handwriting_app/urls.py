from django.urls import path
from . import views

app_name = 'handwriting'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_text_file, name='upload'),
    path('convert/<uuid:conversion_id>/', views.process_conversion, name='process_conversion'),
    path('result/<uuid:conversion_id>/', views.conversion_result, name='conversion_result'),
    path('download/<uuid:conversion_id>/<str:file_type>/', views.download_file, name='download_file'),
    path('api/conversion/<uuid:conversion_id>/status/', views.conversion_status, name='conversion_status'),
]