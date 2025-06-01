
from collections import Counter
from itertools import combinations

RANK_ORDER = { '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                '7': 7, '8': 8, '9': 9, '10': 10,
                 'J': 11, 'Q': 12, 'K': 13, 'A': 14 }

HAND_RANKS = {
    "High Card": 0,
    "One Pair": 1,
    "Two Pair": 2,
    "Three of a Kind": 3,
    "Straight": 4,
    "Flush": 5,
    "Full House": 6,
    "Four of a Kind": 7,
    "Straight Flush": 8,
    # We'll expand this in future steps
}

def is_straight(ranks):
    """Return highest card in straight or None"""
    ranks = sorted(set(ranks), reverse=True)
    for i in range(len(ranks) - 4):
        window = ranks[i:i+5]
        if window[0] - window[4] == 4:
            return window[0]
    # Handle Ace-low straight (A-2-3-4-5)
    if set([14, 5, 4, 3, 2]).issubset(ranks):
        return 5
    return None

def is_flush(cards):
    suits = [card.suit for card in cards]
    for suit in set(suits):
        flush_cards = [c for c in cards if c.suit == suit]
        if len(flush_cards) >= 5:
            return sorted([RANK_ORDER[c.rank] for c in flush_cards], reverse=True)[:5]
    return None

def evaluate_best_hand(cards):

    best_rank = (HAND_RANKS["High Card"], [])

    for combo in combinations(cards, 5):
        ranks = [RANK_ORDER[c.rank] for c in combo]
        suits = [c.suit for c in combo]
        rank_counts = Counter(ranks)
        counts = rank_counts.most_common()
        values = sorted(ranks, reverse = True)

        # Straight Flush
        flush_cards = [c for c in combo if suits.count(c.suit) >= 5]
        if len(flush_cards) >= 5:
            flush_ranks = [RANK_ORDER[c.rank] for c in flush_cards]
            sf_high = is_straight(flush_ranks)
            if sf_high:
                best_rank = max(best_rank, (HAND_RANKS["Straight Flush"], [sf_high]))
                continue

        # Four of a Kind
        if counts[0][1] == 4:
            kicker = max([r for r in ranks if r != counts[0][0]])
            best_rank = max(best_rank, (HAND_RANKS["Four of a Kind"], [counts[0][0], kicker]))
            continue

        # Full House
        if counts[0][1] == 3 and any(c[1] >= 2 for c in counts[1:]):
            pair = next(c[0] for c in counts[1:] if c[1] >= 2)
            best_rank = max(best_rank, (HAND_RANKS["Full House"], [counts[0][0], pair]))
            continue

        # Flush
        flush = is_flush(combo)
        if flush:
            best_rank = max(best_rank, (HAND_RANKS["Flush"], flush))
            continue

        # Straight
        straight_high = is_straight(ranks)
        if straight_high:
            best_rank = max(best_rank, (HAND_RANKS["Straight"], [straight_high]))
            continue

        if counts[0][1] == 3:
         # Three of a kind
            kickers = [r for r in values if r != counts[0][0]][:2]
            best_rank = max(best_rank, (HAND_RANKS["Three of a Kind"], [counts[0][0]] + kickers))
            continue

        # Two Pair
        if counts[0][1] == 2 and counts[1][1] == 2:
            kicker = max([r for r in values if r != counts[0][0] and r != counts[1][0]])
            pairs = sorted([counts[0][0], counts[1][0]], reverse=True)
            best_rank = max(best_rank, (HAND_RANKS["Two Pair"], pairs + [kicker]))
            continue

        # One Pair
        if counts[0][1] == 2:
            kickers = [r for r in values if r != counts[0][0]][:3]
            best_rank = max(best_rank, (HAND_RANKS["One Pair"], [counts[0][0]] + kickers))
            continue

        # High Card
        best_rank = max(best_rank, (HAND_RANKS["High Card"], values))

    return best_rank

def compare_hands(player1_cards, player2_cards, community_cards):
    """
    Compares two players' hands.
    Returns:
        1  -> player1 wins
        -1 -> player2 wins
        0  -> tie
    """

    p1_hand = evaluate_best_hand(player1_cards + community_cards)
    p2_hand = evaluate_best_hand(player2_cards + community_cards)

    if p1_hand[0] > p2_hand[0]:
        return 1
    elif p1_hand[0] < p2_hand[0]:
        return -1
    else:
        # Same hand type — compare tiebreakers
        for val1, val2 in zip(p1_hand[1], p2_hand[1]):
            if val1 > val2:
                return 1
            elif val1 < val2:
                return -1
        return 0  # Tie
