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
    
    unique_values = sorted(list(set(values)), reverse=True)
    
    for i in range(len(unique_values) - 4):
        if unique_values[i] - unique_values[i+4] == 4:
            straight = True
            straight_high = unique_values[i]
            break
    
    if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
        straight = True
        straight_high = 5
    
    if straight and flush:
        if values[0] == 14 and values[1] == 13 and values[2] == 12 and values[3] == 11 and values[4] == 10:
            return (9, values[:5])
        return (8, [straight_high])
    
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 4:
        kicker = [v for v in values if v != sorted_counts[0][0]][0]
        return (7, [sorted_counts[0][0], kicker])
    
    if len(sorted_counts) >= 2 and sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
        return (6, [sorted_counts[0][0], sorted_counts[1][0]])
    
    if flush:
        return (5, values[:5])
    
    if straight:
        return (4, [straight_high])
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 3:
        kickers = [v for v in values if v != sorted_counts[0][0]][:2]
        return (3, [sorted_counts[0][0]] + kickers)
    
    if len(sorted_counts) >= 2 and sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
        kicker = [v for v in values if v != sorted_counts[0][0] and v != sorted_counts[1][0]][0]
        return (2, [sorted_counts[0][0], sorted_counts[1][0], kicker])
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 2:
        kickers = [v for v in values if v != sorted_counts[0][0]][:3]
        return (1, [sorted_counts[0][0]] + kickers)
    
    return (0, values[:5])

