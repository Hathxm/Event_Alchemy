# yourapp/tasks.py

from celery import shared_task
from backend.celery import app
from django.core.mail import send_mail
from django.conf import settings
from user.models import Booking
from datetime import datetime
from vendors.models import Vendors

@shared_task(bind=True)
def notify_vendors(self):
    today = datetime.now().date()
    bookings = Booking.objects.filter(date=today)
    print(bookings)
    vendors_notified = set()

    for booking in bookings:
        for service in booking.services.all():
            vendor = service.vendor
            if vendor.email not in vendors_notified:
                subject = "Daily Booking Notification"
                message = (f"Dear {vendor.username},\n\n"
                           f"You have new bookings for today:\n\n"
                           f"Booking Details:\n"
                           f"Event: {booking.event.name}\n"
                           f"Date: {booking.date}\n\n"
                           f"Please ensure you are prepared for the services you have been booked for.\n\n"
                           f"Best regards,\n"
                           f"Event Management Team")
                send_mail(subject, message, settings.EMAIL_HOST_USER, [vendor.email])
                vendors_notified.add(vendor.email)
    return "Notifications sent to vendors."

# @shared_task(bind=True)
# def notify_vendors(self):
#     subject="hey"
#     message ="yoo"
#     vendoremail="mohammedhathimeasa@gmail.com"
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [vendoremail])
#     return "Notification sent"