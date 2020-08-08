# balanceTeams.py
# Creates two random teams from a list players, balanced according to how they're each rated against particular skills

from .models import Votes

import pandas as pd
import numpy as np
from itertools import combinations
import logging
import math
from random import choice, randint
import operator

from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from functools import partial


cache = TTLCache(maxsize=100, ttl=300)


logging.getLogger().setLevel(logging.INFO)  # default root logger to info level, instead of warning

# Set skill names and importance of each skill here
WEIGHTS = dict({
    "attack": 2,
    "defense": 2,
    "possession": 2,
    "stamina": 1,
    "mobility": 1
})


class Player:

    def __init__(self, name):
        """
        Defines a football player class.
        :param name: The player's name, str.
        """
        self.name = name
        self.skill_names = list(WEIGHTS.keys())

    def get_name(self):
        return self.name

    @cached(cache=cache, key=partial(hashkey, 'get_votes'))
    def get_votes(self):
        attributes = ['player'] + self.skill_names
        player_votes = Votes.objects.filter(player=self.name).values_list(
            *attributes
        )
        return pd.DataFrame(player_votes, columns=attributes)

    @cached(cache=cache, key=partial(hashkey, 'get_skill_scores'))
    def get_skill_scores(self, skills="all"):
        """
        Calculate score per skill
        :param skills: Skills to calculate average scores for (not yet implemented)
        :type skills: list
        :return: Average scores for each skill
        :rtype: pandas.core.series.Series
        """
        votes = self.get_votes()

        if votes.empty:
            logging.warning(f"{self.name} has no votes. Defaulting to skill scores of 5.")
            return pd.Series([5, 5, 5, 5, 5], index=self.skill_names)
        elif skills == "all":
            return votes[votes.columns[~votes.columns.isin(["name", "player"])]].apply(np.mean)
        else:
            return votes[skills].apply(np.mean)

    @cached(cache=cache, key=partial(hashkey, 'get_overall_score'))
    def get_overall_score(self, skills="all", weights=WEIGHTS):
        """
        Calculate overall skill level of the player
        :param weights: Relative importance of each skill
        :type weights: dict
        :param skills: Which skills to include in calculation of overall score, default is 'all'
        :type skills: str or list
        :return: Player's overall score
        :rtype: float
        """

        scores = self.get_skill_scores(skills)

        if weights is None:
            return np.average(scores)
        else:
            skill_weights = [weights[skill] for skill in scores.keys()]
            return np.average(scores, weights=skill_weights)

    @cached(cache=cache, key=partial(hashkey, '__str__'))
    def __str__(self):
        player_score = self.get_overall_score()
        return f"Name: {self.name}, Score: {player_score}"


class Team:

    def __init__(self, name, players=None):
        """
        Defines a football team class.
        :param name: Team name.
        :param players: (Optional) Argument to the Team constructor to allow passing in a list of players right away.
        """
        self.name = name
        if players is not None:
            self._players = players
        else:
            self._players = list()

        assert all([isinstance(p, Player) for p in self._players]),\
            "Please ensure all players are of Player class."

    def get_players(self):
        return [player.get_name() for player in self._players]

    def get_team_size(self):
        return len(self._players)

    def add_player(self, obj):
        if isinstance(obj, Player):
            self._players.append(obj)
        else:
            print("Please provide player object")

    def get_player_scores(self):
        """
        Returns the scores of each player in the team.
        :return:
        """
        scores = [player.get_overall_score() for player in self._players]  # calculate avg score of each player
        return scores

    def get_team_score(self):
        """
        Getter method for the total score of all players in the team.
        :return:
        """
        return sum([player.get_overall_score() for player in self._players])

    def get_mvp(self):
        """
        Get the name of the strongest player on the team.
        :return:
        """
        scores = self.get_player_scores()
        players = [player.get_name() for player in self._players]
        player_scores = dict(zip(players, scores))
        return max(player_scores.items(), key=operator.itemgetter(1))[0]

    def intersection(self, other_team):
        """
        Get overlapping players between this team and another team.
        :param other_team:
        :return:
        """
        a = self.get_players()
        b = other_team.get_players()
        return list(set(a) & set(b))

    def team_difference(self, other_team):
        """
        Calculate the point difference between one team and another team.
        :param other_team:
        :return:
        """
        team_score = self.get_team_score()
        other_team_score = other_team.get_team_score()
        return team_score - other_team_score

    def __iter__(self):
        """
        Allows you to iterate over your team and get each player.
        :return:
        """
        return iter(self._players)

    def __str__(self):
        """
        Defines how the class prints
        :return:
        """
        out = [f"Team name: {self.name}", f"Team score: {self.get_team_score()}", "Players:"]
        out.extend(str(player) for player in self)
        return "\n".join(out)


