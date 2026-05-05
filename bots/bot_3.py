#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from itertools import combinations

def card_value(card):
    return card // 4 + 2

def card_suit(card):
    return card % 4

def evaluate_hand(cards):
    values = sorted([card_value(c) for c in cards], reverse=True)
    suits = [card_suit(c) for c in cards]
    
    flush = len(set(suits)) == 1
    straight = False
    straight_high = 0
    for i in range(len(values)-4):
        if values[i] - values[i+4] == 4:
            straight = True
            straight_high = values[i]
            break
    if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
        straight = True
        straight_high = 5
    
    if straight and flush:
        if values[0] == 14 and values[1] == 13:
            return (9, values[:5])
        return (8, [straight_high] + values[1:5])
    
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    
    if sorted_counts[0][1] == 4:
        kicker = [v for v in values if v != sorted_counts[0][0]][0]
        return (7, [sorted_counts[0][0], kicker])
    
    if sorted_counts[0][1] == 3 and len(sorted_counts) > 1 and sorted_counts[1][1] == 2:
        return (6, [sorted_counts[0][0], sorted_counts[1][0]])
    
    if flush:
        return (5, values[:5])
    
    if straight:
        return (4, [straight_high])
    
    if sorted_counts[0][1] == 3:
        kickers = [v for v in values if v != sorted_counts[0][0]][:2]
        return (3, [sorted_counts[0][0]] + kickers)
    
    if sorted_counts[0][1] == 2 and len(sorted_counts) > 1 and sorted_counts[1][1] == 2:
        kicker = [v for v in values if v != sorted_counts[0][0] and v != sorted_counts[1][0]][0]
        return (2, [sorted_counts[0][0], sorted_counts[1][0], kicker])
    
    if sorted_counts[0][1] == 2:
        kickers = [v for v in values if v != sorted_counts[0][0]][:3]
        return (1, [sorted_counts[0][0]] + kickers)
    
    return (0, values[:5])

def get_preflop_strength(card1, card2):
    val1 = card_value(card1)
    val2 = card_value(card2)
    suit1 = card_suit(card1)
    suit2 = card_suit(card2)
    
    if val1 < val2:
        val1, val2 = val2, val1
    
    pair = val1 == val2
    suited = suit1 == suit2
    gap = val1 - val2
    
    if pair:
        if val1 >= 14:
            return 100
        elif val1 >= 13:
            return 95
        elif val1 >= 12:
            return 88
        elif val1 >= 11:
            return 82
        elif val1 >= 10:
            return 76
        elif val1 >= 9:
            return 70
        elif val1 >= 8:
            return 65
        elif val1 >= 7:
            return 60
        elif val1 >= 6:
            return 55
        else:
            return 50
    elif val1 >= 14 and val2 >= 13:
        return 90 if suited else 85
    elif val1 >= 14 and val2 >= 12:
        return 85 if suited else 78
    elif val1 >= 14 and val2 >= 11:
        return 80 if suited else 72
    elif val1 >= 13 and val2 >= 12:
        return 78 if suited else 70
    elif val1 >= 13 and val2 >= 11:
        return 75 if suited else 65
    elif val1 >= 12 and val2 >= 11:
        return 72 if suited else 62
    elif val1 >= 14 and val2 >= 10:
        return 75 if suited else 65
    elif val1 >= 13 and val2 >= 10:
        return 70 if suited else 60
    elif val1 >= 12 and val2 >= 10:
        return 68 if suited else 58
    elif val1 >= 11 and val2 >= 10:
        return 65 if suited else 55
    elif suited and gap <= 2:
        return 55 + (14 - val1)
    elif gap == 0:
        return 50 + (14 - val1)
    else:
        return max(10, 40 - (14 - val1) - gap)

def calculate_draw_outs(my_cards, public_cards):
    outs = 0
    all_cards = set(my_cards + public_cards)
    deck = set(range(52)) - all_cards
    
    my_values = [card_value(c) for c in my_cards]
    my_suits = [card_suit(c) for c in my_cards]
    public_values = [card_value(c) for c in public_cards]
    public_suits = [card_suit(c) for c in public_cards]
    
    all_values = my_values + public_values
    all_suits = my_suits + public_suits
    
    flush_draw = False
    for s in range(4):
        count = all_suits.count(s)
        if count == 4:
            flush_draw = True
            outs += 9
        elif count == 3 and len(public_cards) <= 3:
            outs += 6
    
    open_ended = False
    gutshot = False
    unique_values = sorted(list(set(all_values)))
    for i in range(len(unique_values) - 3):
        seq = unique_values[i:i+4]
        if seq[-1] - seq[0] == 3:
            open_ended = True
            outs += 8
        elif seq[-1] - seq[0] == 4 and (seq[0] + 1 not in unique_values or seq[-1] - 1 not in unique_values):
            gutshot = True
            outs += 4
    
    for v in my_values:
        if all_values.count(v) == 1:
            outs += 3 * 0.5
        elif all_values.count(v) == 2:
            outs += 2 * 0.8
        elif all_values.count(v) == 3:
            outs += 1
    
    return min(outs, 20)

