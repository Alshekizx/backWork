from django.core.mail import send_mass_mail
from django.conf import settings
from .models import NewsLetterSubscription, CustomUser

def send_newsletter(subject, message):
    recipients = list(
        NewsLetterSubscription.objects.values_list('email', flat=True)
    )
    user_emails = list(
        CustomUser.objects.filter(subscribe_newsletter=True).values_list('email', flat=True)
    )

    all_emails = set(recipients + user_emails)

    email_messages = [
        (subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        for email in all_emails
    ]

    send_mass_mail(email_messages, fail_silently=True)
