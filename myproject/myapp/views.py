from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import VotingForm, RegistrationForm, RosterForm
from .models import Votes

from .teamBalancer import *


class SignUp(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def vote_list(request):
    """
    Show all votes submitted by the user.
    :param request:
    :return:
    """
    posts = Votes.objects.filter(user=request.user).order_by('published_date')
    user_count = User.objects.values().exclude(id=request.user.id).count()
    progress = {
        'user_count': User.objects.values().exclude(id=request.user.id).count(),
        'post_count': Votes.objects.filter(user=request.user).count()
    }
    return render(request, 'vote_list.html', {'posts': posts, 'progress': progress})


def vote_new(request):
    if request.method == "POST":
        form = VotingForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('vote_edit', pk=post.pk)
    else:
        form = VotingForm(uid=request.user.id)  # passes User ID to form class to exclude current user from drop-down
    return render(request, 'votingForm.html', {'form': form})


def vote_detail(request, pk):
    post = get_object_or_404(Votes, pk=pk)
    if post.user == request.user:
        return render(request, 'vote_detail.html', {'post': post})
    else:
        return HttpResponseForbidden("You can't view this vote.")


def vote_edit(request, pk):
    post = get_object_or_404(Votes, pk=pk)
    if not post.user == request.user:
        return HttpResponseForbidden("Oi cheeky! You can't edit this vote.")
    if request.method == "POST":
        form = VotingForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            post.created_date = post.created_date
            post.save()
            return redirect('vote_detail', pk=post.pk)
    else:
        form = VotingForm(instance=post)
    return render(request, 'vote_edit.html', {'form': form})


def roster_thanks(request):
    return render(request, 'roster_thanks.html', {})


def roster(request):
    if request.method == "POST":
        form = RosterForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.published_date = timezone.now()
            players = request.POST.getlist('players')  # sets player selection as a session variable
            request.session['players'] = players
            post.save()
            return redirect('team_rosters')
    else:
        form = RosterForm()
    return render(request, 'roster_selection.html', {'form': form})


def team_rosters(request):

    players = request.session.get('players')
    print(players)

    teams = balance_teams(players, team_size=None, threshold=1, max_cycles=5)

    return render(request, 'team_rosters.html', teams)
