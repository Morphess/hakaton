from django.urls import path
from .views import *

urlpatterns = [
    path('pdfs/', pdf_list, name='pdf_list'),
    path('chat/', chat, name='chat'),
    path('delete_pdf/<int:pdf_id>/', delete_pdf, name='delete_pdf'),
    path('convert_pdf_to_text/<int:pdf_id>/', convert_pdf_to_text, name='convert_pdf_to_text'),
]


