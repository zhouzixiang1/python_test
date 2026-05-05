#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import random

def get_action():
    data = json.loads(sys.stdin.read())
    
    my_chips = data['my_chips']
    my_cards = data['my_cards']
    public_cards = data['public_cards']
    history = data['history']
    
    round_bet = 0
    for h in history:
        if h['action_type'] == 'raise':
            round_bet = h['action']
        elif h['action_type'] == 'call' and h['player_id'] != data['my_id']:
            if round_bet == 0:
                round_bet = 100
    
    actions = []
    
    if my_chips > round_bet:
        actions.append(0)
    
    if my_chips > 0:
        actions.append(-2)
    
    if my_chips > round_bet * 2 and round_bet > 0:
        max_raise = min(my_chips - round_bet, round_bet * 2)
        if max_raise > 0:
            actions.append(max_raise)
    
    actions.append(-1)
    
    return random.choice(actions)

if __name__ == '__main__':
    print(get_action())