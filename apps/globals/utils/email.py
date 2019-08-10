from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from celery import shared_task
from celery.utils.log import get_task_logger

logging = get_task_logger(__name__)


@shared_task
def send_mail(subject, message, recipients):
    """
    Returns a boolean response to indicate status
    """
    if not (message and recipients):
        logging.error("Unsent: Empty message and/or recipients.")
        return False

    num_emails_sent = django_send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipients
    )
    logging.info(f"Sent: {num_emails_sent} emails.")
    return bool(num_emails_sent)
