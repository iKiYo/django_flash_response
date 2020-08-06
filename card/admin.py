from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_creator', 'title', 'category', 'subcategory',
                    'question_text', 'answer_text', 'creation_date'
    )
