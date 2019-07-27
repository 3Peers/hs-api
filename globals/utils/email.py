from django.conf import settings
from django.core.mail import send_mail as django_send_mail


# TODO: add logging on success/error of the sending email
def send_mail(subject, message, recipients):
    """
    Returns a boolean response to indicate status
    """
    if not (message and recipients):
        return False

    num_emails_sent = django_send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipients
    )

    return bool(num_emails_sent)
