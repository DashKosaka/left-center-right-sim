import numpy as np
import sys
import json

from argh import dispatch_command, arg


def simulate_cpu(config):

    # Simulation setup
    num_iters = config['simulations']

    # Game setup
    num_players = config['players']
    num_dice = config['dice']
    num_coins = config['coins']
    starting_player = 0

    # Probability
    weight = np.zeros(4, dtype=np.float64)
    weight[:] = (config['keep_weight'], config['center_weight'], config['left_weight'], config['right_weight'])
    weight = np.cumsum(weight / weight.sum())

    # Monte-Carlo simulations
    win_counts = np.zeros(num_players)
    num_rotations = []
    for iter_idx in range(num_iters):

        if iter_idx % 100 == 0:
            print(f'Starting iter {iter_idx}...')

        game_state = np.full(num_players, fill_value=num_coins, dtype=np.int)

        # Go until there is only one more player left with coins
        curr_rotations = 0
        player_turn = starting_player
        while (game_state >= 1).sum() > 1:
            if player_turn == starting_player:
                curr_rotations += 1

            # Skip player if no coins
            if game_state[player_turn] == 0:
                pass

            # Proceed with current player
            else:
                player_coins = game_state[player_turn]

                # Roll the dice
                dice_rolls = np.random.rand(num_dice)

                for dice_idx in range(min(player_coins, num_dice)):
                    dice_value = dice_rolls[dice_idx]

                    # Probability to keep
                    if dice_value < weight[0]:
                        game_state[player_turn] = game_state[player_turn]

                    # Probability for center
                    elif dice_value < weight[1]:
                        game_state[player_turn] -= 1

                    # Probability for left
                    elif dice_value < weight[2]:
                        game_state[player_turn] -= 1
                        game_state[(player_turn - 1) % num_players] += 1

                    # Probability for right
                    else:
                        game_state[player_turn] -= 1
                        game_state[(player_turn + 1) % num_players] += 1

            # Go to next player
            player_turn = (player_turn + 1) % num_players

        win_counts[game_state.argmax()] += 1
        num_rotations.append(curr_rotations)

    print('Raw Win Counts')
    print(win_counts)
    print('Win Percentages')
    print(win_counts / win_counts.sum())
    print('Rotation Stats [min/mean/median/max]:', np.min(num_rotations), np.mean(num_rotations), np.median(num_rotations), np.max(num_rotations))

def simulate(
    config_path: 'Parameter configuration to use'
):
    with open(config_path, 'r') as f:
        config = json.load(f)


    simulate_cpu(config)




def main():
    dispatch_command(simulate)
    

if __name__ == '__main__':
    sys.exit(main())





