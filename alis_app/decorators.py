from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*allowed_roles):
    def check_role(user):
        if user.is_authenticated and user.role in allowed_roles:
            return True
        raise PermissionDenied
    return user_passes_test(check_role, login_url='login')

def student_required(function=None):
    actual_decorator = role_required('student', 'owner')
    if function:
        return actual_decorator(function)
    return actual_decorator

def teacher_required(function=None):
    actual_decorator = role_required('teacher', 'owner')
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None):
    actual_decorator = role_required('admin', 'owner')
    if function:
        return actual_decorator(function)
    return actual_decorator

def owner_required(function=None):
    actual_decorator = role_required('owner')
    if function:
        return actual_decorator(function)
    return actual_decorator