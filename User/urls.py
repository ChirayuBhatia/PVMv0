from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('login/', views.login_page, name="LogIn"),
    path('logout/', views.logout_page, name="LogOut"),
    path('register/', views.register_page, name="Register"),
    path('uploadfiles/', views.upload_files, name="UploadFiles"),
    path('qr/<int:fid>', views.qr_image, name="qrcode"),
    path('myQRs/', views.qrs_page, name="myQRs"),
    path('printsettings/<int:fid>/', views.printsettings, name="PrintSettings"),
    path('res/', views.pay_status, name="paymentStatus"),
    path('activate/<uidb64>/<token>', views.verify_mail, name='activate'),
]
