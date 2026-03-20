import os
import pickle
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.utils.text import get_valid_filename
from sklearn.metrics.pairwise import cosine_similarity

from .resume_parser import extract_resume_text
from .skills import extract_skills
from .ats_score_v2 import calculate_ats_score
from .skill_gap import skill_gap_analysis
from .recommend import recommend_skills
from .ai_analysis import analyze_resume_negatives
from .resume_generator import generate_resume_improvements, generate_resume_pdf
from .utils import is_premium


# Load ML model
ML_MODEL_DIR = Path(__file__).resolve().parent.parent / 'ml_model'
model = pickle.load(open(ML_MODEL_DIR / 'model.pkl', 'rb'))
vectorizer = pickle.load(open(ML_MODEL_DIR / 'vectorizer.pkl', 'rb'))


# =========================
# HOME PAGE
# =========================
def home(request):
    return render(request, "home.html")


# =========================
# UPLOAD & ANALYSIS
# =========================
def upload_resume(request):

    if not request.user.is_authenticated:
        return redirect("/login")

    if request.method == "POST":

        resumes = request.FILES.getlist('resume')
        job_desc = request.POST.get("job_desc", "")
        role = request.POST.get("role", "software_engineer")

        results = []
        upload_errors = []

        for resume in resumes:

            # Validate file type & size
            file_ext = os.path.splitext(resume.name)[1].lower()
            if file_ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
                upload_errors.append(
                    f"Skipped {resume.name}: unsupported file type ({file_ext}). Allowed: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
                )
                continue

            if resume.size > settings.MAX_UPLOAD_SIZE:
                upload_errors.append(
                    f"Skipped {resume.name}: exceeds max upload size of {settings.MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
                )
                continue

            # Save file safely to MEDIA_ROOT and avoid path traversal issues
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            safe_name = get_valid_filename(resume.name)
            stored_name = f"{uuid.uuid4().hex}_{safe_name}"

            saved_name = default_storage.save(stored_name, resume)
            try:
                file_path = default_storage.path(saved_name)
            except Exception:
                # Some storage backends may not support .path()
                file_path = os.path.join(settings.MEDIA_ROOT, saved_name)

            # Extract text
            resume_text = extract_resume_text(file_path)

            # Clean up the uploaded file after parsing
            try:
                default_storage.delete(saved_name)
            except Exception:
                pass

            if not resume_text:
                resume_text = ""

            # Skill extraction
            skills = extract_skills(resume_text)

            # Vector similarity
            resume_vector = vectorizer.transform([resume_text])
            job_vector = vectorizer.transform([job_desc])

            similarity = cosine_similarity(resume_vector, job_vector)[0][0]

            # Match Score (out of 100)
            match_score = min(round(similarity * 100, 2), 100)

            # ATS Score
            ats_score = calculate_ats_score(resume_text, job_desc, skills)

            # Skill Gap
            gaps = skill_gap_analysis(job_desc, skills)

            # Recommendations
            recommended = recommend_skills(gaps)

            # Resume Weakness
            negatives = analyze_resume_negatives(resume_text, job_desc)

            # Improvements
            improvements = generate_resume_improvements(gaps)

            # =========================
            # PREMIUM FEATURE
            # =========================
            if is_premium(request.user):

                pdf_path = os.path.join(
                    "media",
                    f"generated_{resume.name}.pdf"
                )

                # Allow template selection for premium users
                template = request.POST.get("template", "modern")  # Default to modern

                generate_resume_pdf(
                    {
                        "name": "Candidate Name",
                        "email": "email@example.com",
                        "skills": ", ".join(skills),
                        "experience": "Experience tailored to job role",
                        "role": role
                    },
                    pdf_path,
                    template=template
                )

            else:
                pdf_path = None

            # Store result
            results.append({

                "name": resume.name,
                "score": match_score,
                "ats": ats_score,
                "skills": skills,
                "gaps": gaps,
                "recommended": recommended,
                "negatives": negatives,
                "improvements": improvements,
                "pdf": pdf_path

            })

        # Sort by best match
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Get subscription info
        is_premium_user = False
        premium_ends = None
        plan_name = None
        days_remaining = 0
        auto_renew = False

        try:
            subscription = Subscription.objects.get(user=request.user)
            is_premium_user = subscription.is_premium_active()
            premium_ends = subscription.end_date
            plan_name = subscription.plan
            days_remaining = subscription.get_days_remaining()
            auto_renew = subscription.auto_renew
        except Subscription.DoesNotExist:
            pass

        return render(request, "dashboard.html", {
            "results": results,
            "is_premium": is_premium_user,
            "premium_ends": premium_ends,
            "plan_name": plan_name,
            "days_remaining": days_remaining,
            "auto_renew": auto_renew,
            "upload_errors": upload_errors,
        })

    return render(request, "upload.html")


