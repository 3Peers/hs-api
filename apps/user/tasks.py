from celery import task
from celery.utils.log import get_task_logger
from django.utils import timezone
from .models import SignUpOTP

logging = get_task_logger(__name__)


@task()
def remove_expired_otps():
    num_deleted, _ = SignUpOTP.objects.filter(
        expires_at__lte=timezone.now()
    ).delete()
    logging.info(f"OTP Objects Deleted: {num_deleted}")
