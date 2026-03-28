import random
import time
import argparse

#BASE CLASSES
class Die:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def add_points(self, points):
        self.score += points

    def wants_to_roll(self, turn_total):
        """Overridden by subclasses."""
        raise NotImplementedError

class HumanPlayer(Player):
    def wants_to_roll(self, turn_total):
        choice = input("Roll (r) or Hold (h)? ").strip().lower()
        while choice not in ("r", "h"):
            choice = input("Please enter 'r' or 'h': ").strip().lower()
        return choice == "r"

class ComputerPlayer(Player):
    def wants_to_roll(self, turn_total):
        """
        Strategy:
        Hold at min(25, 100 - current_score)
        Otherwise roll
        """
        threshold = min(25, 100 - self.score)
        return turn_total < threshold

#PLAYER FACTORY
class PlayerFactory:
    @staticmethod
    def create(player_type, name):
        if player_type.lower() == "human":
            return HumanPlayer(name)
        elif player_type.lower() == "computer":
            return ComputerPlayer(name)
        else:
            raise ValueError("Player type must be 'human' or 'computer'.")

#GAME CLASS
class PigGame:
    def __init__(self, p1_type="human", p2_type="human"):
        self.die = Die()

        self.player1 = PlayerFactory.create(p1_type, "Player 1")
        self.player2 = PlayerFactory.create(p2_type, "Player 2")
        self.current_player = self.player1

    def switch_player(self):
        self.current_player = (
            self.player2 if self.current_player == self.player1 else self.player1
        )

    def play_turn(self):
        turn_total = 0
        print(f"\n{self.current_player.name}'s turn!")

        while True:
            print(
                f"Current turn total: {turn_total}, "
                f"Total score: {self.current_player.score}"
            )

            wants_roll = self.current_player.wants_to_roll(turn_total)

            if wants_roll:
                roll = self.die.roll()
                print(f"{self.current_player.name} rolled: {roll}")

                if roll == 1:
                    print("Rolled 1 — turn over, no points added.")
                    return
                else:
                    turn_total += roll
            else:
                print(f"{self.current_player.name} holds.")
                self.current_player.add_points(turn_total)
                print(f"{turn_total} points added.")
                return

    def play(self):
        print("Welcome to Pig!")

        while self.player1.score < 100 and self.player2.score < 100:
            self.play_turn()
            self.switch_player()

        # Determine winner
        winner = (
            self.player1 if self.player1.score >= 100 else self.player2
        )
        print(f"\n{winner.name} wins with {winner.score}!")
        print("Game over.")


#TIMED GAME PROXY
class TimedGameProxy:
    """
    Wraps a PigGame and stops after 60 seconds.
    """

    def __init__(self, game):
        self.game = game
        self.start_time = time.time()

    def play(self):
        print("Timed mode: You have 1 minute!")

        while True:
            # Stop if time exceeded
            if time.time() - self.start_time >= 60:
                self.end_game_time_up()
                return

            # Stop if someone reaches 100
            if self.game.player1.score >= 100 or self.game.player2.score >= 100:
                break

            self.game.play_turn()
            self.game.switch_player()

        # Normal end (someone reached 100)
        winner = (
            self.game.player1
            if self.game.player1.score >= 100
            else self.game.player2
        )
        print(f"\n{winner.name} wins with {winner.score}!")
        print("Game over.")

    def end_game_time_up(self):
        print("\n Time is up!")
        p1, p2 = self.game.player1, self.game.player2

        if p1.score > p2.score:
            winner = p1
        elif p2.score > p1.score:
            winner = p2
        else:
            print("It's a tie!")
            return

        print(f"Winner based on score at time-up: {winner.name} ({winner.score})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--player1", default="human")
    parser.add_argument("--player2", default="human")
    parser.add_argument("--timed", action="store_true")
    args = parser.parse_args()

    game = PigGame(args.player1, args.player2)

    if args.timed:
        game = TimedGameProxy(game)

    game.play()