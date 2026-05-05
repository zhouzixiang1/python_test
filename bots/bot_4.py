#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from itertools import combinations

def card_value(card):
    v = card // 4 + 2
    if v == 14:
        return 14
    return v

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
        return (8, [straight_high] + values[1:5])
    
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
                strength = 95
            elif v1 == 12:
                strength = 90
            elif v1 == 11:
                strength = 85
            elif v1 == 10:
                strength = 78
            elif v1 == 9:
                strength = 70
            elif v1 == 8:
                strength = 62
            elif v1 == 7:
                strength = 55
            elif v1 == 6:
                strength = 48
            elif v1 == 5:
                strength = 42
            elif v1 == 4:
                strength = 36
            elif v1 == 3:
                strength = 30
            elif v1 == 2:
                strength = 25
        elif v1 == 14:
            if v2 == 13:
                strength = 92 if suited else 88
            elif v2 == 12:
                strength = 87 if suited else 82
            elif v2 == 11:
                strength = 82 if suited else 76
            elif v2 == 10:
                strength = 76 if suited else 68
            elif v2 == 9:
                strength = 68 if suited else 58
            elif v2 == 8:
                strength = 58 if suited else 48
            elif v2 == 7:
                strength = 48 if suited else 38
            elif v2 == 6:
                strength = 38 if suited else 28
            elif v2 == 5:
                strength = 28 if suited else 20
            elif v2 == 4:
                strength = 20 if suited else 14
            elif v2 == 3:
                strength = 14 if suited else 10
            elif v2 == 2:
                strength = 10 if suited else 6
        elif v1 == 13:
            if v2 == 12:
                strength = 80 if suited else 74
            elif v2 == 11:
                strength = 74 if suited else 66
            elif v2 == 10:
                strength = 66 if suited else 58
            elif v2 == 9:
                strength = 58 if suited else 48
            elif v2 == 8:
                strength = 48 if suited else 38
            elif v2 == 7:
                strength = 38 if suited else 28
            elif v2 == 6:
                strength = 28 if suited else 20
            elif v2 == 5:
                strength = 20 if suited else 14
            elif v2 == 4:
                strength = 14 if suited else 10
            elif v2 == 3:
                strength = 10 if suited else 7
            elif v2 == 2:
                strength = 7 if suited else 5
        elif v1 == 12:
            if v2 == 11:
                strength = 68 if suited else 60
            elif v2 == 10:
                strength = 60 if suited else 52
            elif v2 == 9:
                strength = 52 if suited else 44
            elif v2 == 8:
                strength = 44 if suited else 36
            elif v2 == 7:
                strength = 36 if suited else 28
            elif v2 == 6:
                strength = 28 if suited else 22
            elif v2 == 5:
                strength = 22 if suited else 16
            elif v2 == 4:
                strength = 16 if suited else 12
            elif v2 == 3:
                strength = 12 if suited else 8
            elif v2 == 2:
                strength = 8 if suited else 5
        elif v1 == 11:
            if v2 == 10:
                strength = 54 if suited else 46
            elif v2 == 9:
                strength = 46 if suited else 38
            elif v2 == 8:
                strength = 38 if suited else 30
            elif v2 == 7:
                strength = 30 if suited else 24
            elif v2 == 6:
                strength = 24 if suited else 18
            elif v2 == 5:
                strength = 18 if suited else 14
            elif v2 == 4:
                strength = 14 if suited else 10
            elif v2 == 3:
                strength = 10 if suited else 7
            elif v2 == 2:
                strength = 7 if suited else 5
        else:
            if suited and gap <= 1:
                strength = 40 + v1
            elif gap <= 1:
                strength = 30 + v1 // 2
            elif suited and gap <= 2:
                strength = 25 + v1 // 2
            else:
                strength = max(5, 15 + (v1 + v2) // 4)
        
        PRE_FLOP_STRENGTH[(c1, c2)] = strength
        PRE_FLOP_STRENGTH[(c2, c1)] = strength

def get_preflop_strength(card1, card2):
    return PRE_FLOP_STRENGTH.get((card1, card2), 50)

def calculate_outs(my_cards, public_cards):
    all_cards = set(my_cards + public_cards)
    deck_size = 52 - len(all_cards)
    if deck_size <= 0:
        return 0
    
    outs = 0
    
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
    
    for i in range(len(unique_values) - 3):
        seq = unique_values[i:i+4]
        if seq[-1] - seq[0] == 3:
            outs += 8
            break
    else:
        for i in range(len(unique_values) - 3):
            seq = unique_values[i:i+4]
            if seq[-1] - seq[0] == 4:
                missing_low = seq[0] - 1
                missing_high = seq[-1] + 1
                if missing_low >= 2 and missing_low not in unique_values:
                    outs += 4
                if missing_high <= 14 and missing_high not in unique_values:
                    outs += 4
    
    for v in my_values:
        if all_values.count(v) == 1:
            outs += 1.5
        elif all_values.count(v) == 2:
            outs += 2
        elif all_values.count(v) == 3:
            outs += 1
    
    return min(outs, 24)

def get_postflop_strength(my_cards, public_cards):
    all_cards = my_cards + public_cards
    best_score = None
    best_combo = []
    
    for combo in combinations(all_cards, 5):
        combo_list = list(combo)
        score = evaluate_hand(combo_list)
        if best_score is None or score > best_score:
            best_score = score
            best_combo = combo_list
    
    rank = best_score[0]
    
    if rank >= 8:
        return 99
    elif rank == 7:
        return 95
    elif rank == 6:
        return 90
    elif rank == 5:
        return 85
    elif rank == 4:
        return 80
    elif rank == 3:
        kicker_strength = best_score[1][0] * 2 + (best_score[1][1] if len(best_score[1]) > 1 else 0)
        return 65 + kicker_strength // 10
    elif rank == 2:
        high_pair = best_score[1][0]
        low_pair = best_score[1][1]
        kicker = best_score[1][2] if len(best_score[1]) > 2 else 0
        return 50 + high_pair + low_pair // 2 + kicker // 5
    elif rank == 1:
        pair_val = best_score[1][0]
        kicker1 = best_score[1][1] if len(best_score[1]) > 1 else 0
        return 35 + pair_val * 2 + kicker1 // 3
    else:
        high = best_score[1][0]
        second = best_score[1][1] if len(best_score[1]) > 1 else 0
        return 10 + high + second // 2
    
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
        return {'aggression': 0.5, 'tightness': 0.5}
    
    aggression = (len(raises) + len(allins)) / total_actions if total_actions > 0 else 0.5
    tightness = len(folds) / total_actions if total_actions > 0 else 0.5
    
    return {'aggression': aggression, 'tightness': tightness}

def get_action():
    data = json.loads(sys.stdin.read())
    
    my_id = data['my_id']
    my_chips = data['my_chips']
    my_cards = data['my_cards']
    public_cards = data['public_cards']
    history = data['history']
    dealer_id = data['dealer_id']
    total_chips = 20000 * 2
    
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
                call_amount = opp_bet_this_round - my_bet_this_round
                my_bet_total += call_amount
                my_bet_this_round += call_amount
                pot_size += call_amount
            elif action_type == 'check':
                pass
        else:
            if action_type == 'raise':
                opp_bet_total += action
                opp_bet_this_round += action
                pot_size += action
                last_raise = action
            elif action_type == 'call':
                call_amount = my_bet_this_round - opp_bet_this_round
                opp_bet_total += call_amount
                opp_bet_this_round += call_amount
                pot_size += call_amount
            elif action_type == 'check':
                pass
    
    amount_to_call = max(0, opp_bet_this_round - my_bet_this_round)
    effective_stack = min(my_chips, total_chips - my_bet_total - opp_bet_total)
    
    position_factor = 1.0
    if my_id == dealer_id:
        position_factor = 1.18
    elif my_id == bb_id:
        position_factor = 1.05
    elif my_id == sb_id:
        position_factor = 0.92
    
    if round_num == 0:
        hand_strength = get_preflop_strength(my_cards[0], my_cards[1])
        adjusted_strength = hand_strength * position_factor
        
        if adjusted_strength >= 92:
            if amount_to_call == 0:
                return min(my_chips, max(200, int(effective_stack * 0.03)))
            elif amount_to_call <= 100:
                raise_amount = min(my_chips - amount_to_call, max(300, int(effective_stack * 0.05)))
                if raise_amount > 0:
                    return raise_amount
                return amount_to_call
            elif amount_to_call <= 200:
                return amount_to_call if my_chips >= amount_to_call else -2
            else:
                if adjusted_strength >= 98:
                    return -2
                return -1
        elif adjusted_strength >= 78:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 100:
                return amount_to_call
            elif amount_to_call <= 300 and adjusted_strength >= 85:
                return amount_to_call
            else:
                return -1
        elif adjusted_strength >= 65:
            if amount_to_call == 0:
                return 0
            elif amount_to_call <= 50:
                return amount_to_call
            else:
                return -1
        elif adjusted_strength >= 50:
            if amount_to_call == 0:
                return 0
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
        
        opponent_profile = analyze_opponent(history, my_id)
        opponent_tight = opponent_profile['tightness'] > 0.4
        opponent_aggressive = opponent_profile['aggression'] > 0.3
        
        if opponent_tight and amount_to_call > 0:
            adjusted_strength *= 0.95
        
        if opponent_aggressive and made_strength >= 70:
            adjusted_strength *= 1.05
        
        pot_odds = amount_to_call / (pot_size + amount_to_call) if amount_to_call > 0 else 0
        implied_odds_multiplier = 1.5 if made_strength >= 70 else 1.2
        
        if is_opponent_allin:
            if adjusted_strength >= 50:
                return -2 if my_chips > 0 else -1
            return -1
        
        if adjusted_strength >= 88:
            if amount_to_call > 0:
                raise_amount = min(my_chips - amount_to_call, max(100, int(pot_size * 0.7), amount_to_call * 2))
                if raise_amount > 0:
                    return raise_amount
                return -2
            else:
                return min(my_chips, max(100, int(pot_size * 0.6)))
        elif adjusted_strength >= 78:
            if amount_to_call > 0:
                if amount_to_call <= pot_size * 0.2:
                    return amount_to_call
                elif amount_to_call <= pot_size * 0.4 and made_strength >= 85:
                    return amount_to_call
                else:
                    raise_amount = min(my_chips - amount_to_call, max(100, int(pot_size * 0.4), amount_to_call * 2))
                    if raise_amount > 0:
                        return raise_amount
                    return amount_to_call
            else:
                return min(my_chips, max(80, int(pot_size * 0.4)))
        elif adjusted_strength >= 65:
            if amount_to_call > 0:
                if amount_to_call <= pot_size * 0.15:
                    return amount_to_call
                else:
                    return -1
            else:
                return 0
        elif adjusted_strength >= 50:
            if amount_to_call > 0:
                if amount_to_call <= pot_size * 0.08 * implied_odds_multiplier:
                    return amount_to_call
                else:
                    return -1
            else:
                return 0
        else:
            return -1

if __name__ == '__main__':
    print(get_action())
