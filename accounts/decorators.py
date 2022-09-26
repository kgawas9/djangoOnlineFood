from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing customer page
def is_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the customer from accessing vendor page 
def is_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def is_admin_user(user):
    if user.is_admin:
        return True
    else:
        raise PermissionDenied
