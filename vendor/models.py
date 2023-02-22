from enum import unique
from django.db import models
from accounts.models import User, UserProfile

from accounts.utils import send_vendor_notification

from datetime import time, date, datetime

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name = 'user', on_delete = models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name = 'user_profile', on_delete = models.CASCADE)

    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length = 100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license', null = True, blank = True)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateField(auto_now_add = True)
    modified_at = models.DateField(auto_now = True)

    def __str__(self):
        return self.vendor_name

    def is_open(self):
        todays_date = date.today()
        today = todays_date.isoweekday()
        current_opening_hour = OpeningHour.objects.filter(vendor = self, day=today)

        current_time = datetime.now().strftime("%H:%M:%S")

        is_open = False
        for cur_op_hr in current_opening_hour:
            try:
                start_time = str(datetime.strptime(cur_op_hr.from_hour, "%I:%M %p").time())
                end_time = str(datetime.strptime(cur_op_hr.to_hour, "%I:%M %p").time())
                
                if current_time > start_time and current_time < end_time:
                    is_open = True
                    break
            except:
                pass
        
        return is_open

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

                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                send_vendor_notification(mail_subject, mail_template, context)
            
            else:
                if self.is_approved == False:
                    mail_subject = 'foodOnline - Eligibility Criteria Failed'
                else:
                    mail_subject = 'Modification in vendor model'

            
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                send_vendor_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday"))
]

HOUR_OF_DAY = [(time(h,m).strftime('%I:%M %p'), time(h,m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', 'from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
    

