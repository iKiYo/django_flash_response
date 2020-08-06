from django import forms


SCORE_CHOICES = [
    ('8', '即答できる'),
    ('4', 'ＯＫ(ミスなし)'),
    ('2', '少しミスする'),
    ('1', '全然できない')
]


class ExerciseForm(forms.Form):

    def __init__(self, num_exercise, *args, **kwargs):
    # def __init__(self, quetion_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(num_exercise):
        # for i in quetion_id :
            field_name = "eval_form_" + str(i)
            self.fields[field_name] = forms.ChoiceField(
                required=True,
                widget=forms.RadioSelect,
                choices=SCORE_CHOICES,
            )


# class SimpleExerciseForm(forms.Form):

#     radio_score_eval = forms.ChoiceField(
#         required=True,
#         widget=forms.RadioSelect,
#         choices=SCORE_CHOICES,
#     )
