from django.db import models

class Waitlist(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} <{self.email}>"

    class Meta:
        verbose_name_plural = "Waitlist"