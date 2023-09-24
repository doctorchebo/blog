from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property

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
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
    total_questions = models.IntegerField(default=0)  # Total number of questions in the quiz
    correct_answers = models.IntegerField(default=0)  # Number of correct answers
    user_answers = models.JSONField(default=dict)  # Store user's answers as a dictionary

    @cached_property
    def questions(self):
        return Question.objects.in_bulk(self.user_answers.keys())

    def calculate_correct_answers(self):
        # Calculate the number of correct answers based on the answers stored
        correct_answers = 0
        for question_id, user_answer in self.user_answers.items():
            question = self.questions.get(int(question_id))
            if question and user_answer == question.correct_answer:
                correct_answers += 1
        self.correct_answers = correct_answers