from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Votes, Roster


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",)


class VotingForm(forms.ModelForm):

    class Meta:
        model = Votes
        fields = ('player',
                  'skill_a',
                  'skill_b',
                  'skill_c',
                  'skill_d',
                  'skill_e',
                  'created_date',
                  'published_date',)

    def __init__(self, *args, **kwargs):
        """
        Creates a dynamic drop down form field of registered users
        :param args:
        :param kwargs:
        """

        super(VotingForm, self).__init__(*args, **kwargs)

        users = User.objects.values()
        first_names = users.values_list('first_name', flat=True)
        last_names = users.values_list('last_name', flat=True)

        human_names = []
        for i in range(len(first_names)):
            human_names.append(f"{first_names[i]} {last_names[i]}")

        USER_CHOICES = list(zip(human_names, human_names))

        self.fields['player'] = forms.ChoiceField(choices=USER_CHOICES)


class RosterForm(forms.ModelForm):
    """
    Multiple choice form to select active players
    """

    class Meta:
        model = Roster
        fields = ('players', 'published_date',)

    def __init__(self, *args, **kwargs):
        """
        Creates a dynamic drop down form field of registered users
        :param args:
        :param kwargs:
        """

        super(RosterForm, self).__init__(*args, **kwargs)

        users = User.objects.values()
        first_names = users.values_list('first_name', flat=True)
        last_names = users.values_list('last_name', flat=True)

        human_names = []
        for i in range(len(first_names)):
            human_names.append(f"{first_names[i]} {last_names[i]}")

        USER_CHOICES = list(zip(human_names, human_names))

        # APPROVAL_CHOICES = (
        #     ('yes', 'Yes'),
        #     ('no', 'No'),
        #     ('cancelled', 'Cancelled'),
        # )

        self.fields['players'] = forms.MultipleChoiceField(choices=USER_CHOICES, widget=forms.CheckboxSelectMultiple())



