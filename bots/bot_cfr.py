#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import random
from itertools import combinations
from collections import defaultdict

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
            return (9, 100)
        return (8, 95 + straight_high / 10)
    
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    
    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 4:
        kicker = [v for v in values if v != sorted_counts[0][0]][0]
        return (7, 90 + sorted_counts[0][0] / 2 + kicker / 10)
    
    if len(sorted_counts) >= 2 and sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
        return (6, 85 + sorted_counts[0][0] / 2 + sorted_counts[1][0] / 5)
    
    if flush:
        high_val = values[0]
        return (5, 75 + high_val / 2)
    
    if straight:
        return (4, 70 + straight_high / 2)
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 3:
        kickers = [v for v in values if v != sorted_counts[0][0]][:2]
        kicker_sum = sum(kickers)
        return (3, 60 + sorted_counts[0][0] + kicker_sum / 5)
    
    if len(sorted_counts) >= 2 and sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
        kicker = [v for v in values if v != sorted_counts[0][0] and v != sorted_counts[1][0]][0]
        return (2, 45 + sorted_counts[0][0] + sorted_counts[1][0] / 2 + kicker / 5)
    
    if len(sorted_counts) >= 1 and sorted_counts[0][1] == 2:
        kickers = [v for v in values if v != sorted_counts[0][0]][:3]
        kicker_sum = sum(kickers)
        return (1, 30 + sorted_counts[0][0] * 1.5 + kicker_sum / 10)
    
    high = values[0]
    second = values[1] if len(values) > 1 else 0
    third = values[2] if len(values) > 2 else 0
    return (0, 5 + high + second / 3 + third / 5)

