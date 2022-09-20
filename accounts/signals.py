from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

# signals - 1. decorators & 2. below another way to connect receiver to the sender 
# post_save.connect(post_save_create_profile_receiver, sender=User)

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user = instance
        )
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # if user profile does not exist and update happened on the user model
            UserProfile.objects.create(
                user = instance
            )

    # print('Signal invoked, user profile created..!')

# @receiver(pre_save, sender=User)
# def pre_save_profile_receiver(sender, instance, **kwargs):
#     print(instance.username, " this user is being saved")