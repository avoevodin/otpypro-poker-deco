# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - десятка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокера.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------
import itertools

from more_itertools import all_equal, sliding_window


def get_ranks():
    """
    Возвращает список всех рангов.
    :return:
    """
    int_rank_aliases = {10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"}
    return [str(i) if i < 10 else int_rank_aliases[i] for i in range(14, 1, -1)]


def get_joker_vars(hand, suits):
    """
    Возвращает список из карт, которыми можно заменить конкретного джокера.
    На входе получает текущую руку, эти карты отфильтровываются из результата.
    Так же на вход получает тупл из достпных для джокера мастей.
    :param hand:
    :param suits:
    :return:
    """
    j_vars = ["".join(comb) for comb in itertools.product(get_ranks(), suits)]
    return itertools.filterfalse(lambda x: x in hand, j_vars)


def get_red_joker_vars(hand):
    """
    Получает карты, способные заменить красного джокера в конкретной руке.
    На вход получает руку, карты из которой будут исключены из
    возвращаемого набора.
    :param hand:
    :return:
    """
    return get_joker_vars(hand, ("H", "D"))


def get_black_joker_vars(hand):
    """
    Получает карты, способные заменить черного джокера в конкретной руке.
    На вход получает руку, карты из которой будут исключены из
    возвращаемого набора.
    :param hand:
    :return:
    """
    return get_joker_vars(hand, ("S", "C"))


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, *kind_seq(4, 1, ranks))
    elif kind_seq(3, 2, ranks):
        return (6, *kind_seq(3, 2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, *two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    int_rank_aliases = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    int_ranks = [int_rank_aliases.get(card[:-1]) or int(card[:-1]) for card in hand]
    return sorted(int_ranks, reverse=True)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits = [card[1:] for card in hand]
    return all_equal(suits)


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return ranks == [i for i in range(ranks[0], ranks[0] - 5, -1)]


def kind_seq(n, m, ranks):
    """
    Возвращает ранги двух различных последовательностей карт одинаковых рангов
    длин n и m. Сначала ищется последовательность большей длины одного, затем меньшей
    длины для другого ранга. Первым возвращается ранг более длинной последовательности.
    :param n:
    :param m:
    :param ranks:
    :return:
    """
    first_kind_len = max(n, m)
    second_kind_len = min(n, m)
    first_kind_rank = kind(first_kind_len, ranks)
    if first_kind_rank:
        second_kind_rank = kind(second_kind_len, ranks, first_kind_rank)
        if second_kind_rank:
            return first_kind_rank, second_kind_rank
    return None


def kind(n, ranks, exclude_rank=None):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    for seq in sliding_window(ranks, n):
        kind_rank = seq[0]
        if kind_rank != exclude_rank and all_equal(seq):
            return kind_rank
    return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    if kind_seq(2, 2, ranks):
        return kind_seq(2, 2, ranks)
    return None


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт"""
    hands_it = itertools.combinations(hand, 5)
    ranks_list = []
    for hand_5 in hands_it:
        ranks_list.append((hand_rank(hand_5), hand_5))
    return list(sorted(ranks_list, reverse=False).pop()[1])


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    hands_it = itertools.combinations(hand, 5)
    ranks_list = []
    black_j = "?B"
    red_j = "?R"
    for hand_5 in hands_it:
        hand_5 = list(hand_5)
        is_black_j = black_j in hand_5
        is_red_j = red_j in hand_5
        hand_5_str = None

        if is_black_j or is_red_j:
            hand_5 = list(
                itertools.filterfalse(lambda x: x == black_j or x == red_j, hand_5)
            )
            hand_5_str = " ".join(hand_5)

        joker_hands = None
        if is_red_j and is_black_j:
            joker_hands = itertools.product(
                [hand_5_str], get_black_joker_vars(hand_5), get_red_joker_vars(hand_5)
            )
        elif is_red_j:
            red_vars = get_red_joker_vars(hand_5)
            joker_hands = itertools.product([hand_5_str], red_vars)
        elif is_black_j:
            joker_hands = itertools.product([hand_5_str], get_black_joker_vars(hand_5))

        if joker_hands:
            for j_hand in joker_hands:
                j_hand = list(j_hand)
                j_hand = list(itertools.chain(j_hand[0].split(), j_hand[1:]))
                ranks_list.append((hand_rank(j_hand), j_hand))
        else:
            ranks_list.append((hand_rank(hand_5), hand_5))

    return list(sorted(ranks_list, reverse=False).pop()[1])


def test_best_hand():
    print("test_best_hand...")
    assert sorted(best_hand("6C 7C 8C 9C TC 5C JS".split())) == [
        "6C",
        "7C",
        "8C",
        "9C",
        "TC",
    ]
    assert sorted(best_hand("TD TC TH 7C 7D 8C 8S".split())) == [
        "8C",
        "8S",
        "TC",
        "TD",
        "TH",
    ]
    assert sorted(best_hand("JD TC TH 7C 7D 7S 7H".split())) == [
        "7C",
        "7D",
        "7H",
        "7S",
        "JD",
    ]
    print("OK")


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split())) == [
        "7C",
        "8C",
        "9C",
        "JC",
        "TC",
    ]
    assert sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split())) == [
        "7C",
        "TC",
        "TD",
        "TH",
        "TS",
    ]
    assert sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split())) == [
        "7C",
        "7D",
        "7H",
        "7S",
        "JD",
    ]
    print("OK")


if __name__ == "__main__":
    test_best_hand()
    test_best_wild_hand()
