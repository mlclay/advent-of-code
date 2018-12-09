#!/usr/bin/python
import os
import re
from collections import defaultdict, deque

LINE_PATTERN = r'(?P<players>\d+) players; last marble is worth (?P<rounds>\d+) points'
LINE_REGEX = re.compile(LINE_PATTERN)


def parse_input():
    """
    Parse input.txt to list of tuple(player count, final marble)

    :return: list of tuples
    """

    games = []

    with open('input.txt', 'r') as txt:
        for line in txt:
            match = LINE_REGEX.match(line.strip())

            if match:
                players = int(match.group('players'))
                rounds = int(match.group('rounds'))

                games.append((players, rounds))

    return games


def play_out_game(game):
    """
    Play out game based on player count and final marble (turn)

    :param game: tuple of player count and final marble
    :return: dict of player scores
    """
    player_scores = defaultdict(int)
    players = [x for x in range(1, game[0] + 1)]
    circle = deque(maxlen=game[1] + 1)

    circle.append(0)

    for turn in range(1, game[1] + 1):
        current_player = players[(turn % len(players)) - 1]

        if turn % 23:
            insert_position = 2 % len(circle)
            circle.insert(insert_position, turn)
            circle.rotate(-1 * insert_position)
            if os.environ.get('DEBUG', False):
                print(f'{turn}\t[{current_player}]: {[x for x in circle]}')
        else:
            circle.rotate(6)
            removed_marble = circle.pop()
            player_scores[current_player] += removed_marble + turn

    return player_scores


def main():
    games = parse_input()

    for game in games:
        player_scores = play_out_game(game)
        print(f'{game[0]} players; last marble is worth {game[1]} points: high score is {max(player_scores.values())}')


if __name__ == '__main__':
    main()
