from django.urls import path
from django.contrib.auth import views as django_views

from .forms import ChangePasswordForm, ResetPasswordForm, ResetPasswordEmailForm


urlpatterns = [
    path("reset_password",
         django_views.PasswordResetView.as_view(template_name="login/recover_password.html",
                                                form_class=ResetPasswordEmailForm),
         name="reset_password"),
    path("reset_password_sent",
         django_views.PasswordResetDoneView.as_view(template_name="login/recover_password_done.html"),
         name="password_reset_done"),
    path("reset_password/confirm/<uidb64>/<token>",
         django_views.PasswordResetConfirmView.as_view(template_name="login/recover_password_confirm.html",
                                                       form_class=ResetPasswordForm),
         name="password_reset_confirm"),
    path("reset_password_complete",
         django_views.PasswordResetCompleteView.as_view(template_name="login/recover_password_complete.html"),
         name="password_reset_complete"),

    path("change_password", django_views.PasswordChangeView.as_view(template_name="login/change_password.html",
                                                                    form_class=ChangePasswordForm),
         name="change_password"),
    path("change_password_done", django_views.PasswordChangeDoneView.as_view(template_name="login/change_password_done.html"),
         name="password_change_done")
]
