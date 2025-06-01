import random

def evaluate_hand_strength(hand, community_cards):
    # Simplified hand strength evaluator.
    # Returns a float between 0 (worst) and 1 (best).

    # Start with base value
    score = 0.0

    # Count pairs in hand
    if hand[0].rank == hand[1].rank:
        score += 0.5

    # High card bonus
    high_ranks = ['J', 'Q', 'K', 'A']
    for card in hand:
        if card.rank in high_ranks:
            score += 0.2

    # Suited bonus
    if hand[0].suit == hand[1].suit:
        score += 0.1

    # Basic synergy with community (e.g., mathching ranks)
    all_cards = hand + community_cards
    ranks = [card.rank for card in all_cards]
    for rank in set(ranks):
        if ranks.count(rank) >= 2:
            score += 0.1

    return min(score, 1.0)


def calculate_pot_odds(current_bet, pot_size, player_chips):
    # Calculates pot odds as a float between 0 and 1.
    if current_bet == 0:
        return 1.0
    elif current_bet == 20:
        return 0.3
    elif current_bet > player_chips:
        return 0.0
    return current_bet / (pot_size + current_bet)

def decide_action(player, game):
    # Decides AI action based on hand strength and pot odds.
    # Returns: 'call', 'raise' or 'fold'
    hand_strength = evaluate_hand_strength(player.hand, game.community_cards)
    pot_odds = calculate_pot_odds(game.betting.current_bet, game.betting.pot, player.chips)
    
    if hand_strength < 0.3 and pot_odds < 0.2:
        game.betting.fold(player)
        return 'fold'
    elif hand_strength > 0.7:
        raise_amount = game.betting.current_bet + random.randint(10, 50)
        game.betting.raise_bet(player, raise_amount, game.players)
        return f'raise to {raise_amount}'
    else:
        if player.is_called:
            return 'checked'
        else:     
            game.betting.call(player)
            return 'call'    
    