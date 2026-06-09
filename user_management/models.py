from django.db import models
from django.contrib.auth.models import User


class Page(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url_path = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserPageAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_assignments')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='user_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    assigned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')

    def __str__(self):
        return f"{self.user.username} -> {self.page.name}"
