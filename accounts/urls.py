from django.urls import path

app_name = 'accounts'

from .views import(
    signup_view,
    login_view,
    logout_view,
    verify_email,
    profile_view,
    forgot_password_view,
    reset_password_view,
    change_password_view,
    favorites_list,
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('profile/', profile_view, name='profile'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
    path('forgot/', forgot_password_view, name='forgot'),
    path('reset-password/<uidb64>/<token>/', reset_password_view, name='reset_password'),
    path('change-password/', change_password_view, name='change_password'),
    path('favorites/', favorites_list, name='favorites_list'),
]
