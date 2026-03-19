from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('upload', views.upload_resume),
    path('dashboard', views.dashboard),
    path('generate-resume', views.generate_resume),
    path('download-resume', views.download_resume),
    path('pricing', views.pricing),
    path('subscription-history', views.subscription_history),
    path('toggle-auto-renew', views.toggle_auto_renew),
    path('upgrade', views.upgrade_to_premium),
    path('create-razorpay-order', views.create_razorpay_order),
    path('verify-payment', views.verify_payment),
    path('razorpay-webhook', views.razorpay_webhook),
]