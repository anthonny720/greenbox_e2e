from djoser import email


class PasswordReset(email.ActivationEmail):
    template_name = 'email/password_reset_email.html'
