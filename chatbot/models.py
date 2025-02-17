from django.db import models

class Message(models.Model):
    user_id = models.CharField(max_length=50)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.user_message[:30]}"
