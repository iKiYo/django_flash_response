import json
import uuid
import numpy as np

from django.conf import settings
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import (
    View, TemplateView
)

from .forms import ExerciseForm  # SimpleExerciseForm
from card.models import Card, get_predicted_level


class HomePageView(TemplateView):
    template_name = 'home.html'


class ExerciseSet(object):
    """
    store exercise information in session model
    """
    def __init__(self, request):
        self.session = request.session
        exercise_set = self.session.get(settings.EXERCISE_SESSION_ID)
        if not exercise_set:
            exercise_set = self.session[settings.EXERCISE_SESSION_ID] = {}
        self.exercise_set = exercise_set

    def add(self, cards_to_ex):
        # get the values from selected cards in Queryset format
        qid_qs = list(cards_to_ex.values('card_id'))
        #print(f": ## {qid_qs}" )

        # change uuid to str
        qid_qs = [dict([a, str(x)] for a, x in q.items()) for q in qid_qs]
        #print(f": ### {(qid_qs[0])}" )

        # cast each q_id in dict to json(serialize) and set to session
        for i in range(len(qid_qs)):
            #print(type(json.dumps(qid_qs[i])))
            self.exercise_set[i] = json.dumps(qid_qs[i])

        self.save()

    def save(self):
        self.session.modified = True


class ExerciseView(View):

    def __init__(self):
        # FIX get num q from session vaiables
        self.num_card = 5
        self.q_ids = {}

    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            user_exercise_rec = Card.objects.filter(
                card_creator=self.request.user)
        else:
            # set user no.1 for guest users
            user_exercise_rec = Card.objects.filter(
                card_creator__username='guest_user')

        # get a list of all card ids in practice ordered by current score
        q_rank = get_predicted_level(user_exercise_rec, delta_t_ahead=0)

        if q_rank.size == 0:
            # TODO: send error message and ask user to regester exercises
            top_uuid = []
            print("WARNING(flash-response admin):"
                  + "There is no cards to practice, register cards")
        else:
            top_ids = np.argsort(q_rank[:,0])[:self.num_card]
            top_uuid = q_rank[top_ids,1]

        # get top K cards to exercise
        cards = Card.objects.filter(card_id__in=top_uuid)

        # register card to practice to a session object
        exercise_set = ExerciseSet(request)
        exercise_set.add(cards)

        # prepare the multiple choice form for rendering
        eval_forms = ExerciseForm(self.num_card)
        # TRY OPTIMIZE: this way looks simpler
        #simple_eval_forms = SimpleExerciseForm() 
        context = {'num_card':self.num_card,
                   'cards': cards,
                   'form': eval_forms,
                   'exercise_set': zip(cards, eval_forms),
                   # 'form': simple_eval_forms, 
                   # 'exercise_set': zip(cards, simple_eval_forms),
        }

        return render(request, 'exercise.html', context)

    def post(self, request, *args, **kwargs):
        score_data = ExerciseForm(self.num_card, request.POST)
        q_ids = ExerciseSet(request)

        if self.request.user.is_authenticated:
            user_exercise_rec = Card.objects.filter(card_creator=self.request.user)
        else:
            user_exercise_rec = Card.objects.filter(card_creator__username='guest_user')

        if score_data.is_valid():
            # FOR MY STUDY to access the data in Form Object, use .data
            #print(score_data.cleaned_data.values(), "scoredata")
            #print(q_ids.exercise_set.values())

            for q_id, eval in zip (q_ids.exercise_set.values(), score_data.cleaned_data.values()):
                # KEEP: debug for possibly adding more fields to store
                #print("registered", q_id, eval, uuid.UUID(json.loads(q_id).get("card_id")))

            # TODO simplify here somehow like line below(without UUID)
                selected_q = get_object_or_404(user_exercise_rec,
                                               card_id=uuid.UUID(json.loads(q_id).get("card_id")))
                selected_q.proficiency_score += int(eval)
                selected_q.attempt_count += 1
                selected_q.last_trial_date = timezone.now()
                selected_q.save()

                return HttpResponseRedirect('accounts')

        else:
            # Todo: set exception
            print("ERROR(flash-response admin): form was invalid")
            return HttpResponseRedirect('accounts')

