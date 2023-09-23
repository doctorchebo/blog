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

def submit_answers(request):
    if request.method == 'POST':
        user = request.user  # Assuming you have user authentication
        total_questions = 0
        correct_answers = 0

        for key, value in request.POST.items():
            print(f"Key: {key}, Value: {value}")
            
            if key.startswith('question_'):
                total_questions += 1
                question_id = int(key.split('_')[1])
                answer_id = int(value)
                answer = Answer.objects.get(pk=answer_id)

                # Check if the selected answer is correct
                if answer.is_correct:
                    correct_answers += 1

        # Calculate the user's tier
        tier = calculate_tier(correct_answers)

        # Save the user's result
        UserResult.objects.create(user=user, correct_answers=correct_answers, total_questions=total_questions, tier=tier)

        return redirect('result')


def calculate_tier(correct_answers):
    if correct_answers <= 3:
        return Tier.objects.get(title='Aun en las Sombras')
    elif correct_answers <= 7:
        return Tier.objects.get(title='Con los Ojos Entreabiertos')
    else:
        return Tier.objects.get(title='La Verdad Desvelada')

def result(request):
    user_result = UserResult.objects.filter(user=request.user).last()
    return render(request, 'quiz/result.html', {'user_result': user_result})
