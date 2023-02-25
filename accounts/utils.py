from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

def detectUser(user):
    if user.role == 1:
        redirect_url = 'vendor_dashboard'

    elif user.role == 2:
        redirect_url = 'customer_dashboard'
    
    elif user.role == None and user.is_superadmin:
        redirect_url = '/admin'
        
    return redirect_url


# def asend_verification_email(request, user):
#     # we need use the current site due to local host and post deployment site

#     # About autoescape off
#     # autoescape from email template trust the values from where its coming 
#     # and you are safe agains the cross site scripting 

#     current_site = get_current_site(request)
#     from_email = settings.DEFAULT_FROM_EMAIL
#     email_subject = 'foodOnline - Confirm E-mail Address'
#     message = render_to_string('accounts/emails/account_verification_email.html', {
#         'user': user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })

#     to_email = user.email
#     mail = EmailMessage(email_subject, message, from_email, to=(to_email,))
#     mail.send()


def send_verification_email(request, user, email_subject, email_template):
    # we need use the current site due to local host and post deployment site

    # About autoescape off
    # autoescape from email template trust the values from where its coming 
    # and you are safe agains the cross site scripting 
    
    current_site = get_current_site(request)
    from_email = settings.DEFAULT_FROM_EMAIL
    email_subject = f'foodOnline - { email_subject }'
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    to_email = user.email
    mail = EmailMessage(email_subject, message, from_email, to=(to_email,))
    mail.send()


def send_vendor_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)

    to_email = context['user'].email
    mail = EmailMessage(mail_subject, message, from_email, to=(to_email,))
    mail.send()


# this is similary like above function just renamed the function name to have meaningful name
def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)

    to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=(to_email,))
    mail.send()
