from django.db import models
from django.utils.timezone import now

class Content(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    count = models.IntegerField(default=0)
    score_average = models.FloatField(default=0)

    def calculate_score_avg(self, value):
        return (self.score_average * self.count + value) / (self.count + 1)

    def fix_score_avg(self, value, pre_avg):
        if self.count != 0:
            return (((self.score_average * self.count) - pre_avg) + value) / self.count
        return value

class User(models.Model):
    user_name = models.CharField(max_length=255)

class Score(models.Model):
    score_value = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(default=now)