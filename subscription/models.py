from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Subscription(models.Model):

    PLAN_CHOICES = [
        ("FREE", "Free"),
        ("PREMIUM_MONTHLY", "Premium Monthly"),
        ("PREMIUM_YEARLY", "Premium Yearly")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="FREE")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=False)  # Auto-renew toggle
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

    def is_premium_active(self):
        if self.plan == "FREE":
            return False
        if self.end_date and timezone.now() > self.end_date:
            return False
        return self.is_active

    def get_days_remaining(self):
        """Returns the number of days remaining until subscription expires"""
        if not self.end_date:
            return 0
        remaining = self.end_date - timezone.now()
        days = remaining.days
        return max(0, days)

    def activate_premium(self, plan_type):
        self.plan = plan_type
        self.is_active = True
        if plan_type == "PREMIUM_MONTHLY":
            self.end_date = timezone.now() + datetime.timedelta(days=30)
        elif plan_type == "PREMIUM_YEARLY":
            self.end_date = timezone.now() + datetime.timedelta(days=365)
        self.save()


class SubscriptionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=Subscription.PLAN_CHOICES)
    action = models.CharField(max_length=120, default='CREATED')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.plan}) - {self.action} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
