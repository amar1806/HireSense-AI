from subscription.models import Subscription

# ================= CHECK PREMIUM =================

def is_premium(user):
    
    # If user not logged in
    if not user.is_authenticated:
        return False

    # Check subscription
    try:
        subscription = Subscription.objects.get(user=user)
        return subscription.is_premium_active()
    except Subscription.DoesNotExist:
        return False