def balance_teams(players, team_size=5, threshold=0.5, max_cycles=20, **kwargs):
    """
    Recursive function to finds all possible team configurations for a set of players. If none are found within the
    threshold, it returns the closest match.
    :param players: List of player names.
    :param team_size: Int. Number of players in each team.
    :param threshold: Float. User-specified maximum point difference allowed between teams.
    :param max_cycles: How many times to iterate while increasing threshold on failed matching.
    :param kwargs: Extra named arguments. Used mainly to prevent infinte recursion.
    :return: Dictionary of match configuration.
    """

    even_teams = len(players) % 2 == 0

    if team_size is None:
        team_size = math.floor(len(players) / 2)
        logging.info(f"Team size set to {team_size}")

    team_combos = list(combinations(players, team_size))

    # If uneven team matching
    if not even_teams:
        second_team_size = len(players) - team_size
        logging.info(
            f"Uneven number of players detected. Splitting into teams of {team_size} and {second_team_size}.")
        team_combos += list(combinations(players, second_team_size))

    # Create a Team object from each combination
    player_objects = [Player(player) for player in players]

    teams = []
    for combo in team_combos:
        team_players = [p for p in player_objects if p.get_name() in combo]
        team = Team(name="", players=team_players)
        teams.append(team)

    def find_matches(teams):
        """
        :param teams: List of team configurations.
        :return: Dictionary of two closely matched teams.
        """

        # Choose a random starting team lineup
        i = randint(0, len(teams) - 1)
        team_a, team_a_score = teams[i], teams[i].get_team_score()

        matched_teams = []
        for team in teams:
            if not even_teams:
                if team.get_team_size() == second_team_size:
                    if len(team_a.intersection(team)) == 0:  # no overlapping players
                        if abs(team_a.team_difference(team)) <= (threshold * 10):  # to compensate for missing player
                            matched_teams.append(team)
            else:
                if len(team_a.intersection(team)) == 0:  # no overlapping players
                    if abs(team_a.team_difference(team)) <= threshold:
                        matched_teams.append(team)

        logging.info(f"{len(matched_teams)} matches found")

        # Base cases
        if len(matched_teams) == 0:  # no matches found
            if len(teams) == 1:  # all possible teams have been analysed
                try:
                    attempts += 1
                except NameError:
                    attempts = 1

                if attempts <= max_cycles:  # increase threshold max number of times
                    logging.info(f"No matches found at current threshold level. Raising by 0.5 to {threshold + 1.5}.")
                    return balance_teams(players, team_size, threshold + 1.5, attempts=attempts)
                else:
                    return None
            else:
                logging.info("No matches found this time, moving down the list.")
                del teams[i]
                return find_matches(teams)
        else:
            # Get the two matched teams
            result = dict({
                "team_a": team_a,
                "team_b": choice(matched_teams)
            })

            # Print team information
            for k, v in result.items():
                print(f"{k} score: {v.get_team_score()}")
                print(f"{k} players: {v.get_players()}")

            # Don't send individual players' scores to the front end
            result_restricted = {
                'team_a': result['team_a'].get_players(),
                'team_b': result['team_b'].get_players()
            }

            return result_restricted

    return find_matches(teams=teams)


def main(players, team_size=5, threshold=0.5):

    results = balance_teams(players=players, team_size=team_size, threshold=threshold)

    # Print team information
    for k, v in results.items():
        print(v)

    # Return players only
    team_config = {
        'team_a': results['team_a'].get_players(),
        'team_b': results['team_b'].get_players()
    }

    return team_config


if __name__ == "__main__":

    # players = ['Nik Fury', 'Peter Parker', 'Clint Barton', 'Steve Rogers', 'Tony Stark',
    #            'Natasha Romanov', 'Phil Coulson', 'Bruce Banner', 'Thor Odinson', 'Wanda Maximoff']

    main()
