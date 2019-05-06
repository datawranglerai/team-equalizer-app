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
                  'created_date',)

    def __init__(self, *args, **kwargs):
        """
        Overrrides drop-down field.
        Creates a dynamic drop down form field of registered users. Excludes logged in user and any players that the
        logged in user has already voted on.
        :param uid: ID of the currently logged in user.
        :param args:
        :param kwargs:
        """

        uid = kwargs.pop('uid', None)

        super(VotingForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)

        if instance and instance.player:
            self.fields['player'].disabled = True
            self.fields['created_date'].disabled = True
        else:
            # Get list of names of all users, excluding currently logged in user
            users = User.objects.values().exclude(id=uid)
            first_names = users.values_list('first_name', flat=True)
            last_names = users.values_list('last_name', flat=True)

            human_names = []
            for i in range(len(first_names)):
                human_names.append(f"{first_names[i]} {last_names[i]}")

            # Players the user has already voted on
            voted_players = list(
                Votes.objects.filter(user_id=uid).values_list('player', flat=True))  # returns an iterable

            # Return players that don't match current user and haven't been voted on
            valid_players = [name for name in human_names if name not in voted_players]
            form_user_choices = list(zip(valid_players, valid_players))

            self.fields['player'] = forms.ChoiceField(choices=form_user_choices)


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



