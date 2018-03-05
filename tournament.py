from jaipur import Jaipur
from jaipur_players import RandomPlayer, JewelPlayer, GreedyPlayer, MinimaxPlayer, AlphaBetaPlayer
from jaipur_players import custom_score, custom_score_2, custom_score_3
from collections import namedtuple

Agent = namedtuple("Agent", ["player", "name"])

# for each player agent play matches against all the CPU agents and record scores
def play_round(player_agent, cpu_agents, win_counts, num_matches):
    timeout_count = 0
    forfeit_count = 0
    illegal_count = 0
    
    # Number of matches per cpu
    for _ in range(num_matches):

        # Give both players the chance to play first
        games = sum([[Jaipur(player_agent, agent),
                    Jaipur(agent, player_agent)] 
                    for agent in cpu_agents], [])

        # play a single game
        for game in games:
            winner, _, termination = game.play()
            win_counts[winner] += 1

            # add to early termination
            if termination == 'forfeit':
                forfeit_count += 1
            elif termination == 'timeout':
                timeout_count += 1
            elif termination == 'illegal move':
                illegal_count += 1

    return timeout_count, forfeit_count, illegal_count

def update(total_wins, wins):
    for player in total_wins:
        total_wins[player] += wins[player]

    return total_wins


# test all player agents versus the CPUs and output the results
def play_matches(n_matches, player_agents, cpu_agents):
    total_wins = {agent.name : 0 for agent in cpu_agents}
    total_timeouts = 0
    total_forfeits = 0
    total_illegals = 0

    total_matches = 2 * n_matches * len(player_agents)

    print('\n{:^9}{:^13}'.format('Match #', "Opponent") + ''.join(['{:^13}'.format(x.name) for x in cpu_agents]))
    print('{:^9}{:^13} '.format('', '') + ''.join('{:^5}| {:^5}'.format('Won', 'Lost') for agent in cpu_agents))

    for idx, agent in enumerate(player_agents):
        wins = {key.name :0 for key in cpu_agents}
        wins[agent.name] = 0

        print("{!s:^9}{:^13}".format(idx + 1, agent.name), end="", flush=True)

        counts = play_round(agent, cpu_agents, wins, n_matches)
        total_wins = update(total_wins, wins)
        total_timeouts += counts[0]
        total_forfeits += counts[1]
        total_illegals += counts[2]
        _total = 2*n_matches
        round_totals = sum([[wins[agent.name], _total - wins[agent.name]]
                            for agent in cpu_agents], [])
        
        print(' ' + ' '.join([
            '{:^5}| {:^5}'.format(
                round_totals[i], round_totals[i+1]
            ) for i in range(0, len(round_totals), 2)
        ]))

    print('-'*74)
    print('{:^9}{:^13}'.format("", "Win Rate:") + 
            ''.join([
                '{:^13}'.format(
                    '{:.1f}%'.format(100 * total_wins[x[1].name] / total_matches)
                    ) for x in enumerate(cpu_agents)
    ]))

    if total_timeouts:
        print(("\nThere were {} timeouts during the game.").format(total_timeouts))
    if total_forfeits:
        print(("\nThere were {} forfeits during the game.").format(total_forfeits))
    if total_illegals:
        print(("\nThere were {} illegal moves during the game.".format(total_illegals)))

if __name__ == "__main__":
    JewelAgent = Agent(JewelPlayer(), "Jewel")
    GreedyAgent = Agent(GreedyPlayer(), "Greedy")
    RandomAgent = Agent(RandomPlayer(), "Random")
    MinimaxAgent = Agent(MinimaxPlayer(score_fn = custom_score), "Minimax 1")
    MinimaxAgent_2 = Agent(MinimaxPlayer(score_fn = custom_score_2), "Minimax 2")
    MinimaxAgent_3 = Agent(MinimaxPlayer(score_fn = custom_score_3), "Minimax 3")
    AlphabetaAgent = Agent(AlphaBetaPlayer(score_fn = custom_score), "AlphaBeta 1")
    AlphabetaAgent_2 = Agent(AlphaBetaPlayer(score_fn = custom_score_2), "AlphaBeta 2")
    AlphabetaAgent_3 = Agent(AlphaBetaPlayer(score_fn = custom_score_3), "AlphaBeta 3")
    play_matches(10, [JewelAgent, GreedyAgent, RandomAgent], [MinimaxAgent, AlphabetaAgent])