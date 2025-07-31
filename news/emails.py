from django.core.mail import send_mass_mail
from django.conf import settings
from .models import NewsLetterSubscription, CustomUser,  NewsletterHistory

def send_newsletter(subject, message):
    recipients = list(
        NewsLetterSubscription.objects.values_list('email', flat=True)
    )
    user_emails = list(
        CustomUser.objects.filter(subscribe_newsletter=True).values_list('email', flat=True)
    )

    all_emails = list(set(recipients + user_emails))

    email_messages = [
        (subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        for email in all_emails
    ]

    send_mass_mail(email_messages, fail_silently=True)

    # Save to history
    NewsletterHistory.objects.create(
        subject=subject,
        message=message,
        recipients=all_emails
    )
