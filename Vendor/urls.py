from django.urls import include, path
from .views import FileAPIView, QRCheckView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('check_qr/', QRCheckView.as_view()),
    path('print/', FileAPIView.as_view()),
]
