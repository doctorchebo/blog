from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_answer_by_pk')
def get_answer_by_pk(answers, answer_id):
    return answers.filter(pk=answer_id).first()