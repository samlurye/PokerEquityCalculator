#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <assert.h>
#include <string.h>

#define DECK_SIZE 52

#define ACE_LOW 1
#define JACK 11
#define QUEEN 12
#define KING 13
#define ACE_HIGH 14

#define SPADES 0
#define CLUBS 1
#define HEARTS 2
#define DIAMONDS 3

#define B2(n) n,     n + 1,     n + 1,     n + 2
#define B4(n) B2(n), B2(n + 1), B2(n + 1), B2(n + 2)
#define B6(n) B4(n), B4(n + 1), B4(n + 1), B4(n + 2)
#define COUNT_SET_BITS B6(0), B6(1), B6(1), B6(2)

static const char bit_lookup[256] = { COUNT_SET_BITS };

typedef struct hand_info {
	int id;
	int fixed[2];
	unsigned long pocket;
	unsigned long cur_hand;
	int straight_flush;
	int quads;
	unsigned long flush;
	int straight;
	int trips;
	int pairs[2];
	int kickers[5];
} hand_info;

int count_set_bits(unsigned long l, int nbytes) {
	int num_bits_set = 0;
	for (unsigned long i = 0; i < nbytes; i++) {
		num_bits_set += bit_lookup[(l >> (8UL * i)) & 0xff];
	}
	return num_bits_set;
}

int card_to_index(char* card) {
	char c_val = card[0];
	int val;
	if (c_val == 'A') {
		val = ACE_LOW;
	} else if (c_val == 'K') {
		val = KING;
	} else if (c_val == 'Q') {
		val = QUEEN;
	} else if (c_val == 'J') {
		val = JACK;
	} else if (c_val == 'T') {
		val = 10;
	} else {
		val = c_val - '0';
	}
	char c_suit = card[1];
	int suit;
	if (c_suit == 'S') {
		suit = SPADES;
	} else if (c_suit == 'C') {
		suit = CLUBS;
	} else if (c_suit == 'H') {
		suit = HEARTS;
	} else if (c_suit == 'D') {
		suit = DIAMONDS;
	}
	return (val - 1) * 4 + suit;
}

int get_num_cards_of_val(hand_info* h, int card_val) {
	if (card_val == 14) {
		card_val = 1;
	}
	return count_set_bits((h->cur_hand >> (4 * (card_val - 1))) & 0x0f, 1);
}

int check_straight(hand_info* h) {
	int count = 0;
	int high_card = 0;
	int num_cards_seen = 0;
	int num_aces = 0;
	int num_cards = 0;
	for (int i = 1; i < 14; i++) {
		num_cards = get_num_cards_of_val(h, i);
		if (i == 1) {
			num_aces = num_cards;
		}
		if (num_cards) {
			count++;
			if (count >= 5) {
				high_card = i;
			}
			num_cards_seen += num_cards;
		} else {
			count = 0;
		}
		if (num_cards_seen == 7) {
			break;
		}
	}
	if (high_card == 13 && num_aces) {
		h->straight = 14;
		return 14;
	} else {
		h->straight = high_card;
		return high_card;
	}
}

int check_straight_flush(hand_info* h) {
	unsigned long temp = h->cur_hand;
	h->cur_hand = h->flush;
	check_straight(h);
	h->cur_hand = temp;
	if (h->straight) {
		h->straight_flush = h->straight;
		return h->straight_flush;
	}
	h->straight_flush = 0;
	return 0;
}

int compare_kickers(hand_info* h1, hand_info* h2, int num_kickers) {
	for (int i = 0; i < num_kickers; i++) {
		if (h1->kickers[i] > h2->kickers[i]) {
			return 1;
		} else if (h2->kickers[i] > h1->kickers[i]) {
			return 2;
		}
	}
	return 0;
}

int compare_straight_flushes(hand_info* h1, hand_info* h2) {
	if (h1->straight_flush > h2->straight_flush) {
		return 1;
	} else if (h2->straight_flush > h1->straight_flush) {
		return 2;
	} else {
		return 0;
	}
}

int compare_quads(hand_info* h1, hand_info* h2) {
	if (h1->quads > h2->quads) {
		return 1;
	} else if (h2->quads > h1->quads) {
		return 2;
	}
	return compare_kickers(h1, h2, 1);
}

int compare_full_houses(hand_info* h1, hand_info* h2) {
	if (h1->trips > h2->trips) {
		return 1;
	} else if (h2->trips > h1->trips) {
		return 2;
	} else if (h1->pairs[0] > h2->pairs[0]) {
		return 1;
	} else if (h2->pairs[0] > h1->pairs[0]) {
		return 2;
	} else {
		return 0;
	}
}