def get_current_hand_strength(my_cards, public_cards):
    if not public_cards:
        return get_preflop_strength(my_cards[0], my_cards[1])
    
    all_cards = my_cards + public_cards
    best_score = None
    for combo in combinations(all_cards, 5):
        score = evaluate_hand(list(combo))
        if best_score is None or score > best_score:
            best_score = score
    
    strength = 50
    if best_score[0] >= 7:
        strength = 95 + (best_score[0] - 7) * 2
    elif best_score[0] >= 6:
        strength = 90
    elif best_score[0] >= 5:
        strength = 85
    elif best_score[0] >= 4:
        strength = 80
    elif best_score[0] >= 3:
        strength = 70
    elif best_score[0] >= 2:
        strength = 60
    elif best_score[0] >= 1:
        strength = 50 + (best_score[1][0] - 2) * 3
    else:
        strength = 30 + (best_score[1][0] - 2) * 2
    
    return min(strength, 100)

def get_action():
    data = json.loads(sys.stdin.read())
    
    my_id = data['my_id']
    my_chips = data['my_chips']
    my_cards = data['my_cards']
    public_cards = data['public_cards']
    history = data['history']
    dealer_id = data['dealer_id']
    
    round_num = 0
    my_bet_in_round = 0
    opponent_bet_in_round = 0
    pot_size = 0
    last_raise = 0
    
    sb_id = (dealer_id + 1) % 2
    bb_id = (dealer_id + 2) % 2
    pot_size = 50 + 100
    
    for h in history:
        round_num = h['round']
        if h['player_id'] == my_id:
            if h['action'] > 0:
                my_bet_in_round += h['action']
                pot_size += h['action']
            elif h['action_type'] == 'call':
                call_amt = opponent_bet_in_round - my_bet_in_round
                my_bet_in_round += call_amt
                pot_size += call_amt
        else:
            if h['action'] > 0:
                opponent_bet_in_round += h['action']
                last_raise = h['action']
                pot_size += h['action']
            elif h['action_type'] == 'call':
                call_amt = my_bet_in_round - opponent_bet_in_round
                opponent_bet_in_round += call_amt
                pot_size += call_amt
    
    total_bet_needed = max(0, opponent_bet_in_round - my_bet_in_round)
    
    position_factor = 1.0
    if my_id == dealer_id:
        position_factor = 1.15
    elif my_id == sb_id:
        position_factor = 0.9
    
    if round_num == 0:
        hand_strength = get_preflop_strength(my_cards[0], my_cards[1])
        adjusted_strength = hand_strength * position_factor
    else:
        hand_strength = get_current_hand_strength(my_cards, public_cards)
        outs = calculate_draw_outs(my_cards, public_cards)
        cards_left = 50 - len(public_cards) - 2
        draw_odds = outs / cards_left if cards_left > 0 else 0
        adjusted_strength = hand_strength * 0.7 + draw_odds * 30
        adjusted_strength = min(adjusted_strength, 100)
    
    pot_odds = 0
    if total_bet_needed > 0:
        pot_odds = total_bet_needed / (pot_size + total_bet_needed)
    
    if total_bet_needed > my_chips:
        if adjusted_strength >= 80:
            return -2
        else:
            return -1
    
    if round_num == 0:
        if adjusted_strength >= 90:
            if total_bet_needed == 0:
                return min(my_chips, 200)
            elif total_bet_needed <= 100:
                return min(my_chips - total_bet_needed, max(200, total_bet_needed * 2))
            else:
                if adjusted_strength >= 95:
                    return -2
                else:
                    return 0
        elif adjusted_strength >= 75:
            if total_bet_needed <= 100:
                return 0
            elif total_bet_needed <= 200 and adjusted_strength >= 80:
                return 0
            else:
                return -1
        elif adjusted_strength >= 55:
            if total_bet_needed == 0:
                return 0
            elif total_bet_needed <= 50:
                return 0
            else:
                return -1
        else:
            if total_bet_needed == 0:
                return 0
            else:
                return -1
    else:
        if adjusted_strength >= 85:
            if total_bet_needed > 0:
                raise_amount = min(my_chips - total_bet_needed, max(100, int(pot_size * 0.5), total_bet_needed * 2))
                if raise_amount > 0:
                    return raise_amount
                else:
                    return -2 if my_chips > total_bet_needed else 0
            else:
                return min(my_chips, max(100, int(pot_size * 0.5)))
        elif adjusted_strength >= 70:
            if total_bet_needed <= my_chips * 0.15:
                return 0
            elif total_bet_needed == 0:
                return 0
            else:
                return -1
        elif adjusted_strength >= 50:
            if total_bet_needed == 0:
                return 0
            elif total_bet_needed <= my_chips * 0.08:
                return 0
            else:
                return -1
        else:
            return -1

if __name__ == '__main__':
    print(get_action())
