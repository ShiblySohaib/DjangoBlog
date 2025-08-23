from django.shortcuts import render
from .forms import CustomUserCreationForm
from .utils import send_verification_email, send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.db.models import Q


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            messages.success(request, "Account created successfully! Please check your email to verify your account.")
            return redirect("accounts:login")
            #test verification
            # verification_link = test_verification_email(request, user)
            # return render(request, "accounts/emailVerificationEmail.html", {"verification_link": verification_link}) 
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('accounts:signup')


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not user.is_verified and not user.is_superuser:
                messages.error(request, "Account not verified. Please check your email and verify your account before logging in.")
                return render(request, "accounts/login.html")
            login(request, user)
            return redirect("posts:home")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")



def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)
            messages.success(request, "Password reset email has been sent.")
            #test password reset
            # password_reset_link = test_password_reset_email(request, user)
            # return render(request, "accounts/passwordResetEmail.html", {"password_reset_link": password_reset_link})
            return redirect("accounts:login")
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, "accounts/forgot.html")



def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "accounts/resetPassword.html")
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect("accounts:login")
        return render(request, "accounts/resetPassword.html")
    else:
        messages.error(request, "Password reset link is invalid or has expired.")
        return redirect("accounts:login")
    

@login_required
def profile_view(request, user_id=None):
    User = get_user_model()
    if user_id:
        try:
            profile_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('accounts:profile')
        editable = (profile_user == request.user)
    else:
        profile_user = request.user
        editable = True
    if editable and request.method == "POST":
        if request.POST.get("email") != profile_user.email:
            if User.objects.filter(email=request.POST.get("email")).exists():
                messages.error(request, "Email already exists.")
                return render(request, "accounts/profile.html", {"user": profile_user, "editable": editable})
            else:
                profile_user.email = request.POST.get("email")
                profile_user.is_verified = False
                send_verification_email(request, profile_user)
                messages.success(request, "Email updated successfully! Please check your email to verify your new email address.")
        profile_user.first_name = request.POST.get("first_name", profile_user.first_name)
        profile_user.last_name = request.POST.get("last_name", profile_user.last_name)
        profile_user.bio = request.POST.get("bio", profile_user.bio)
        if request.FILES.get("profile_picture"):
            if profile_user.profile_picture and hasattr(profile_user.profile_picture, 'path') and 'default-profile.jpg' not in profile_user.profile_picture.name:
                import os
                try:
                    if os.path.isfile(profile_user.profile_picture.path):
                        os.remove(profile_user.profile_picture.path)
                except Exception:
                    pass
            profile_user.profile_picture = request.FILES.get("profile_picture")
        profile_user.save()
    return render(request, "accounts/profile.html", {"user": profile_user, "editable": editable})


@login_required
def change_password_view(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, "accounts/changePassword.html")

        user = authenticate(request, email=request.user.email, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("accounts:login")
        else:
            messages.error(request, "Current password is incorrect.")
    return render(request, "accounts/changePassword.html")


@login_required
def favorites_list(request):
    query = request.GET.get('q', '')
    posts = request.user.favorite_posts.all().order_by('-created_at')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(category__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        )
    return render(request, 'posts/favorites_list.html', {'posts': posts})