int compare_flushes(hand_info* h1, hand_info* h2) {
	unsigned long h1_ace_high = h1->flush & 0xf;
	unsigned long h2_ace_high = h2->flush & 0xf;
	if (h1_ace_high && !h2_ace_high) {
		return 1;
	} else if (!h1_ace_high && h2_ace_high) {
		return 2;
	} else {
		int ctr = 0;
		for (int i = 13; i > 1; i--) {
			if (ctr == 5) {
				return 0;
			}
			unsigned long temp1 = h1->cur_hand;
			h1->cur_hand = h1->flush;
			unsigned long temp2 = h2->cur_hand;
			h2->cur_hand = h2->flush;
			int h1_has_i = get_num_cards_of_val(h1, i);
			int h2_has_i = get_num_cards_of_val(h2, i);
			h1->cur_hand = temp1;
			h2->cur_hand = temp2;
			if (h1_has_i && !h2_has_i) {
				return 1;
			} else if (!h1_has_i && h2_has_i) {
				return 2;
			} else if (h1_has_i && h2_has_i) {
				ctr++;
			}
		}
		return 0;
	}
}

int compare_straights(hand_info* h1, hand_info* h2) {
	if (h1->straight > h2->straight) {
		return 1;
	} else if (h2->straight > h1->straight) {
		return 2;
	} else {
		return 0;
	}
}

int compare_trips(hand_info* h1, hand_info* h2) {
	if (h1->trips > h2->trips) {
		return 1;
	} else if (h2->trips > h1->trips) {
		return 2;
	}
	return compare_kickers(h1, h2, 2);
}

int compare_two_pair(hand_info* h1, hand_info* h2) {
	if (h1->pairs[0] > h2->pairs[0]) {
		return 1;
	} else if (h2->pairs[0] > h1->pairs[0]) {
		return 2;
	} else if (h1->pairs[1] > h2->pairs[1]) {
		return 1;
	} else if (h2->pairs[1] > h1->pairs[1]) {
		return 2;
	}
	return compare_kickers(h1, h2, 1);
}

int compare_one_pair(hand_info* h1, hand_info* h2) {
	if (h1->pairs[0] > h2->pairs[0]) {
		return 1;
	} else if (h2->pairs[0] > h1->pairs[0]) {
		return 2;
	}
	return compare_kickers(h1, h2, 3);
}

int compare_high_card(hand_info* h1, hand_info* h2) {
	return compare_kickers(h1, h2, 5);
}

unsigned long flushes[] = { 
	0x1111111111111111, 
	0x2222222222222222, 
	0x4444444444444444, 
	0x8888888888888888 
};

unsigned long check_flush(hand_info* h) {
	for (int i = 0; i < 4; i++) {
		unsigned long filtered_hand = h->cur_hand & flushes[i];
		if (count_set_bits(filtered_hand, 8) >= 5) {
			h->flush = filtered_hand;
			return filtered_hand;
		}
	}
	h->flush = 0;
	return 0;
}

void get_n_of_a_kind(hand_info* h) {
	h->quads = 0;
	h->trips = 0;
	memset(h->pairs, 0, sizeof(h->pairs));
	memset(h->kickers, 0, sizeof(h->kickers));
	int card_count = 0;
	for (int i = 2; i < 15; i++) {
		int new_cards = get_num_cards_of_val(h, i);
		card_count += new_cards;
		if (new_cards == 4) {
			h->quads = i;
		} else if (new_cards == 3) {
			if (h->trips) {
				h->pairs[0] = h->trips;
			}
			h->trips = i;
		} else if (new_cards == 2) {
			if (h->pairs[1] > h->kickers[0]) {
				h->kickers[0] = h->pairs[1];
			}
			h->pairs[1] = h->pairs[0];
			h->pairs[0] = i;
		} else if (new_cards == 1) {
			memcpy(&h->kickers[1], h->kickers, 4 * sizeof(int));
			h->kickers[0] = i;
		}
		if (card_count == 7) {
			break;
		}
	}
	if (h->quads && h->trips) {
		h->kickers[0] = h->trips;
	}
	if (h->quads && h->pairs[0]) {
		if (h->pairs[0] > h->kickers[0]) {
			h->kickers[0] = h->pairs[0];
		}
	}
}

void set_hands(hand_info* h1, hand_info* h2, int* h_indices, int* cards) {
	unsigned long board = 0;
	for (int i = 0; i < 5; i++) {
		board |= 1UL << cards[h_indices[i]];
	}
	h1->cur_hand = h1->pocket | board;
	h2->cur_hand = h2->pocket | board;
}