PRE_FLOP_MATRIX = {}
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
                strength = 99
            elif v1 == 13:
                strength = 94
            elif v1 == 12:
                strength = 89
            elif v1 == 11:
                strength = 84
            elif v1 == 10:
                strength = 78
            elif v1 == 9:
                strength = 72
            elif v1 == 8:
                strength = 65
            elif v1 == 7:
                strength = 58
            elif v1 == 6:
                strength = 51
            elif v1 == 5:
                strength = 44
            elif v1 == 4:
                strength = 37
            elif v1 == 3:
                strength = 30
            elif v1 == 2:
                strength = 24
        elif v1 == 14:
            if v2 == 13:
                strength = 91 if suited else 87
            elif v2 == 12:
                strength = 86 if suited else 81
            elif v2 == 11:
                strength = 81 if suited else 75
            elif v2 == 10:
                strength = 75 if suited else 67
            elif v2 == 9:
                strength = 68 if suited else 58
            elif v2 == 8:
                strength = 60 if suited else 50
            elif v2 == 7:
                strength = 51 if suited else 41
            elif v2 == 6:
                strength = 42 if suited else 32
            elif v2 <= 5:
                strength = 33 if suited else 23
        elif v1 == 13:
            if v2 == 12:
                strength = 80 if suited else 74
            elif v2 == 11:
                strength = 74 if suited else 66
            elif v2 == 10:
                strength = 67 if suited else 59
            elif v2 == 9:
                strength = 59 if suited else 50
            elif v2 == 8:
                strength = 50 if suited else 41
            elif v2 == 7:
                strength = 41 if suited else 32
            elif v2 <= 6:
                strength = 32 if suited else 23
        elif v1 == 12:
            if v2 == 11:
                strength = 69 if suited else 61
            elif v2 == 10:
                strength = 62 if suited else 54
            elif v2 == 9:
                strength = 54 if suited else 46
            elif v2 == 8:
                strength = 46 if suited else 38
            elif v2 == 7:
                strength = 38 if suited else 30
            elif v2 <= 6:
                strength = 30 if suited else 22
        elif v1 == 11:
            if v2 == 10:
                strength = 56 if suited else 48
            elif v2 == 9:
                strength = 49 if suited else 41
            elif v2 == 8:
                strength = 41 if suited else 33
            elif v2 == 7:
                strength = 33 if suited else 26
            elif v2 <= 6:
                strength = 26 if suited else 19
        elif v1 == 10:
            if v2 == 9:
                strength = 45 if suited else 37
            elif v2 == 8:
                strength = 38 if suited else 30
            elif v2 == 7:
                strength = 31 if suited else 24
            elif v2 <= 6:
                strength = 24 if suited else 18
        elif v1 <= 9:
            if suited and gap <= 1:
                strength = 32 + v1
            elif gap <= 1:
                strength = 25 + v1 // 2
            elif suited and gap <= 2:
                strength = 20 + v1 // 2
            else:
                strength = max(6, 15 + (v1 + v2) // 4)
        
        PRE_FLOP_MATRIX[(c1, c2)] = strength
        PRE_FLOP_MATRIX[(c2, c1)] = strength

def get_preflop_strength(card1, card2):
    return PRE_FLOP_MATRIX.get((card1, card2), 50)

def calculate_outs(my_cards, public_cards):
    outs = 0
    all_cards = set(my_cards + public_cards)
    
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
    best_rank = -1
    best_score = 0
    
    for combo in combinations(all_cards, 5):
        rank, score = evaluate_hand(list(combo))
        if rank > best_rank or (rank == best_rank and score > best_score):
            best_rank = rank
            best_score = score
    
    return best_score

def analyze_opponent(history, my_id):
    stats = {
        'vpip': 0.0,
        'pfr': 0.0,
        'af': 0.0,
        'aggression': 0.5,
        'tightness': 0.5,
        'is_nit': False,
        'is_loose': False,
        'is_aggressive': False,
        'is_passive': False,
        '3bet_freq': 0.0,
        'cbet_freq': 0.0,
        'fold_to_cbet': 0.0
    }
    
    preflop_hands = 0
    vpip_count = 0
    pfr_count = 0
    total_raises = 0
    total_calls = 0
    total_folds = 0
    three_bet_count = 0
    cbet_count = 0
    cbet_fold_count = 0
    
    for h in history:
        if h['player_id'] == my_id:
            continue
        
        action_type = h['action_type']
        round_num = h['round']
        
        if round_num == 0:
            preflop_hands += 1
            if action_type in ['call', 'raise', 'allin']:
                vpip_count += 1
            if action_type in ['raise', 'allin']:
                pfr_count += 1
        
        if action_type == 'raise':
            total_raises += 1
        elif action_type == 'call':
            total_calls += 1
        elif action_type == 'fold':
            total_folds += 1
    
    if preflop_hands > 0:
        stats['vpip'] = vpip_count / preflop_hands
        stats['pfr'] = pfr_count / preflop_hands
    
    total_actions = total_raises + total_calls
    if total_actions > 0:
        stats['af'] = total_raises / max(total_calls, 1)
    
    if total_raises + total_folds > 0:
        stats['aggression'] = total_raises / (total_raises + total_folds)
    
    if total_actions + total_folds > 0:
        stats['tightness'] = total_folds / (total_actions + total_folds)
    
    stats['is_nit'] = stats['tightness'] > 0.55
    stats['is_loose'] = stats['tightness'] < 0.25
    stats['is_aggressive'] = stats['aggression'] > 0.4
    stats['is_passive'] = stats['aggression'] < 0.15
    
    return stats

def monte_carlo_simulation(my_cards, public_cards, iterations=500):
    if len(public_cards) >= 5:
        return 1.0 if get_postflop_strength(my_cards, public_cards) > 50 else 0.0
    
    remaining_cards = [c for c in range(52) if c not in my_cards + public_cards]
    wins = 0
    ties = 0
    
    for _ in range(iterations):
        shuffled = random.sample(remaining_cards, 5 - len(public_cards))
        full_public = public_cards + shuffled
        
        opp_remaining = [c for c in remaining_cards if c not in shuffled]
        opp_cards = random.sample(opp_remaining, 2)
        
        my_strength = get_postflop_strength(my_cards, full_public)
        opp_strength = get_postflop_strength(opp_cards, full_public)
        
        if my_strength > opp_strength:
            wins += 1
        elif my_strength == opp_strength:
            ties += 0.5
    
    return (wins + ties) / iterations

def calculate_pot_odds(amount_to_call, pot_size):
    if amount_to_call <= 0:
        return 1.0
    return amount_to_call / (pot_size + amount_to_call)

def calculate_implied_odds(my_chips, amount_to_call, pot_size, hand_strength):
    base_implied = 1.0
    
    if hand_strength >= 85:
        base_implied = 2.5
    elif hand_strength >= 70:
        base_implied = 1.8
    elif hand_strength >= 55:
        base_implied = 1.4
    elif hand_strength >= 40:
        base_implied = 1.2
    
    stack_ratio = my_chips / (pot_size + my_chips)
    return base_implied * (1 + stack_ratio * 0.7)

def cfr_bet_size(pot_size, hand_strength, opponent_profile, position_factor):
    if hand_strength >= 90:
        base_size = pot_size * 0.9
    elif hand_strength >= 80:
        base_size = pot_size * 0.65
    elif hand_strength >= 70:
        base_size = pot_size * 0.45
    elif hand_strength >= 60:
        base_size = pot_size * 0.3
    else:
        base_size = pot_size * 0.15
    
    if opponent_profile['is_nit']:
        base_size *= 1.2
    if opponent_profile['is_loose']:
        base_size *= 0.8
    if opponent_profile['is_passive']:
        base_size *= 1.1
    
    if position_factor > 1.1:
        base_size *= 1.1
    elif position_factor < 0.9:
        base_size *= 0.9
    
    return base_size

def gto_bluff_calculator(pot_size, stack_size, hand_strength, opponent_profile):
    pot_odds = stack_size / (pot_size + stack_size)
    
    if hand_strength < 20:
        bluff_freq = max(0.1, 0.4 - pot_odds)
    elif hand_strength < 35:
        bluff_freq = max(0.05, 0.2 - pot_odds * 0.5)
    else:
        bluff_freq = 0.0
    
    if opponent_profile['is_nit']:
        bluff_freq *= 1.6
    if opponent_profile['is_loose']:
        bluff_freq *= 0.5
    if opponent_profile['is_passive']:
        bluff_freq *= 1.4
    
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
    has_raised = False
    opp_raised_this_round = False
    
    sb_id = (dealer_id + 1) % 2
    bb_id = (dealer_id + 2) % 2
    
    for h in history:
        round_num = h['round']
        player = h['player_id']
        action = h['action']
        action_type = h['action_type']
        
        if action_type == 'allin' and player != my_id:
            is_opponent_allin = True
        
        if player == my_id:
            if action_type == 'raise':
                my_bet_total += action
                my_bet_this_round += action
                pot_size += action
                last_raise = action
                has_raised = True
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
                opp_raised_this_round = True
            elif action_type == 'call':
                call_amount = max(0, my_bet_this_round - opp_bet_this_round)
                opp_bet_total += call_amount
                opp_bet_this_round += call_amount
                pot_size += call_amount
    
    amount_to_call = max(0, opp_bet_this_round - my_bet_this_round)
    effective_stack = min(my_chips, 40000 - my_bet_total - opp_bet_total)
    stack_to_pot_ratio = effective_stack / pot_size if pot_size > 0 else 0
    
    position_factor = 1.0
    if my_id == dealer_id:
        position_factor = 1.28
    elif my_id == bb_id:
        position_factor = 1.05
    elif my_id == sb_id:
        position_factor = 0.82
    
    opponent_profile = analyze_opponent(history, my_id)
    
    if round_num == 0:
        hand_strength = get_preflop_strength(my_cards[0], my_cards[1])
        adjusted_strength = hand_strength * position_factor
        
        if opponent_profile['is_nit']:
            adjusted_strength *= 1.12
        if opponent_profile['is_aggressive']:
            adjusted_strength *= 0.88
        
        if adjusted_strength >= 96:
            if amount_to_call == 0:
                raise_amount = max(250, int(effective_stack * 0.06))
                return min(raise_amount, my_chips)
            elif amount_to_call <= 100:
                raise_amount = max(400, int(effective_stack * 0.1))
                if my_chips > amount_to_call:
                    return min(raise_amount, my_chips - amount_to_call)
                return amount_to_call if my_chips >= amount_to_call else -2
            elif amount_to_call <= 400:
                if adjusted_strength >= 99:
                    return -2 if my_chips > 0 else -1
                return amount_to_call if my_chips >= amount_to_call else -2
            else:
                if adjusted_strength >= 98:
                    return -2 if my_chips > 0 else -1
                return -1
        
        elif adjusted_strength >= 85:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 100:
                return amount_to_call
            elif amount_to_call <= 500 and adjusted_strength >= 90:
                return amount_to_call
            else:
                return -1
        
        elif adjusted_strength >= 72:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 50:
                return amount_to_call
            elif amount_to_call <= 150 and position_factor > 1.05:
                return amount_to_call
            else:
                return -1
        
        elif adjusted_strength >= 58:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 30 and position_factor > 1.1:
                return amount_to_call
            else:
                return -1
        
        else:
            if amount_to_call == 0 and position_factor > 1.15 and hand_strength >= 48:
                return 0
            return -1 if amount_to_call > 0 else 0
    
    else:
        outs = calculate_outs(my_cards, public_cards)
        cards_left = 50 - len(public_cards) - 2
        draw_odds = outs / cards_left if cards_left > 0 else 0
        
        made_strength = get_postflop_strength(my_cards, public_cards)
        
        mc_win_rate = monte_carlo_simulation(my_cards, public_cards, 300)
        adjusted_strength = made_strength * 0.6 + mc_win_rate * 40
        
        if opponent_profile['is_nit'] and amount_to_call > 0:
            adjusted_strength *= 0.85
        if opponent_profile['is_aggressive'] and made_strength >= 78:
            adjusted_strength *= 1.15
        if opponent_profile['is_passive'] and made_strength >= 62:
            adjusted_strength *= 1.1
        
        pot_odds = calculate_pot_odds(amount_to_call, pot_size)
        implied_odds = calculate_implied_odds(my_chips, amount_to_call, pot_size, made_strength)
        effective_odds = pot_odds * implied_odds
        
        bluff_freq = gto_bluff_calculator(pot_size, effective_stack, adjusted_strength, opponent_profile)
        
        if is_opponent_allin:
            required_equity = pot_odds
            if adjusted_strength / 100 >= required_equity:
                return -2 if my_chips > 0 else -1
            return -1
        
        if adjusted_strength >= 93:
            if amount_to_call > 0:
                raise_amount = min(
                    my_chips - amount_to_call,
                    max(120, int(pot_size * 0.9), int(amount_to_call * 3))
                )
                if raise_amount > 0:
                    return raise_amount
                return -2
            else:
                return min(my_chips, max(150, int(pot_size * 0.8)))
        
        elif adjusted_strength >= 83:
            if amount_to_call > 0:
                if amount_to_call <= pot_size * 0.1:
                    return amount_to_call
                elif amount_to_call <= pot_size * 0.25 and made_strength >= 90:
                    return amount_to_call
                else:
                    raise_amount = min(
                        my_chips - amount_to_call,
                        max(100, int(pot_size * 0.6), int(amount_to_call * 2.2))
                    )
                    if raise_amount > 0:
                        return raise_amount
                    return amount_to_call
            else:
                bet_size = cfr_bet_size(pot_size, adjusted_strength, opponent_profile, position_factor)
                return min(my_chips, int(bet_size))
        
        elif adjusted_strength >= 72:
            if amount_to_call > 0:
                if effective_odds <= 0.15:
                    return amount_to_call
                elif effective_odds <= 0.25 and made_strength >= 68:
                    return amount_to_call
                else:
                    return -1
            else:
                if made_strength >= 78:
                    return min(my_chips, int(pot_size * 0.35))
                return 0
        
        elif adjusted_strength >= 55:
            if amount_to_call > 0:
                if effective_odds <= 0.08 and (made_strength >= 60 or draw_odds > 0.3):
                    return amount_to_call
                else:
                    return -1
            else:
                if draw_odds > 0.35 and not opponent_profile['is_aggressive']:
                    bluff_amount = min(my_chips, int(pot_size * 0.28))
                    if bluff_amount > 0:
                        return bluff_amount
                return 0
        
        elif adjusted_strength >= 40:
            if amount_to_call == 0:
                if draw_odds > 0.4 and not opponent_profile['is_aggressive']:
                    bluff_amount = min(my_chips, int(pot_size * 0.2))
                    if bluff_amount > 0:
                        return bluff_amount
                return 0
            else:
                return -1
        
        else:
            if amount_to_call == 0 and bluff_freq > 0.15 and not opponent_profile['is_nit']:
                bluff_amount = min(my_chips, int(pot_size * 0.15))
                if bluff_amount > 0:
                    return bluff_amount
            return -1

if __name__ == '__main__':
    print(get_action())
