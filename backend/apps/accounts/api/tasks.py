from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_password_reset_email(user_email, user_id, token):
    """Task to send an email with password reset link."""
    # Create password reset URL (frontend URL)
    reset_url = f"{settings.FRONTEND_URL}/password_reset/{user_id}/{token}/"

    # Render email content
    subject = "Reset your password"
    message = render_to_string(
        "accounts/emails/password_reset_email.html",
        {
            "reset_url": reset_url,
        },
    )

    # Send email
    send_mail(
        subject=subject,
        message=message,
        html_message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

    return f"Password reset email sent to {user_email}"