# ================= 
# DASHBOARD VIEW 
# =================

from django.shortcuts import render
from subscription.models import Subscription


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/")

    # Subscription info
    is_premium = False
    premium_ends = None
    plan_name = None
    days_remaining = 0
    auto_renew = False

    try:
        subscription = Subscription.objects.get(user=request.user)
        is_premium = subscription.is_premium_active()
        premium_ends = subscription.end_date
        plan_name = subscription.plan
        days_remaining = subscription.get_days_remaining()
        auto_renew = subscription.auto_renew
    except Subscription.DoesNotExist:
        pass

    # Return empty results - actual results come from upload_resume
    results = []

    return render(request, "dashboard.html", {
        "results": results,
        "is_premium": is_premium,
        "premium_ends": premium_ends,
        "plan_name": plan_name,
        "days_remaining": days_remaining,
        "auto_renew": auto_renew,
        "upload_errors": [],
    })

# ================= 
# GENERATE RESUME 
# =================

from django.shortcuts import render, redirect
from django.http import HttpResponse
import os

def generate_resume(request):

    # If user not logged in → go home
    # ✅ LOGIN REQUIRED
    if not request.user.is_authenticated:
        return redirect("/")   # go to home

    # ✅ PREMIUM REQUIRED
    if not is_premium(request.user):
        return redirect("/pricing")

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        skills = request.POST.get("skills")
        experience = request.POST.get("experience")
        role = request.POST.get("role", "software_engineer")
        template = request.POST.get("template", "modern")

        # Convert skills string → list
        skills_list = skills.split(",") if skills else []

        # Generate PDF
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        safe_user = get_valid_filename(str(request.user.username))
        stored_name = f"resume_{safe_user}_{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, stored_name)

        generate_resume_pdf(
            {
                "name": name,
                "email": email,
                "skills": skills,
                "experience": experience,
                "role": role
            },
            pdf_path,
            template=template
        )

        # Return download response
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{name}_resume.pdf"'

        # Cleanup generated file after download
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception:
            pass

        return response

    return render(request, "generate_resume.html")


# =========================
# PRICING
# =========================

def pricing(request):
    return render(request, "pricing.html")

# =========================
# UPGRADE TO PREMIUM
# =========================

def upgrade_to_premium(request):
    if not request.user.is_authenticated:
        return redirect("/")

    from subscription.models import Subscription

    # Create or update subscription with monthly plan for demo
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={'plan': 'FREE'}
    )
    if not subscription.is_active:
        subscription.activate_premium("PREMIUM_MONTHLY")

    return redirect("/dashboard")

