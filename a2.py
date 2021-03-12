#!/usr/bin/env python3
"""
Assignment 2 - Sleeping Coders
CSSE1001/7030
Semester 2, 2019
"""

import random

__author__ = "Brae Webb"


class Card:
    """
    Abstract representation of a card.
    """

    PLAY_ACTION = "NO_ACTION"

    def play(self, player, game):
        """
        Removes the played card from the player's hand. Picks up a new card
        from the game pickup pile and adds the card to the player's hand.
        Sets the action for this card.

        Parameters:
            player (Player): The player who just played this card.
            game (CodersGame): The current game of Sleeping Coders.

        """
        hand = player.get_hand()
        slot = hand.get_cards().index(self)
        hand.remove_card(slot)
        hand.add_cards(game.get_pickup_pile().pick())
        game.set_action(self.PLAY_ACTION)

    def action(self, player, game, slot):
        """
        Perform a special card action. The base Card class has no special action.

        Parameters:
            player (Player): The player relevant for this action.
            game (CodersGame): The current game of Sleeping Coders.
            slot (int): The slot of the card which was selected for this action.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def __repr__(self):
        return str(self)


class NumberCard(Card):
    """
    Representation of a card.
    """
    def __init__(self, number):
        """
        Construct a card with an assigned number.

        Parameters:
            number (int): The number assigned to this instance of the card.
        """
        super().__init__()
        self._number = number

    def get_number(self):
        """(int): Returns the number assigned to this card."""
        return self._number

    def play(self, player, game):
        """
        Resolves playing the card and then moves to the next player's turn

        Parameters:
            player (Player): The player who just played this card.
            game (CodersGame): The current game of Sleeping Coders.
        """
        super().play(player, game)
        game.next_player()

    def __str__(self):
        return f"{self.__class__.__name__}({self.get_number()})"


class NamedCard(Card):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def get_name(self):
        return self._name

    def __str__(self):
        return f"{self.__class__.__name__}({self.get_name()})"


class CoderCard(NamedCard):
    def play(self, player, game):
        """
        Only sets the action of the game

        Parameters:
            player (Player): The player who just played this card.
            game (CodersGame): The current game of Sleeping Coders.
        """
        game.set_action(self.PLAY_ACTION)


class TutorCard(NamedCard):

    PLAY_ACTION = "PICKUP_CODER"

    def action(self, player, game, slot):
        card = game.get_sleeping_coder(slot)

        if card is None:
            return

        player_deck = game.current_player().get_coders()
        player_deck.add_card(card)
        game.set_sleeping_coder(slot, None)

        game.set_action("NO_ACTION")
        game.next_player()


class ActionCard(Card):
    def action(self, player, game, slot):
        card = player.get_coders().get_card(slot)
        player.get_coders().remove_card(slot)

        self._perform_action(game, player, card)

        game.set_action("NO_ACTION")
        game.next_player()

    def _perform_action(self, game, player, card):
        pass


class KeyboardKidnapperCard(ActionCard):

    PLAY_ACTION = "STEAL_CODER"

    def _perform_action(self, game, player, card):
        # swap decks
        game.current_player().get_coders().add_card(card)


class AllNighterCard(ActionCard):

    PLAY_ACTION = "SLEEP_CODER"

    def _perform_action(self, game, player, card):
        # place back to sleep
        for slot, coder in enumerate(game.get_sleeping_coders()):
            if coder is None:
                game.set_sleeping_coder(slot, card)
                break


class Deck:
    """
    A collection of ordered cards.
    """
    def __init__(self, starting_cards=None):
        """
        Constructs a deck with a set of starting cards.

        Parameters:
            starting_cards (list<Card>): If given, this will be the cards in the
                                         current deck.
        """
        if starting_cards is None:
            starting_cards = []
        self._cards = starting_cards

    def get_cards(self):
        """(list<Card>): Returns a list of cards in the deck."""
        return self._cards

    def get_card(self, slot):
        """(Card): Return the card at the specified slot in a deck."""
        return self._cards[slot]

    def top(self):
        """(Card): Return the card on the top of the deck, i.e. the last added."""
        return self._cards[-1]

    def remove_card(self, slot):
        """Remove a card at the given slot in a deck.

        Parameters:
            slot (int): The slot of the card at which to remove from
        """
        self._cards.pop(slot)

    def get_amount(self):
        """(int): Returns the amount of cards in the deck"""
        return len(self._cards)

    def shuffle(self):
        """
        Randomly places all cards in a new order.
        """
        random.shuffle(self._cards)

    def pick(self, amount=1):
        """
        Take a card or multiple cards from the deck.

        Parameters:
            amount (int): The amount of cards to take from the deck.

        Returns:
            (list<Card>): Cards taken from the deck.
        """
        cards = []
        for _ in range(amount):
            cards.append(self._cards.pop())
        return cards

    def add_card(self, card):
        """
        Place a single card on the top of the deck.

        Parameters:
            card (Card): The card to place on the deck.
        """
        self._cards.append(card)

    def add_cards(self, cards):
        """
        Place a list of cards on top of the deck.

        Parameters:
            cards (list<Card>): The cards to place on the deck.
        """
        self._cards.extend(cards)

    def copy(self, other_deck):
        """
        Copy all of the cards from the other_deck parameter into this deck.

        Parameters:
            other_deck (Deck): Another deck with cards to copy into this deck.
        """
        self.add_cards(other_deck.get_cards())

    def __str__(self):
        card_strings = ', '.join(map(str, self._cards))
        return f"Deck({card_strings})"

    def __repr__(self):
        return str(self)


class Player:
    """
    The base player in a game.
    """
    def __init__(self, name):
        """
        Construct a player with an empty hand, empty coder collection
        and a given name.

        Parameters:
            name (str): The name of the player.
        """
        self._name = name
        self._deck = Deck()
        self._coders = Deck()

    def get_name(self):
        """
        (str): The name of the player.
        """
        return self._name

    def get_hand(self):
        """
        (Deck): The players deck of playable cards.
        """
        return self._deck

    def get_coders(self):
        """
        (Deck): The players deck of collected coder cards.
        """
        return self._coders

    def has_won(self):
        """
        (bool): True iff the player has exactly or more than 4 coders.
        """
        return self._coders.get_amount() >= 4

    def __str__(self):
        return f"Player({self.get_name()}, {self.get_hand()}, {self.get_coders()})"

    def __repr__(self):
        return str(self)


def main():
    print("Please run gui.py instead")


if __name__ == "__main__":
    main()
