import numpy as np
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

month_in_sec = (60**2)*24*30


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.card_creator.id, filename)


def sum_exp_mem(t, a1=0.000319, a2=1.79e-7, mu1=0.35, mu2=0.321):
    return mu1 * np.exp(-a1*t) + mu2 * np.exp(-a2*t)


def imp_mem(freq, d=0.1, rate=10):
    return 0.5 / (1 + rate*np.exp(-d * freq))


def score_function(delta_t, freq):
    return (1 - imp_mem(freq)) * sum_exp_mem(delta_t) + imp_mem(freq)


def get_predicted_level(user_exercise_rec,
                        delta_t_ahead=6*month_in_sec,
                        *category):

    all_cards = user_exercise_rec.values(
        'card_id', 'last_trial_date', 'attempt_count', 'proficiency_score')
    card_rank = []
    for card in all_cards:
        diff_time = (timezone.now() - card['last_trial_date']).total_seconds()
        + delta_t_ahead
        forget_rate = score_function(diff_time, card['attempt_count'])
        predicted_score = round(forget_rate * card['proficiency_score'], 1)
        card_rank.append((predicted_score.tolist(), card['card_id']))
    return np.array(card_rank)


class Card(models.Model):
    # Todo: add the slug or title field to identify a card
    title = models.CharField(_('title'), max_length=200, default="no title")
    slug = models.SlugField(max_length=200, blank=True)
    card_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    card_creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='card_creator',
                                     on_delete=models.CASCADE
                                     )

    creation_date = models.DateTimeField(_('creation_date'), auto_now_add=True)

    question_text = models.TextField(_('question_text'), max_length=300)
    answer_text = models.TextField(_('answer_text'), max_length=300)
    answer_audio = models.FileField(_('answer_audio'),
                                    upload_to=user_directory_path,
                                    blank=True
                                   )
    category = models.CharField(_('category'),
                                max_length=200,
                                default="no category"
                                )
    subcategory = models.CharField(_('subcategory'),
                                   max_length=200,
                                   default="no subcategory"
                                   )
    detail = models.CharField(_('detail'), max_length=200, default="no detail")
    literary_style = models.BooleanField(_('literary_style'), default=False)

    proficiency_score = models.FloatField(_('proficiency_score'), default=0.0)
    attempt_count = models.IntegerField(_('attempt_count'), default=0)
    # Todo: set default date, user's regesitration date
    last_trial_date = models.DateTimeField(_('last_trial_date'),
                                           auto_now_add=True
                                           )
    # last_trial_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('category',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('card_detail', args=[self.card_id])

    def compute_score(self):
        diff_time = timezone.now() - self.last_trial_date
        forget_rate = score_function(diff_time.total_seconds(),
                                     self.attempt_count
                                     )
        print("d_t", diff_time.total_seconds(),
              "f_rate", forget_rate)
        print("pevious score", self.proficiency_score,
              "predicted score", round(forget_rate * self.proficiency_score, 1)
        )
        return round(forget_rate * self.proficiency_score, 1)
