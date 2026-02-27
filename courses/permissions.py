from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInstructorOrReadOnly(BasePermission):
    """
    - Anyone can view (GET, HEAD, OPTIONS)
    - Only instructors can create
    - Only course owner can update/delete
    """

    def has_permission(self, request, view):
        # Allow read-only requests
        if request.method in SAFE_METHODS:
            return True

        # Allow only instructors to create
        return (
            request.user.is_authenticated and
            request.user.role == "INSTRUCTOR"
        )

    def has_object_permission(self, request, view, obj):
        # Allow read-only requests
        if request.method in SAFE_METHODS:
            return True

        # Allow only course owner to update/delete
        return obj.instructor == request.user