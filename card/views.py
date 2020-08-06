import csv
import io
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView, FormView,
    CreateView, ListView, DetailView, UpdateView, DeleteView
)

from .forms import CSVUploadFileForm  # SimpleExerciseForm
from .models import Card, user_directory_path

from .google_text2speech import get_speech_audio
from celery import task


@task
def set_answer_audio_file(target_qid):
    """
    Task to get and store the audio file of the answer text
    from Google text to speech API
    """
    # Todo: shorten the path expression
    target_card = Card.objects.get(card_id=target_qid)
    audio_file_path = os.path.join(settings.MEDIA_ROOT,
                                   user_directory_path(target_card,
                                                       target_card.title)
                                  )
    get_speech_audio(audio_file_path, target_card.answer_text)
    target_card.answer_audio = audio_file_path + ".mp3"
    target_card.save()
    return print(F"successfully saved audio file to \
    {target_card.answer_audio.url}")


# Todo: separate importing view into another app for import/export functionaity
class CardImport(FormView):
    template_name = 'card_upload.html'
    success_url = reverse_lazy('card_upload_successed')
    form_class = CSVUploadFileForm

    def form_valid(self, form):
        csvfile = io.TextIOWrapper(form.cleaned_data['file'], encoding='utf-8')
        reader = csv.reader(csvfile)

        for row in reader:
            #print(row)
            #card, created = Card.objects.get_or_create(card_id=row[0])
            card, created = Card.objects.get_or_create(
                card_creator=self.request.user,
                question_text=row[1],
                answer_text=row[2],
                defaults={'card_creator': self.request.user},
            )
            card.title = row[0]
            card.question_text = row[1]
            card.answer_text = row[2]
            card.category = row[3]
            card.subcategory = row[4]
            card.detail = row[5]
            if row[6] != "":
                card.literary_style = True
            card.creation_date = timezone.now()
            card.save()

            set_answer_audio_file.delay(card.card_id)

        return super().form_valid(form)


class UploadSuccessedView(TemplateView):
    template_name = 'card_upload_successed.html'


#
# Todo: separate cards views into another app
#
class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    template_name = 'card_new.html'
    fields = ('title', 'category', 'subcategory', 'detail',
              'question_text', 'answer_text', 'literary_style')
    login_url = 'login'

    def form_valid(self, form):
        form.instance.card_creator = self.request.user
        return super().form_valid(form)


class CardListView(ListView):
    template_name = 'card_list.html'
    context_object_name = 'cards'
    paginate_by = 20

    def get_queryset(self):
        # Todo: read docmentation to add the default quesions created by admin
        # self.creator = get_object_or_404(Card, name=self.kwargs['creator'])
        if self.request.user.is_authenticated:
            return Card.objects.filter(
                card_creator__in=[self.request.user]).order_by('-title')
            # +admin here?
        else:
            return Card.objects.filter(
                card_creator__username='guest_user').order_by('-title')


class SearchResultListView(ListView):
    template_name = 'search_results.html'
    context_object_name = 'search_results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        if self.request.user.is_authenticated:
            user_cards = Card.objects.filter(
                card_creator=self.request.user)
        else:
            user_cards = Card.objects.filter(
                card_creator__username='guest_user')

        return user_cards.filter(
            Q(title__icontains=query) |
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query) |
            Q(category__icontains=query) |
            Q(subcategory__icontains=query) |
            Q(detail__icontains=query)
        )

    def get_context_data(self):
        context = super().get_context_data()
        context['query'] = self.request.GET.get('q')
        return context


class CardDetailView(DetailView):
    model = Card
    template_name = 'card_detail.html'
    context_object_name = 'card'


class CardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Card
    fields = ['category', 'subcategory', 'detail',
              'question_text', 'answer_text', 'literary_style'
             ]
    template_name = 'card_edit.html'
    context_object_name = 'card'
    login_url = 'login'

    # for the case user try to delete the default card created by admin
    def test_func(self):
        obj = self.get_object()
        return obj.card_creator == self.request.user


class CardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Card
    template_name = 'card_delete.html'
    success_url = reverse_lazy('card_list')
    context_object_name = 'card'
    login_url = 'login'

    def test_func(self):
        obj = self.get_object()
        return obj.card_creator == self.request.user
