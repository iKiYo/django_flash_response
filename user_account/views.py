import numpy as np
import datetime
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Avg, Sum

# from qr_grammar.models import get_predicted_level, Question
from card.models import get_predicted_level, Card
from user_account.models import CustomUser
from .forms import CustomUserCreationForm


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        # create the user model of a requested user
        self.object = form.save()

        # copy the default cards
        all_default_cards = Card.objects.filter(card_creator__username='default_user')
        for card in all_default_cards:
            card.pk = None
            card.user = CustomUser.objects.get(card_creator=self.object.username)
            card.save()

        return super().form_valid(form)


# TODO: check the role of reidrect_field_name, how context 'section' works
class DashboardView(generic.View):
    redirect_field_name = 'redirect_to'
    template_name = 'dashboard.html'

    def get(self, request):

        # retrieve info from user cards
        if self.request.user.is_authenticated:
            # get a list of all card ids in practice
            user_exercise_rec = Card.objects.filter(card_creator=self.request.user)
        else:
            user_exercise_rec = Card.objects.filter(card_creator__username='guest_user')

        total_num_card = user_exercise_rec.count()

        if total_num_card == 0:
            predicted_level = 0
            total_attempts = 0
            avg_attempt = 0
            total_attempts_today = 0

        else:
            # TODO: fix the function for prediction
            # predicted_level = int(np.sum(
            # predicted_level_list[:, 0])/total_num_q*10)
            # get predicted level
            predicted_level_list = get_predicted_level(user_exercise_rec)
            predicted_level = int(np.sum(
                predicted_level_list[:, 0])/10)

            total_attempts = user_exercise_rec.aggregate(
                Sum('attempt_count')).get(
                    'attempt_count__sum')
            avg_attempt = user_exercise_rec.aggregate(
                Avg('attempt_count')).get(
                    'attempt_count__avg')
            total_attempts_today = user_exercise_rec.filter(
                last_trial_date__date=datetime.date.today()).aggregate(
                    Sum('attempt_count')).get(
                        'attempt_count__sum')

        # Todo: add more analytical items
        # Todo: add diff of last and current score
        # last_total_score = user_exercise_rec.aggregate(
        #     Sum('proficiency_score'))
        card_rank = get_predicted_level(user_exercise_rec, delta_t_ahead=0)
        if card_rank.size == 0:
            uptodate_total_score = 0
        else:
            uptodate_total_score = np.sum(card_rank[:, 0])

        context = {'section': 'dashboard',
                   'predicted_level': predicted_level,
                   'total_attempts_today': total_attempts_today,
                   'total_score': round(uptodate_total_score, 1),
                   'total_num_card': total_num_card,
                   'total_attempts': total_attempts,
                   'avg_attempt': round(avg_attempt, 1)
                   }

        return render(request, self.template_name, context)
