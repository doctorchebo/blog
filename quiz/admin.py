from django.contrib import admin
from .models import Question, Answer, Tier

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class TierAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image')
    search_fields = ('title', 'content')
    list_filter = ('title',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Tier, TierAdmin)
