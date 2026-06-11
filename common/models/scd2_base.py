from django.db import models
from django.conf import settings
from django.db.models import Max
from django.utils import timezone

from common.models.base import BaseModel


class SCDManager(models.Manager):
    """
    Default manager for SCD Type 2 models.

    .active()           → queryset of non-deleted, active (current version) records
    .get_active(hub_id) → fetch the single current version for a logical entity
    """

    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def get_active(self, hub_id):
        return self.get(hub_id=hub_id, is_active=True, is_deleted=False)


class SCDModel(BaseModel):
    """
    Abstract SCD Type 2 model.

    Extends BaseModel with:
    - hub_id: stable integer identity across versions (auto-assigned as max+1 on first insert)
    - is_active / is_deleted: version and soft-delete state
    - deleted_at / deleted_by: auto-populated on soft delete transition
    - SCDManager: .active() and .get_active(hub_id) shortcuts

    The SCD2 pattern (deactivate old row, insert new row) is handled by the utility
    functions in utils/scd2.py. This model provides the fields and state-transition
    automation in save(); callers never need to set deleted_at, deleted_by, or is_active
    manually when soft-deleting.

    Usage:
        class Hospital(SCDModel):
            name = models.CharField(max_length=255)
            ...
    """

    hub_id = models.PositiveIntegerField(db_index=True, editable=False, db_column='hub_id')

    is_active = models.BooleanField(default=True, db_index=True, db_column='actv_ind')
    is_deleted = models.BooleanField(default=False, db_index=True, db_column='del_ind')

    deleted_at = models.DateTimeField(null=True, blank=True, db_column='del_dt')
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_deleted',
        db_column='del_by_id',
    )

    objects = SCDManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Auto-assign hub_id on first creation; preserve it on new SCD2 versions
        if self._state.adding and not self.hub_id:
            max_val = self.__class__.objects.aggregate(Max('hub_id'))['hub_id__max'] or 0
            self.hub_id = max_val + 1

        # Auto-populate deleted_at, deleted_by, and is_active=False
        # when is_deleted transitions False → True
        if self.is_deleted:
            is_transition = True
            if not self._state.adding:
                try:
                    original = self.__class__.objects.get(pk=self.pk)
                    is_transition = not original.is_deleted
                except self.__class__.DoesNotExist:
                    is_transition = True

            if is_transition:
                if not self.deleted_at:
                    self.deleted_at = timezone.now()

                if not self.deleted_by_id:
                    from common.middleware.current_user_middleware import get_current_request
                    request = get_current_request()
                    user = request.user if request and hasattr(request, 'user') else None
                    if user and user.is_authenticated:
                        self.deleted_by = user

                # A deleted record must not remain active
                self.is_active = False

        # Delegate audit trail (created_by, updated_by) to BaseModel.save()
        super().save(*args, **kwargs)

    def deactivate(self):
        """Mark this version as inactive (SCD2 close-out step). Does not soft-delete."""
        self.is_active = False
        self.save()
