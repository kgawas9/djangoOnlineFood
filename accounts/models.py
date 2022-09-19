from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    '''
        User manager will never contain any fields
        it will only contain the methods e.g., create_user or create_superuser
    '''
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User must have email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        # it encodes the password and store it in database. we cannot store the password in plain text
        user.set_password(password)     

        # django by default use using parameter to define which database the manager should use for the operations 
        # in case if we have multiple database we need to define where the data should be saved
        # with the help of using we can pass the appropriate database
        # self._db will take the default database
        user.save(using=self._db)       
        return user


    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
                email = self.normalize_email(email),
                username = username,
                password = password,
                first_name = first_name, 
                last_name = last_name
            )

        # To provide user a superuser authorization
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superadmin = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    RESTAURANT = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (RESTAURANT, 'Restaurant'),
        (CUSTOMER, 'Customer'),
    )    
    #    It consist of all the fields like first_name, last_name etc
    #    full control of editing the whole custom user model including the authentication functionality of django
    #    AbstractUser - it does not give the full control of django user model. we only can add the extra field so we use AbstractBaseUser
    
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 50, unique = True)
    email = models.EmailField(max_length = 100, unique = True)
    phone_number = models.CharField(max_length = 12, blank = True)
    
    # restuarant, customer and admin role
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank = True, null = True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add = True)
    last_login = models.DateTimeField(auto_now_add = True)
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)

    # set autorization and permissions
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)

    # to change the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    # below methods will return True only if the user is active super user or admin 
    # for in-active by default it will return false

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_lable):
        return True


class UserProfile(models.Model):
    # models.CASCADE - to decide what action needs to be taken if users are deleted
    # models.CASCADE - if user deleted from system the profile also will be deleted
    user = models.OneToOneField(User, on_delete = models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photoes', blank=True, null=True)

    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


