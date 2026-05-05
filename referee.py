#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import subprocess
import sys

N_PLAYERS = 2
SMALL_BLIND = 50
BIG_BLIND = 100
MAX_HAND = 50

def card_value(card):
    return card // 4 + 2

def card_suit(card):
    return card % 4

def evaluate_hand(cards):
    values = sorted([card_value(c) for c in cards], reverse=True)
    suits = [card_suit(c) for c in cards]
    
    flush = len(set(suits)) == 1
    straight = False
    for i in range(len(values)-4):
        if values[i] - values[i+4] == 4:
            straight = True
            straight_high = values[i]
            break
    
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
    
    if sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
        return (6, [sorted_counts[0][0], sorted_counts[1][0]])
    
    if flush:
        return (5, values[:5])
    
    if straight:
        return (4, [straight_high])
    
    if sorted_counts[0][1] == 3:
        kickers = [v for v in values if v != sorted_counts[0][0]][:2]
        return (3, [sorted_counts[0][0]] + kickers)
    
    if sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
        kicker = [v for v in values if v != sorted_counts[0][0] and v != sorted_counts[1][0]][0]
        return (2, [sorted_counts[0][0], sorted_counts[1][0], kicker])
    
    if sorted_counts[0][1] == 2:
        kickers = [v for v in values if v != sorted_counts[0][0]][:3]
        return (1, [sorted_counts[0][0]] + kickers)
    
    return (0, values[:5])