int generate_next_hands(hand_info* h1, hand_info* h2, int* h_indices, int* cards) {
	int i_change = 0;
	for (int i = 0; i < 5; i++) {
		if (i == 4) {
			if (h_indices[4] == (DECK_SIZE - 4) - 1) {
				return 1;
			} else {
				h_indices[4]++;
				i_change = i;
			}
		} else if (h_indices[i] < h_indices[i + 1] - 1) {
			h_indices[i]++;
			i_change = i;
			break;
		}
	}
	for (int i = 0; i < i_change; i++) {
		h_indices[i] = i;
	}
	set_hands(h1, h2, h_indices, cards);
	return 0;
}

int update_counts(int cond1, int cond2, hand_info* h1, hand_info* h2, int* h1_wins, 
			int* h2_wins, int* ties, int (*cmp_fn)(hand_info*, hand_info*)) {
	if (cond1 && !cond2) {
		(*h1_wins)++;
		return 1;
	} else if (!cond1 && cond2) {
		(*h2_wins)++;
		return 1;
	} else if (cond1 && cond2) {
		int winner = cmp_fn(h1, h2);
		if (winner == 1) {
			(*h1_wins)++;
			return 1;
		} else if (winner == 2) {
			(*h2_wins)++;
			return 1;
		} else {
			(*ties)++;
			return 1;
		}
	}
	return 0;
}

int main(int argc, char* argv[]) {
	hand_info h1;
	hand_info h2;
	memset(&h1, 0, sizeof(hand_info));
	memset(&h2, 0, sizeof(hand_info));
	h1.id = 1;
	h1.fixed[0] = card_to_index(argv[1]);
	h1.fixed[1] = card_to_index(argv[2]);
	h1.pocket = 1UL << h1.fixed[0] | 1UL << h1.fixed[1];
	h2.id = 2;
	h2.fixed[0] = card_to_index(argv[3]);
	h2.fixed[1] = card_to_index(argv[4]);
	h2.pocket = 1UL << h2.fixed[0] | 1UL << h2.fixed[1];
	int cards[DECK_SIZE - 4];
	int ctr = 0;
	for (int i = 0; i < DECK_SIZE; i++) {
		if (i != h1.fixed[0] && i != h1.fixed[1] && i != h2.fixed[0] && i != h2.fixed[1]) {
			cards[ctr] = i;
			ctr++;
		}
	}
	int h_indices[] = { 0, 1, 2, 3, 4 };
	set_hands(&h1, &h2, h_indices, cards);
	int iters = 0;
	int finished = 0;
	int h1_wins = 0;
	int h2_wins = 0;
	int ties = 0;
	clock_t start = clock();
	while (!finished) {
		iters++;
		h1.straight_flush = 0;
		h2.straight_flush = 0;
		get_n_of_a_kind(&h1);
		get_n_of_a_kind(&h2);
		check_flush(&h1);
		check_flush(&h2);
		if (h1.flush) {
			check_straight_flush(&h1);
		}
		if (h2.flush) {
			check_straight_flush(&h2);
		}
		check_straight(&h1);
		check_straight(&h2);
		if (update_counts(h1.straight_flush, h2.straight_flush, &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_straight_flushes)) {
		} else if (update_counts(h1.quads, h2.quads, &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_quads)) {
		} else if (update_counts(h1.trips && h1.pairs[0], h2.trips && h2.pairs[0], &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_full_houses)) {
		} else if (update_counts(h1.flush, h2.flush, &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_flushes)) {
		} else if (update_counts(h1.straight, h2.straight, &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_flushes)) {
		} else if (update_counts(h1.trips, h2.trips, &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_trips)) {
		} else if (update_counts(h1.pairs[0] && h1.pairs[1], h2.pairs[0] && h2.pairs[1], &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_two_pair)) {
		} else if (update_counts(h1.pairs[0], h2.pairs[0], &h1, &h2, 
			&h1_wins, &h2_wins, &ties, compare_one_pair)) {
		} else if (update_counts(1, 1, &h1, &h2, &h1_wins, &h2_wins, &ties, compare_high_card)) {
		}
		finished = generate_next_hands(&h1, &h2, h_indices, cards);
	}
	double secs = (float) (clock() - start) / (float) CLOCKS_PER_SEC;
	printf("\nYou win %.2f%% of the time\n", h1_wins * 100. / iters);
	printf("Opponent wins %.2f%% of the time\n", h2_wins * 100. / iters);
	printf("Tie %.2f%% of the time\n\n", ties * 100. / iters);
	printf("%i iterations in %f seconds (%f iterations/sec)\n\n", iters, secs, iters / secs);
}


















