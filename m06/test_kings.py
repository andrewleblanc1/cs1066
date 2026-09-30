import pytest

from cards import JOKER, shuffle
from kings import Hand, count_points, drop_3, select_card


def test_deck_contains_one_joker():
    deck = shuffle(mixup=False)

    assert len(deck) == 53
    assert deck.count(JOKER) == 1


def test_joker_is_worth_ten_points():
    assert count_points([JOKER]) == 10


@pytest.mark.parametrize(
    "rank", ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
)
def test_drop_3_uses_joker_to_match_any_rank(rank):
    matching_cards = [rank + "C", rank + "H", JOKER]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    remaining_cards = [candidate + "D" for candidate in ranks if candidate[0] != rank[0]][:2]
    player = Hand("Tester")
    player += matching_cards + remaining_cards

    discard = drop_3(player)

    assert sorted(player.hand) == sorted(remaining_cards)
    assert discard in matching_cards


def test_drop_3_does_not_accept_joker_without_a_matching_pair():
    player = Hand("Tester")
    player += [JOKER, "2C", "3D", "4H", "5S"]

    with pytest.raises(AssertionError, match="without 3 matching cards"):
        drop_3(player)


def test_select_card_can_select_joker(monkeypatch):
    player = Hand("Tester")
    player += [JOKER, "JC"]
    monkeypatch.setattr("builtins.input", lambda _: "Joker")

    assert player.pop(select_card(player)) == JOKER


@pytest.mark.parametrize(
    "rank", ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
)
@pytest.mark.parametrize(
    "positions",
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)],
    ids=["first-three", "middle-three", "last-three"],
)
def test_drop_3_removes_three_matching_cards_and_returns_one(rank, positions):
    matching_cards = [rank + suit for suit in ["C", "H", "S"]]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    remaining_cards = [candidate + "D" for candidate in ranks if candidate[0] != rank[0]][:2]
    cards = [None] * 5
    for position, card in zip(positions, matching_cards):
        cards[position] = card
    remaining_positions = [position for position in range(5) if position not in positions]
    for position, card in zip(remaining_positions, remaining_cards):
        cards[position] = card

    player = Hand("Tester")
    player += cards

    discard = drop_3(player)

    assert len(player) == 2
    assert sorted(player.hand) == sorted(remaining_cards)
    assert discard in matching_cards


def test_drop_3_rejects_hand_without_three_matching_cards():
    player = Hand("Tester")
    player += ["2C", "4D", "6H", "8S", "QC"]

    with pytest.raises(AssertionError, match="without 3 matching cards"):
        drop_3(player)


@pytest.mark.parametrize("cards", [["2C"] * 4, ["2C"] * 6])
def test_drop_3_rejects_hand_that_does_not_contain_five_cards(cards):
    player = Hand("Tester")
    player += cards

    with pytest.raises(AssertionError):
        drop_3(player)
