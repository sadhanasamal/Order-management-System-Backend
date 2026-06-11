from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    Abstract base model providing a full audit trail.

    All models that need created_by / updated_by tracking should inherit from this.
    For models that also need SCD Type 2 (versioning + soft delete), use SCDModel instead.

    Requires CurrentUserMiddleware to be active so that save() can resolve the
    authenticated user from thread-local storage without explicit passing.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_updated',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from common.middleware.current_user_middleware import get_current_request

        request = get_current_request()
        user = request.user if request and hasattr(request, 'user') else None

        if not user or not user.is_authenticated:
            user_info = "None" if not user else f"{user} (authenticated={getattr(user, 'is_authenticated', False)})"
            raise ValueError(
                f"Cannot save {self.__class__.__name__} without an authenticated user. "
                f"Found user: {user_info}. "
                f"Possible causes: (1) No Authorization header in request, "
                f"(2) Invalid/expired token, (3) CurrentUserMiddleware not in MIDDLEWARE. "
                f"For management commands, set created_by/updated_by explicitly and call super().save()."
            )

        if self._state.adding and not self.created_by_id:
            self.created_by = user

        self.updated_by = user

        super().save(*args, **kwargs)