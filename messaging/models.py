from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content  = models.TextField()
    sent_at  = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']
        db_table = 'core_message'

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"


class Block(models.Model):
    blocker    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')
        db_table = 'core_block'

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"
