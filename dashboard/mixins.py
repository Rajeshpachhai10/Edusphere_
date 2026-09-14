from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Restricts a view to users with role == 'admin'.

    We raise PermissionDenied (403) rather than redirecting to login,
    because unlike an anonymous visitor hitting a login-required page,
    someone who IS logged in but isn't an admin shouldn't be told
    "log in to see this" — they're already logged in. A 403 is the
    honest response: you're authenticated, you're just not authorized.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to access the admin dashboard.")