# =========================
# DOWNLOAD RESUME
# =========================
def download_resume(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not is_premium(request.user):
        return redirect("/pricing")

# =========================
# RAZORPAY PAYMENT VIEWS
# =========================

import razorpay
from django.conf import settings
from django.http import JsonResponse
from subscription.models import Subscription

def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    return razorpay.Client(auth=(key_id, key_secret))


def create_razorpay_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Ensure Razorpay configuration is set
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({"error": "Razorpay API keys are not configured."}, status=500)
    if "your_key" in settings.RAZORPAY_KEY_ID.lower() or "your_secret" in settings.RAZORPAY_KEY_SECRET.lower():
        return JsonResponse({"error": "Razorpay API keys are placeholders. Please set real keys in settings."}, status=500)

    plan_type = request.POST.get("plan_type")
    if plan_type not in ["PREMIUM_MONTHLY", "PREMIUM_YEARLY"]:
        return JsonResponse({"error": "Invalid plan type"}, status=400)

    # Plan pricing
    plan_prices = {
        "PREMIUM_MONTHLY": 99,  # ₹99 per month
        "PREMIUM_YEARLY": 999,  # ₹999 per year
    }

    amount = plan_prices[plan_type] * 100  # Amount in paisa

    # Create Razorpay order
    order_data = {
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"  # Auto capture
    }

    try:
        order = get_razorpay_client().order.create(data=order_data)

        # Save order details in subscription
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': 'FREE'}
        )
        subscription.razorpay_order_id = order['id']
        subscription.amount = amount / 100  # Store in rupees
        subscription.save()

        return JsonResponse({
            "order_id": order['id'],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def verify_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")
    plan_type = request.POST.get("plan_type")

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        return JsonResponse({"error": "Missing payment verification parameters."}, status=400)

    try:
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        get_razorpay_client().utility.verify_payment_signature(params_dict)

        # Update subscription
        subscription = Subscription.objects.get(
            user=request.user,
            razorpay_order_id=razorpay_order_id
        )

        subscription.razorpay_payment_id = razorpay_payment_id
        subscription.activate_premium(plan_type)

        # Record history
        from subscription.models import SubscriptionHistory
        SubscriptionHistory.objects.create(
            user=subscription.user,
            plan=subscription.plan,
            action="PAYMENT_VERIFIED",
            amount=subscription.amount
        )

        return JsonResponse({"status": "success", "message": "Payment verified and subscription activated"})

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"error": "Payment verification failed"}, status=400)
    except Subscription.DoesNotExist:
        return JsonResponse({"error": "Subscription not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def razorpay_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Verify webhook signature
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    webhook_body = request.body.decode('utf-8')

    try:
        get_razorpay_client().utility.verify_webhook_signature(
            webhook_body,
            webhook_signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )

        # Process webhook data
        import json
        webhook_data = json.loads(webhook_body)

        if webhook_data['event'] == 'payment.captured':
            payment_entity = webhook_data['payload']['payment']['entity']
            order_id = payment_entity['order_id']

            # Find and update subscription
            try:
                subscription = Subscription.objects.get(razorpay_order_id=order_id)
                if not subscription.is_active:
                    # Determine plan type from amount
                    amount = payment_entity['amount'] / 100
                    if amount == 99:
                        plan_type = "PREMIUM_MONTHLY"
                    elif amount == 999:
                        plan_type = "PREMIUM_YEARLY"
                    else:
                        plan_type = "PREMIUM_MONTHLY"  # fallback

                    subscription.razorpay_payment_id = payment_entity['id']
                    subscription.activate_premium(plan_type)

                    from subscription.models import SubscriptionHistory
                    SubscriptionHistory.objects.create(
                        user=subscription.user,
                        plan=subscription.plan,
                        action='WEBHOOK_PAYMENT_CAPTURED',
                        amount=subscription.amount
                    )

            except Subscription.DoesNotExist:
                pass  # Order not found, ignore

        return JsonResponse({"status": "ok"})

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"error": "Webhook verification failed"}, status=400)

# =========================
# PRICING PAGE
# =========================

def pricing(request):
    from django.conf import settings

    key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")

    razorpay_configured = bool(key_id and key_secret and "your_key" not in key_id.lower() and "your_secret" not in key_secret.lower())

    return render(request, "pricing.html", {
        "razorpay_configured": razorpay_configured,
        "razorpay_key_id": key_id,
    })


# =========================
# SUBSCRIPTION HISTORY
# =========================

def subscription_history(request):
    """Display all subscription payments and changes"""
    if not request.user.is_authenticated:
        return redirect("/")

    from subscription.models import SubscriptionHistory

    history = SubscriptionHistory.objects.filter(user=request.user)

    return render(request, "subscription_history.html", {
        "history": history
    })


# =========================
# TOGGLE AUTO-RENEW
# =========================

def toggle_auto_renew(request):
    """Toggle auto-renew setting"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        subscription = Subscription.objects.get(user=request.user)
        subscription.auto_renew = not subscription.auto_renew
        subscription.save()

        return JsonResponse({
            "status": "success",
            "auto_renew": subscription.auto_renew,
            "message": f"Auto-renew {'enabled' if subscription.auto_renew else 'disabled'}"
        })
    except Subscription.DoesNotExist:
        return JsonResponse({"error": "Subscription not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
