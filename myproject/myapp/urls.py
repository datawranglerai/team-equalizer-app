from django.urls import path
from . import views

urlpatterns = [
    path('vote/list', views.vote_list, name='vote_list'),
    path('vote/new/', views.vote_new, name='vote_new'),
    path('vote/<int:pk>/', views.vote_detail, name='vote_detail'),
    path('vote/<int:pk>/edit/', views.vote_edit, name='vote_edit'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('roster_selection/', views.roster, name='roster_selection'),
    path('roster_thanks/', views.roster_thanks, name='thank_you'),
    path('team_rosters/', views.team_rosters, name='team_rosters')
]
