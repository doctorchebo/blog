from django.shortcuts import render, redirect
from .models import Question, Answer, Tier, UserResult
import random


def questionnaire(request):
    questions = list(Question.objects.all())
    random.shuffle(questions)  # Shuffle the order of questions

    # Limit the number of questions to 10 (or adjust as needed)
    selected_questions = questions[:10]

    for question in selected_questions:
        answers = list(question.answer_set.all())
        random.shuffle(answers)  # Shuffle the order of answers for each question
        question.shuffled_answers = answers

    return render(request, 'quiz/questionnaire.html', {'questions': selected_questions})

def show_answers(request):
    # Retrieve the user's answers
    user = request.user if request.user.is_authenticated else None
    user_result = UserResult.objects.filter(user=user).last()

    # Retrieve the correct answers for the questions
    correct_answers = {}
    for question in Question.objects.all():
        correct_answer = Answer.objects.filter(question=question, is_correct=True).first()
        if correct_answer:
            correct_answers[question.id] = correct_answer.text

    return render(request, 'quiz/show_answers.html', {'user_result': user_result, 'correct_answers': correct_answers})

def submit_answers(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        total_questions = 0
        user_answers = {}
        correct_answers = 0  # Track correct answers

        for key, value in request.POST.items():
            if key.startswith('question_'):
                total_questions += 1
                question_id = int(key.split('_')[1])
                answer_id = int(value)
                user_answers[question_id] = answer_id

                # Calculate correct answers as you iterate through questions
                question = Question.objects.get(pk=question_id)
                try:
                    correct_answer = Answer.objects.get(question=question, is_correct=True)
                    if answer_id == correct_answer.id:
                        correct_answers += 1
                except Answer.DoesNotExist:
                    pass

        # Calculate the user's tier based on correct_answers
        tier = calculate_tier(correct_answers)

        # Find the existing user result or create a new one
        user_result = None
        if user:
            # If the user is authenticated, find their existing result if it exists
            try:
                user_result = UserResult.objects.get(user=user)
            except UserResult.DoesNotExist:
                pass

        # If a user result is found, update it; otherwise, create a new one
        if user_result:
            user_result.tier = tier
            user_result.total_questions = total_questions
            user_result.user_answers = user_answers
            user_result.correct_answers = correct_answers  # Update correct answers count
            user_result.save()
        else:
            user_result = UserResult.objects.create(
                user=user,
                tier=tier,
                total_questions=total_questions,
                user_answers=user_answers,
                correct_answers=correct_answers,  # Set correct answers count
            )

        return redirect('quiz:result')

def calculate_tier(correct_answers):
    if correct_answers <= 3:
        return Tier.objects.get(title='Aun en las Sombras')
    elif correct_answers <= 7:
        return Tier.objects.get(title='Con los Ojos Entreabiertos')
    else:
        return Tier.objects.get(title='La Verdad Desvelada')


def result(request):
    user = request.user if request.user.is_authenticated else None
    user_result = UserResult.objects.filter(user=user).last()
    return render(request, 'quiz/result.html', {'user_result': user_result})