class Referee:
    def __init__(self, bot_paths):
        self.bot_paths = bot_paths
        self.bot_processes = []
        self.total_win_chips = [0, 0]
        self.total_win_games = [0, 0]
    
    def start_bot(self, path):
        try:
            proc = subprocess.Popen([sys.executable, path], 
                                   stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            return proc
        except:
            return None
    
    def stop_bots(self):
        for proc in self.bot_processes:
            if proc and proc.poll() is None:
                proc.kill()
    
    def send_request(self, proc, request):
        if proc is None or proc.poll() is not None:
            return -1
        
        try:
            proc.stdin.write((json.dumps(request) + '\n').encode('utf-8'))
            proc.stdin.flush()
            line = proc.stdout.readline().decode('utf-8').strip()
            return int(line)
        except:
            return -1
    
    def play_hand(self, hand_num):
        deck = list(range(52))
        random.shuffle(deck)
        
        dealer_id = hand_num % N_PLAYERS
        sb_id = (dealer_id + 1) % N_PLAYERS
        bb_id = (dealer_id + 2) % N_PLAYERS
        
        player_cards = [[], []]
        player_cards[0] = [deck.pop(), deck.pop()]
        player_cards[1] = [deck.pop(), deck.pop()]
        
        public_cards = []
        
        player_chips = [20000, 20000]
        player_bets = [0, 0]
        player_active = [True, True]
        player_allin = [False, False]
        
        player_bets[sb_id] = SMALL_BLIND
        player_chips[sb_id] -= SMALL_BLIND
        player_bets[bb_id] = BIG_BLIND
        player_chips[bb_id] -= BIG_BLIND
        
        history = []
        round_num = 0
        current_player = bb_id
        
        while True:
            if round_num == 1 and len(public_cards) == 0:
                public_cards = [deck.pop(), deck.pop(), deck.pop()]
            elif round_num == 2 and len(public_cards) == 3:
                public_cards.append(deck.pop())
            elif round_num == 3 and len(public_cards) == 4:
                public_cards.append(deck.pop())
            
            active_players = [i for i in range(N_PLAYERS) if player_active[i]]
            if len(active_players) == 1:
                winner = active_players[0]
                self.total_win_chips[winner] += sum(player_bets)
                self.total_win_games[winner] += 1
                return
            
            all_allin = all(player_allin[i] for i in active_players)
            if all_allin:
                break
            
            bets_equal = all(player_bets[i] == player_bets[active_players[0]] for i in active_players)
            if bets_equal and len(history) > 0:
                round_num += 1
                if round_num >= 4:
                    break
                current_player = sb_id
                continue
            
            if not player_active[current_player]:
                current_player = (current_player + 1) % N_PLAYERS
                continue
            
            request = {
                "num_players": N_PLAYERS,
                "dealer_id": dealer_id,
                "my_id": current_player,
                "my_chips": player_chips[current_player],
                "my_cards": player_cards[current_player],
                "public_cards": public_cards.copy(),
                "history": history.copy(),
                "hand": hand_num,
                "max_hand": MAX_HAND,
                "total_win_chips": self.total_win_chips.copy(),
                "total_win_games": self.total_win_games.copy()
            }
            
            response = self.send_request(self.bot_processes[current_player], request)
            
            action_type = "fold"
            if response == -1:
                player_active[current_player] = False
                action_type = "fold"
            elif response == -2:
                bet_amount = player_chips[current_player]
                player_bets[current_player] += bet_amount
                player_chips[current_player] = 0
                player_allin[current_player] = True
                action_type = "allin"
            elif response == 0:
                call_amount = max(player_bets) - player_bets[current_player]
                if call_amount > 0:
                    if player_chips[current_player] >= call_amount:
                        player_bets[current_player] += call_amount
                        player_chips[current_player] -= call_amount
                        action_type = "call"
                    else:
                        player_active[current_player] = False
                        action_type = "fold"
                else:
                    action_type = "check"
            elif response > 0:
                raise_amount = response
                min_raise = BIG_BLIND if max(player_bets) == 0 else (max(player_bets) - player_bets[current_player]) * 2
                
                if raise_amount >= min_raise and player_chips[current_player] >= raise_amount:
                    player_bets[current_player] += raise_amount
                    player_chips[current_player] -= raise_amount
                    action_type = "raise"
                else:
                    player_active[current_player] = False
                    action_type = "fold"
            else:
                player_active[current_player] = False
                action_type = "fold"
            
            history.append({
                "round": round_num,
                "player_id": current_player,
                "action": response,
                "action_type": action_type
            })
            
            current_player = (current_player + 1) % N_PLAYERS
        
        active_players = [i for i in range(N_PLAYERS) if player_active[i]]
        if len(active_players) == 1:
            winner = active_players[0]
        else:
            hands = []
            for i in active_players:
                all_cards = player_cards[i] + public_cards
                best_score = None
                best_hand = []
                from itertools import combinations
                for combo in combinations(all_cards, 5):
                    score = evaluate_hand(list(combo))
                    if best_score is None or score > best_score:
                        best_score = score
                        best_hand = list(combo)
                hands.append((i, best_score))
            
            hands.sort(key=lambda x: x[1], reverse=True)
            winner = hands[0][0]
            
        self.total_win_chips[winner] += sum(player_bets)
        self.total_win_games[winner] += 1
    
    def run(self):
        self.bot_processes = [self.start_bot(path) for path in self.bot_paths]
        
        for hand in range(MAX_HAND):
            self.play_hand(hand)
            print(f"Hand {hand+1}/{MAX_HAND}: Chips = {self.total_win_chips}")
        
        self.stop_bots()
        
        print("\n=== Final Result ===")
        print(f"Player 0: {self.total_win_chips[0]} chips, {self.total_win_games[0]} wins")
        print(f"Player 1: {self.total_win_chips[1]} chips, {self.total_win_games[1]} wins")
        
        if self.total_win_chips[0] > self.total_win_chips[1]:
            print("Player 0 wins!")
        elif self.total_win_chips[1] > self.total_win_chips[0]:
            print("Player 1 wins!")
        else:
            print("Draw!")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python referee.py <bot1.py> <bot2.py>")
        sys.exit(1)
    
    referee = Referee([sys.argv[1], sys.argv[2]])
    referee.run()