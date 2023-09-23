from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    text = models.TextField()
    
    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Tier(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='tiers/')
    
    def __str__(self):
        return self.title

class UserResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    correct_answers = models.IntegerField()
    total_questions = models.IntegerField()
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
