#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

def card_value(card):
    return card // 4 + 2

def card_suit(card):
    return card % 4

def get_hand_strength(my_cards):
    val1 = card_value(my_cards[0])
    val2 = card_value(my_cards[1])
    suit1 = card_suit(my_cards[0])
    suit2 = card_suit(my_cards[1])
    
    if val1 > val2:
        val1, val2 = val2, val1
    
    pair = (val1 == val2)
    suited = (suit1 == suit2)
    connected = (val2 - val1 <= 2)
    
    if val1 >= 14:
        if pair:
            return 10
        if suited:
            return 9
        return 8
    elif val1 >= 13:
        if pair:
            return 9
        if suited:
            return 8
        return 7
    elif val1 >= 12:
        if pair:
            return 8
        if suited and connected:
            return 7
        if suited:
            return 6
        return 5
    elif val1 >= 11:
        if pair:
            return 7
        if suited and connected:
            return 6
        if suited:
            return 5
        return 4
    elif val1 >= 10:
        if pair:
            return 6
        if suited and connected:
            return 5
        return 3
    elif val1 >= 9:
        if pair:
            return 5
        if suited and connected:
            return 4
        return 2
    else:
        if pair:
            return 4
        return 1

def get_action():
    data = json.loads(sys.stdin.read())
    
    my_id = data['my_id']
    my_chips = data['my_chips']
    my_cards = data['my_cards']
    history = data['history']
    
    round_num = 0
    round_bet = 0
    my_bet_in_round = 0
    opponent_bet_in_round = 0
    
    for h in history:
        round_num = h['round']
        if h['action_type'] == 'raise':
            round_bet = h['action']
        elif h['action_type'] == 'call':
            if round_bet == 0:
                round_bet = 100
        if h['player_id'] == my_id:
            if h['action'] > 0:
                my_bet_in_round += h['action']
            elif h['action_type'] == 'call':
                my_bet_in_round += round_bet if round_bet > 0 else 100
        else:
            if h['action'] > 0:
                opponent_bet_in_round += h['action']
            elif h['action_type'] == 'call':
                opponent_bet_in_round += round_bet if round_bet > 0 else 100
    
    hand_strength = get_hand_strength(my_cards)
    
    total_bet_needed = opponent_bet_in_round - my_bet_in_round
    
    if total_bet_needed > my_chips:
        if hand_strength >= 7:
            return -2
        else:
            return -1
    
    if round_num == 0:
        if hand_strength >= 8:
            if opponent_bet_in_round == 0:
                return 200
            elif total_bet_needed <= 100:
                return 0
            else:
                return -2
        elif hand_strength >= 6:
            if total_bet_needed <= 100:
                return 0
            elif total_bet_needed <= 200:
                return 0
            else:
                return -1
        elif hand_strength >= 4:
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
        community_cards = data['public_cards']
        all_cards = my_cards + community_cards
        
        has_pair = False
        has_three = False
        has_straight = False
        has_flush = False
        
        values = sorted([card_value(c) for c in all_cards])
        suits = [card_suit(c) for c in all_cards]
        
        for i in range(len(values)-1):
            if values[i] == values[i+1]:
                count = 1
                j = i
                while j < len(values) and values[j] == values[i]:
                    count += 1
                    j += 1
                if count >= 3:
                    has_three = True
                else:
                    has_pair = True
        
        for i in range(len(values)-4):
            if values[i+4] - values[i] == 4:
                has_straight = True
                break
        
        for s in range(4):
            if suits.count(s) >= 5:
                has_flush = True
                break
        
        board_strength = 0
        if has_three or (has_pair and len(community_cards) >= 3):
            board_strength = 7
        elif has_pair:
            board_strength = 5
        elif has_straight or has_flush:
            board_strength = 6
        else:
            board_strength = 3
        
        combined_strength = min(10, hand_strength + board_strength // 2)
        
        if combined_strength >= 8:
            if opponent_bet_in_round > 0 and total_bet_needed > 0:
                return min(my_chips, total_bet_needed * 2) if my_chips > total_bet_needed else -2
            elif opponent_bet_in_round == 0:
                return min(my_chips, 200)
            else:
                return 0
        elif combined_strength >= 6:
            if total_bet_needed <= my_chips // 10:
                return 0
            else:
                return -1
        elif combined_strength >= 4:
            if total_bet_needed == 0:
                return 0
            else:
                return -1
        else:
            return -1

if __name__ == '__main__':
    print(get_action())