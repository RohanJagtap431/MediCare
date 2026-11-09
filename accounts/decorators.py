
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        is_admin = (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "ADMIN"
        )

        if not is_admin:
            raise PermissionDenied(
                "You do not have permission to perform this action."
            )

        return view_func(request, *args, **kwargs)

    return wrapper
