from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login

class UserPassesTestMixinNoPermissionDeny(UserPassesTestMixin):
	# Redefined handle_no_permission to avoid the 403 No permission when an already connected user tries to reach a private url of another user.
    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path())