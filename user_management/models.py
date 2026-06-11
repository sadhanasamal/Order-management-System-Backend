from django.db import models
from django.contrib.auth.models import User

from common.models import BaseModel


class Page(BaseModel):
    name = models.CharField(max_length=100, unique=True, db_column='page_nm')
    url_path = models.CharField(max_length=255, unique=True, db_column='url_path')
    is_active = models.BooleanField(default=True, db_column='actv_ind')

    def __str__(self):
        return self.name


class UserPageAssignment(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='page_assignments',
        db_column='user_id',
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        db_column='page_id',
    )

    class Meta:
        unique_together = ('user', 'page')

    def __str__(self):
        return f"{self.user.username} -> {self.page.name}"