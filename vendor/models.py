from django.db import models
from accounts.models import User, UserProfile

from accounts.utils import send_vendor_notification

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name = 'user', on_delete = models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name = 'user_profile', on_delete = models.CASCADE)

    vendor_name = models.CharField(max_length=100)
    vendor_license = models.ImageField(upload_to='vendor/license', null = True, blank = True)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateField(auto_now_add = True)
    modified_at = models.DateField(auto_now = True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        # to identify if update is happening or not
        if self.pk is not None:
            original_status = Vendor.objects.get(pk=self.pk)
            if original_status.is_approved != self.is_approved:
                if self.is_approved == True:
                    # send notification email
                    mail_subject = 'Congratulations! Your restaurant is approved.. you can build your menu now..'
                else:
                    # send notification email
                    mail_subject = 'We are sorry! You are not eligible for publishing your food menu on our marketplace.'
            
            else:
                if self.is_approved == False:
                    mail_subject = 'foodOnline - Eligibility Criteria Failed'

            
            mail_template = 'accounts/emails/admin_approval_email.html'
            context = {
                'user': self.user,
                'is_approved': self.is_approved,
            }
            send_vendor_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)
