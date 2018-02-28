from jaipur import Jaipur
from jaipur_players import RandomPlayer, JewelPlayer, GreedyPlayer

def play_matches(n_matches, time_limit, player_agents, cpu_agents):
    total_wins = {agent.name : 0 for agent in player_agents + cpu_agents}
    total_timeouts = 0.
    total_forfeits = 0.

    for idx, agent in enumerate(player_agents):
        for idy, agent_2 in enumerate(cpu_agents):
            for _ in range(n_matches):
                j = Jaipur(agent, agent_2)
                winner, move_history, outcome = j.play()
                total_wins[winner] += 1

    print(total_wins)

if __name__ == "__main__":
    play_matches(10, 1000, [JewelPlayer('Rohit'), GreedyPlayer('Theo')], [RandomPlayer('Albert')])