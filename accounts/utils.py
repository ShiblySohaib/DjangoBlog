from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import render


def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.id))

    current_site = get_current_site(request)
    verification_link = f"http://{current_site.domain}/accounts/verify-email/{uid}/{token}"

    email_subject = "Verify Your Email Address - DjangoBlog"
    email_body = render_to_string(
        "accounts/emailVerificationEmail.html",
        {"user": user, "verification_link": verification_link},
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()


# def test_verification_email(request, user):
#     from django.contrib.auth.tokens import default_token_generator
#     from django.utils.encoding import force_bytes
#     from django.utils.http import urlsafe_base64_encode
#     from django.contrib.sites.shortcuts import get_current_site

#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.id))
#     current_site = get_current_site(request)
#     verification_link = f"/accounts/verify-email/{uid}/{token}"
#     return verification_link



def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.id))

    current_site = get_current_site(request)
    password_reset_link = f"http://{current_site.domain}/accounts/reset-password/{uid}/{token}"

    email_subject = "Reset Your Password - DjangoBlog"
    email_body = render_to_string(
        "accounts/passwordResetEmail.html",
        {"user": user, "password_reset_link": password_reset_link},
    )

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()


# def test_password_reset_email(request, user):
#     from django.contrib.auth.tokens import default_token_generator
#     from django.utils.encoding import force_bytes
#     from django.utils.http import urlsafe_base64_encode
#     from django.contrib.sites.shortcuts import get_current_site

#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.id))
#     current_site = get_current_site(request)
#     password_reset_link = f"/accounts/reset-password/{uid}/{token}"
#     return password_reset_link