PRE_FLOP_STRENGTH = {}
for c1 in range(52):
    for c2 in range(c1 + 1, 52):
        v1 = card_value(c1)
        v2 = card_value(c2)
        s1 = card_suit(c1)
        s2 = card_suit(c2)
        
        if v1 < v2:
            v1, v2 = v2, v1
        
        pair = v1 == v2
        suited = s1 == s2
        gap = v1 - v2
        
        strength = 0
        
        if pair:
            if v1 == 14:
                strength = 100
            elif v1 == 13:
                strength = 96
            elif v1 == 12:
                strength = 92
            elif v1 == 11:
                strength = 87
            elif v1 == 10:
                strength = 81
            elif v1 == 9:
                strength = 74
            elif v1 == 8:
                strength = 67
            elif v1 == 7:
                strength = 59
            elif v1 == 6:
                strength = 51
            elif v1 == 5:
                strength = 44
            elif v1 == 4:
                strength = 37
            elif v1 == 3:
                strength = 31
            elif v1 == 2:
                strength = 26
        elif v1 == 14:
            if v2 == 13:
                strength = 93 if suited else 89
            elif v2 == 12:
                strength = 88 if suited else 83
            elif v2 == 11:
                strength = 83 if suited else 77
            elif v2 == 10:
                strength = 77 if suited else 69
            elif v2 == 9:
                strength = 70 if suited else 60
            elif v2 == 8:
                strength = 62 if suited else 52
            elif v2 == 7:
                strength = 53 if suited else 43
            elif v2 == 6:
                strength = 44 if suited else 34
            elif v2 <= 5:
                strength = 35 if suited else 25
        elif v1 == 13:
            if v2 == 12:
                strength = 82 if suited else 76
            elif v2 == 11:
                strength = 76 if suited else 68
            elif v2 == 10:
                strength = 69 if suited else 61
            elif v2 == 9:
                strength = 61 if suited else 52
            elif v2 == 8:
                strength = 52 if suited else 43
            elif v2 == 7:
                strength = 43 if suited else 34
            elif v2 <= 6:
                strength = 34 if suited else 25
        elif v1 == 12:
            if v2 == 11:
                strength = 71 if suited else 63
            elif v2 == 10:
                strength = 64 if suited else 56
            elif v2 == 9:
                strength = 56 if suited else 48
            elif v2 == 8:
                strength = 48 if suited else 40
            elif v2 == 7:
                strength = 40 if suited else 32
            elif v2 <= 6:
                strength = 32 if suited else 24
        elif v1 == 11:
            if v2 == 10:
                strength = 58 if suited else 50
            elif v2 == 9:
                strength = 51 if suited else 43
            elif v2 == 8:
                strength = 43 if suited else 35
            elif v2 == 7:
                strength = 35 if suited else 28
            elif v2 <= 6:
                strength = 28 if suited else 21
        elif v1 == 10:
            if v2 == 9:
                strength = 47 if suited else 39
            elif v2 == 8:
                strength = 40 if suited else 32
            elif v2 == 7:
                strength = 33 if suited else 26
            elif v2 <= 6:
                strength = 26 if suited else 20
        elif v1 <= 9:
            if suited and gap <= 1:
                strength = 35 + v1
            elif gap <= 1:
                strength = 28 + v1 // 2
            elif suited and gap <= 2:
                strength = 22 + v1 // 2
            else:
                strength = max(8, 18 + (v1 + v2) // 4)
        
        PRE_FLOP_STRENGTH[(c1, c2)] = strength
        PRE_FLOP_STRENGTH[(c2, c1)] = strength

def get_preflop_strength(card1, card2):
    return PRE_FLOP_STRENGTH.get((card1, card2), 50)

def calculate_outs(my_cards, public_cards):
    outs = 0
    all_cards = set(my_cards + public_cards)
    deck_size = 52 - len(all_cards)
    if deck_size <= 0:
        return 0
    
    my_values = [card_value(c) for c in my_cards]
    my_suits = [card_suit(c) for c in my_cards]
    public_values = [card_value(c) for c in public_cards]
    public_suits = [card_suit(c) for c in public_cards]
    
    all_values = my_values + public_values
    all_suits = my_suits + public_suits
    
    for s in range(4):
        count = all_suits.count(s)
        if count == 4:
            outs += 9
        elif count == 3:
            outs += 6
        elif count == 2 and len(public_cards) <= 3:
            outs += 3
    
    unique_values = sorted(list(set(all_values)))
    
    open_ended_count = 0
    for i in range(len(unique_values) - 3):
        seq = unique_values[i:i+4]
        if seq[-1] - seq[0] == 3:
            open_ended_count += 1
    
    if open_ended_count > 0:
        outs += 8 * open_ended_count
    else:
        gutshot_count = 0
        for i in range(len(unique_values) - 3):
            seq = unique_values[i:i+4]
            if seq[-1] - seq[0] == 4:
                missing_low = seq[0] - 1
                missing_high = seq[-1] + 1
                if missing_low >= 2 and missing_low not in unique_values:
                    gutshot_count += 1
                if missing_high <= 14 and missing_high not in unique_values:
                    gutshot_count += 1
        outs += 4 * gutshot_count
    
    for v in my_values:
        if all_values.count(v) == 1:
            outs += 1.5
        elif all_values.count(v) == 2:
            outs += 2.5
        elif all_values.count(v) == 3:
            outs += 1
    
    return min(outs, 24)

def get_postflop_strength(my_cards, public_cards):
    all_cards = my_cards + public_cards
    best_score = None
    
    for combo in combinations(all_cards, 5):
        score = evaluate_hand(list(combo))
        if best_score is None or score > best_score:
            best_score = score
    
    rank = best_score[0]
    
    if rank >= 8:
        return 99
    elif rank == 7:
        return 96
    elif rank == 6:
        return 92
    elif rank == 5:
        return 87
    elif rank == 4:
        return 82
    elif rank == 3:
        kicker_strength = best_score[1][0] * 2 + (best_score[1][1] if len(best_score[1]) > 1 else 0)
        return min(90, 68 + kicker_strength // 8)
    elif rank == 2:
        high_pair = best_score[1][0]
        low_pair = best_score[1][1]
        kicker = best_score[1][2] if len(best_score[1]) > 2 else 0
        return min(75, 52 + high_pair + low_pair // 2 + kicker // 4)
    elif rank == 1:
        pair_val = best_score[1][0]
        kicker1 = best_score[1][1] if len(best_score[1]) > 1 else 0
        return min(60, 38 + pair_val * 2 + kicker1 // 2)
    else:
        high = best_score[1][0]
        second = best_score[1][1] if len(best_score[1]) > 1 else 0
        return 12 + high + second // 2
    
    return 50

def analyze_opponent(history, my_id):
    raises = []
    calls = []
    checks = []
    folds = []
    allins = []
    
    for h in history:
        if h['player_id'] == my_id:
            continue
        
        action_type = h['action_type']
        if action_type == 'raise':
            raises.append(h['action'])
        elif action_type == 'call':
            calls.append(h['action'])
        elif action_type == 'check':
            checks.append(1)
        elif action_type == 'fold':
            folds.append(1)
        elif action_type == 'allin':
            allins.append(1)
    
    total_actions = len(raises) + len(calls) + len(checks) + len(folds) + len(allins)
    
    if total_actions == 0:
        return {'aggression': 0.5, 'tightness': 0.5, 'frequency': 0.5}
    
    aggression = (len(raises) + len(allins)) / total_actions
    tightness = len(folds) / total_actions
    frequency = (len(calls) + len(checks)) / total_actions
    
    return {
        'aggression': aggression,
        'tightness': tightness,
        'frequency': frequency
    }

def calculate_pot_odds(amount_to_call, pot_size):
    if amount_to_call <= 0:
        return 1.0
    return amount_to_call / (pot_size + amount_to_call)

def calculate_implied_odds(my_chips, amount_to_call, pot_size, hand_strength):
    base_implied = 1.0
    
    if hand_strength >= 80:
        base_implied = 2.0
    elif hand_strength >= 60:
        base_implied = 1.5
    elif hand_strength >= 40:
        base_implied = 1.2
    
    stack_ratio = my_chips / (pot_size + my_chips)
    return base_implied * (1 + stack_ratio * 0.5)

def gto_bluff_frequency(pot_size, stack_size, hand_strength):
    pot_odds = stack_size / (pot_size + stack_size)
    
    if hand_strength < 30:
        bluff_freq = max(0.05, 0.3 - pot_odds)
    elif hand_strength < 50:
        bluff_freq = max(0.02, 0.15 - pot_odds * 0.5)
    else:
        bluff_freq = 0.0
    
    return bluff_freq

def get_action():
    data = json.loads(sys.stdin.read())
    
    my_id = data['my_id']
    my_chips = data['my_chips']
    my_cards = data['my_cards']
    public_cards = data['public_cards']
    history = data['history']
    dealer_id = data['dealer_id']
    
    round_num = 0
    my_bet_total = 0
    opp_bet_total = 0
    my_bet_this_round = 0
    opp_bet_this_round = 0
    pot_size = 150
    last_raise = 0
    is_opponent_allin = False
    
    sb_id = (dealer_id + 1) % 2
    bb_id = (dealer_id + 2) % 2
    
    for h in history:
        round_num = h['round']
        player = h['player_id']
        action = h['action']
        action_type = h['action_type']
        
        if action_type == 'allin':
            if player != my_id:
                is_opponent_allin = True
        
        if player == my_id:
            if action_type == 'raise':
                my_bet_total += action
                my_bet_this_round += action
                pot_size += action
                last_raise = action
            elif action_type == 'call':
                call_amount = max(0, opp_bet_this_round - my_bet_this_round)
                my_bet_total += call_amount
                my_bet_this_round += call_amount
                pot_size += call_amount
        else:
            if action_type == 'raise':
                opp_bet_total += action
                opp_bet_this_round += action
                pot_size += action
                last_raise = action
            elif action_type == 'call':
                call_amount = max(0, my_bet_this_round - opp_bet_this_round)
                opp_bet_total += call_amount
                opp_bet_this_round += call_amount
                pot_size += call_amount
    
    amount_to_call = max(0, opp_bet_this_round - my_bet_this_round)
    effective_stack = min(my_chips, 40000 - my_bet_total - opp_bet_total)
    
    position_factor = 1.0
    if my_id == dealer_id:
        position_factor = 1.22
    elif my_id == bb_id:
        position_factor = 1.08
    elif my_id == sb_id:
        position_factor = 0.88
    
    opponent_profile = analyze_opponent(history, my_id)
    opponent_aggressive = opponent_profile['aggression'] > 0.35
    opponent_tight = opponent_profile['tightness'] > 0.45
    opponent_passive = opponent_profile['frequency'] > 0.6
    
    if round_num == 0:
        hand_strength = get_preflop_strength(my_cards[0], my_cards[1])
        adjusted_strength = hand_strength * position_factor
        
        if opponent_tight:
            adjusted_strength *= 1.05
        if opponent_aggressive:
            adjusted_strength *= 0.95
        
        if adjusted_strength >= 94:
            if amount_to_call == 0:
                raise_size = max(200, min(my_chips, int(effective_stack * 0.04)))
                return raise_size
            elif amount_to_call <= 100:
                raise_size = max(300, min(my_chips - amount_to_call, int(effective_stack * 0.06)))
                if raise_size > 0:
                    return raise_size
                return amount_to_call if my_chips >= amount_to_call else -2
            elif amount_to_call <= 300:
                if adjusted_strength >= 97:
                    raise_size = min(my_chips - amount_to_call, int(effective_stack * 0.1))
                    if raise_size > 0:
                        return raise_size
                return amount_to_call if my_chips >= amount_to_call else -2
            else:
                if adjusted_strength >= 98:
                    return -2
                return -1
        elif adjusted_strength >= 82:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 100:
                return amount_to_call
            elif amount_to_call <= 400 and adjusted_strength >= 87:
                return amount_to_call
            else:
                return -1
        elif adjusted_strength >= 68:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 50:
                return amount_to_call
            elif amount_to_call <= 100 and position_factor > 1.0:
                return amount_to_call
            else:
                return -1
        elif adjusted_strength >= 52:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 25 and position_factor > 1.05:
                return amount_to_call
            else:
                return -1
        else:
            if amount_to_call == 0:
                return 0
            else:
                return -1
    else:
        outs = calculate_outs(my_cards, public_cards)
        cards_left = 50 - len(public_cards) - 2
        draw_odds = outs / cards_left if cards_left > 0 else 0
        
        made_strength = get_postflop_strength(my_cards, public_cards)
        adjusted_strength = made_strength * 0.7 + draw_odds * 35
        adjusted_strength = min(adjusted_strength, 100)
        
        if opponent_tight and amount_to_call > 0:
            adjusted_strength *= 0.92
        if opponent_aggressive and made_strength >= 75:
            adjusted_strength *= 1.08
        if opponent_passive and made_strength >= 60:
            adjusted_strength *= 1.05
        
        pot_odds = calculate_pot_odds(amount_to_call, pot_size)
        implied_odds = calculate_implied_odds(my_chips, amount_to_call, pot_size, made_strength)
        
        bluff_freq = gto_bluff_frequency(pot_size, effective_stack, adjusted_strength)
        
        if is_opponent_allin:
            required_equity = pot_odds
            if adjusted_strength / 100 >= required_equity:
                return -2 if my_chips > 0 else -1
            return -1
        
        if adjusted_strength >= 90:
            if amount_to_call > 0:
                raise_amount = min(
                    my_chips - amount_to_call,
                    max(100, int(pot_size * 0.8), int(amount_to_call * 2.5))
                )
                if raise_amount > 0:
                    return raise_amount
                return -2
            else:
                return min(my_chips, max(100, int(pot_size * 0.7)))
        elif adjusted_strength >= 80:
            if amount_to_call > 0:
                if amount_to_call <= pot_size * 0.15:
                    return amount_to_call
                elif amount_to_call <= pot_size * 0.35 and made_strength >= 85:
                    return amount_to_call
                else:
                    raise_amount = min(
                        my_chips - amount_to_call,
                        max(80, int(pot_size * 0.5), int(amount_to_call * 2))
                    )
                    if raise_amount > 0:
                        return raise_amount
                    return amount_to_call
            else:
                return min(my_chips, max(80, int(pot_size * 0.5)))
        elif adjusted_strength >= 68:
            if amount_to_call > 0:
                effective_odds = pot_odds * implied_odds
                if effective_odds <= 0.2:
                    return amount_to_call
                elif effective_odds <= 0.35 and made_strength >= 60:
                    return amount_to_call
                else:
                    return -1
            else:
                if made_strength >= 70:
                    return min(my_chips, int(pot_size * 0.25))
                return 0
        elif adjusted_strength >= 50:
            if amount_to_call > 0:
                effective_odds = pot_odds * implied_odds
                if effective_odds <= 0.12 and (made_strength >= 55 or draw_odds > 0.25):
                    return amount_to_call
                else:
                    return -1
            else:
                if draw_odds > 0.3:
                    bluff_amount = min(my_chips, int(pot_size * 0.2))
                    if bluff_amount > 0:
                        return bluff_amount
                return 0
        elif adjusted_strength >= 35:
            if amount_to_call == 0:
                if draw_odds > 0.35 and not opponent_aggressive:
                    bluff_amount = min(my_chips, int(pot_size * 0.15))
                    if bluff_amount > 0:
                        return bluff_amount
                return 0
            else:
                return -1
        else:
            if amount_to_call == 0 and bluff_freq > 0.1 and not opponent_tight:
                bluff_amount = min(my_chips, int(pot_size * 0.1))
                if bluff_amount > 0:
                    return bluff_amount
            return -1

if __name__ == '__main__':
    print(get_action())
