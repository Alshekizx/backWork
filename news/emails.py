from django.core.mail import send_mass_mail
from django.conf import settings
from .models import NewsLetterSubscription, CustomUser, NewsletterHistory
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def send_newsletter(subject, message):
    recipients = list(
        NewsLetterSubscription.objects.values_list('email', flat=True)
    )
    user_emails = list(
        CustomUser.objects.filter(subscribe_newsletter=True).values_list('email', flat=True)
    )

    all_emails = list(set(recipients + user_emails))

    if not all_emails:
        logger.warning("No recipients for newsletter")
        return

    email_messages = [
        (subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        for email in all_emails
    ]

    try:
        with transaction.atomic():
            send_mass_mail(email_messages, fail_silently=False)

            NewsletterHistory.objects.create(
                subject=subject,
                message=message,
                recipients=all_emails  # ✅ make sure this field supports list/JSON
            )
    except Exception as e:
        logger.error(f"Failed to send newsletter: {e}")
        raise
