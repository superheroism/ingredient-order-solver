#!/usr/bin/env python3
"""
Ingredient Order Solver (Python version)

- 10 ingredients: A–J
- Code length: 3 (no repeated ingredients)
- Feedback per guess:
    * correct placements   = right ingredient, right position
    * incorrect placements = right ingredient, wrong position

The solver uses a Mastermind-style strategy to narrow down candidates.
"""

from itertools import permutations
from typing import List, Tuple, Dict, Optional


class IngredientOrderSolver:
    def __init__(
        self,
        ingredients: str = "ABCDEFGHIJ",
        code_len: int = 3,
        max_guesses: int = 12,
    ) -> None:
        self.ingredients = ingredients
        self.code_len = code_len
        self.max_guesses = max_guesses
        self.universe = self._generate_universe()
        self.reset()

    # ---------------- Core setup ---------------- #

    def _generate_universe(self) -> List[str]:
        """All possible codes: permutations of given length, no repeats."""
        return ["".join(p) for p in permutations(self.ingredients, self.code_len)]

    def reset(self) -> None:
        """Reset to initial state."""
        self.history: List[Dict] = []  # each: {"guess": str, "correct": int, "incorrect": int}
        self.candidates: List[str] = list(self.universe)
        self.notes = self._deduce_knowledge(self.candidates)
        self.status: str = "RUNNING"  # RUNNING | SOLVED | UNSOLVABLE
        self.solution: Optional[str] = None
        self._last_guess: Optional[str] = None

    # ---------------- Scoring & filtering ---------------- #

    def _score(self, guess: str, code: str) -> Tuple[int, int]:
        """
        Compute (correct, incorrect) for a guess vs code.

        correct   = ingredients in the right position
        incorrect = ingredients present but in different positions
        """
        correct = sum(g == c for g, c in zip(guess, code))
        overlap = len(set(guess) & set(code))
        incorrect = overlap - correct
        return correct, incorrect

    def _consistent_codes(self, history: List[Dict], universe: List[str]) -> List[str]:
        """Filter universe to those codes consistent with all past feedback."""
        out = []
        for code in universe:
            ok = True
            for h in history:
                c, w = self._score(h["guess"], code)
                if c != h["correct"] or w != h["incorrect"]:
                    ok = False
                    break
            if ok:
                out.append(code)
        return out

    def _best_next_guess(self, candidates: List[str], universe: List[str]) -> str:
        """
        Choose a guess that (roughly) minimizes worst-case remaining candidates.
        If tied, prefer guesses that are themselves candidates.
        """
        guess_space = candidates if candidates else universe
        best_guess = None
        best_worst_bucket = float("inf")
        best_is_candidate = False

        for g in guess_space:
            buckets: Dict[Tuple[int, int], int] = {}
            for c in candidates:
                score = self._score(g, c)
                buckets[score] = buckets.get(score, 0) + 1

            worst_bucket = max(buckets.values()) if buckets else 0
            is_cand = g in candidates

            if (
                worst_bucket < best_worst_bucket
                or (worst_bucket == best_worst_bucket and is_cand and not best_is_candidate)
            ):
                best_guess = g
                best_worst_bucket = worst_bucket
                best_is_candidate = is_cand

        return best_guess or guess_space[0]

    # ---------------- Knowledge / tracker ---------------- #

    def _deduce_knowledge(self, candidates: List[str]) -> Dict:
        """
        For each ingredient, deduce:
          - absent      : never appears in any candidate
          - white       : appears in all candidates, but position not fixed
          - black@pos   : appears in all candidates at the same index
          - unknown     : sometimes present, sometimes not
        """
        per_ingredient: Dict[str, Dict[str, str]] = {}
        if not candidates:
            for ch in self.ingredients:
                per_ingredient[ch] = {"status": "unknown"}
            return {"per_ingredient": per_ingredient}

        n = len(candidates)
        letter_counts = {ch: 0 for ch in self.ingredients}
        letter_pos = {ch: [0] * self.code_len for ch in self.ingredients}

        for code in candidates:
            s = set(code)
            for ch in s:
                letter_counts[ch] += 1
            for i, ch in enumerate(code):
                letter_pos[ch][i] += 1

        for ch in self.ingredients:
            if letter_counts[ch] == 0:
                per_ingredient[ch] = {"status": "absent"}
            elif letter_counts[ch] == n:
                # ingredient is in every candidate; check if position is fixed
                fixed_idx = None
                for i in range(self.code_len):
                    if letter_pos[ch][i] == n:
                        fixed_idx = i
                        break
                if fixed_idx is not None:
                    per_ingredient[ch] = {"status": f"black@{fixed_idx}"}
                else:
                    per_ingredient[ch] = {"status": "white"}
            else:
                per_ingredient[ch] = {"status": "unknown"}

        return {"per_ingredient": per_ingredient}

    def tracker_str(self) -> str:
        """
        Visual tracker like:

        | A B C D E |
        | F G H I J |

        Each cell shows:
          - 1/2/3: ingredient known correct at that position
          - ?    : ingredient in the set, position not known
          - X    : ingredient definitely not in the set
          - _    : unknown
        """
        per = self.notes.get("per_ingredient", {})
        lines = []
        for row in ["ABCDE", "FGHIJ"]:
            symbols = []
            for ch in row:
                status = per.get(ch, {}).get("status", "unknown")
                if status.startswith("black@"):
                    idx = int(status.split("@")[1]) + 1  # 1-based position
                    symbols.append(str(idx))
                elif status == "white":
                    symbols.append("?")
                elif status == "absent":
                    symbols.append("X")
                else:
                    symbols.append("_")
            lines.append("| " + " ".join(symbols) + " |")
        return "\n".join(lines)

    # ---------------- Public API ---------------- #

    def suggest(self) -> str:
        """Return a suggested next guess."""
        if not self.history:
            self._last_guess = "ABC"
        else:
            self._last_guess = self._best_next_guess(self.candidates, self.universe)
        return self._last_guess

    def step(self, correct: int, incorrect: int, guess: Optional[str] = None) -> str:
        """
        Record feedback for a guess and update state.

        correct   = correct placements (right ingredient, right position)
        incorrect = incorrect placements (right ingredient, wrong position)
        """
        if guess is None:
            if self._last_guess is None:
                raise ValueError("No previous guess. Call suggest() or pass a guess.")
            guess = self._last_guess

        self.history.append({"guess": guess, "correct": correct, "incorrect": incorrect})

        # If all 3 are correct, we’re done.
        if correct == self.code_len:
            self.status = "SOLVED"
            self.solution = guess
            self.candidates = [guess]
            self.notes = self._deduce_knowledge(self.candidates)
            return self.status

        # Filter candidates based on all feedback so far
        self.candidates = self._consistent_codes(self.history, self.universe)
        self.notes = self._deduce_knowledge(self.candidates)

        if len(self.candidates) == 0:
            self.status = "UNSOLVABLE"
            self.solution = None
        elif len(self.candidates) == 1:
            self.status = "SOLVED"
            self.solution = self.candidates[0]

        return self.status

    def simulate(self, secret: str, verbose: bool = True) -> Tuple[List[Dict], str]:
        """
        Simulate playing against a known secret (for testing the algorithm).
        Returns (history, final_status).
        """
        secret = self._validate_secret(secret)
        self.reset()

        if verbose:
            print(f"Simulating against secret: {secret}")

        for guess_num in range(1, self.max_guesses + 1):
            if len(self.candidates) == 0:
                self.status = "UNSOLVABLE"
                break
            if len(self.candidates) == 1:
                self.status = "SOLVED"
                self.solution = self.candidates[0]
                break

            guess = self.suggest()
            correct, incorrect = self._score(guess, secret)
            self.step(correct, incorrect, guess)

            if verbose:
                print(
                    f"Guess {guess_num}: {guess} → "
                    f"correct={correct}, incorrect={incorrect}, "
                    f"remaining={len(self.candidates)}"
                )
                print(self.tracker_str())
                print("-" * 40)

            if self.status != "RUNNING":
                break

        if verbose:
            print(f"Final status: {self.status}, solution: {self.solution}")

        return self.history, self.status

    # ---------------- Validation helpers ---------------- #

    def _validate_secret(self, secret: str) -> str:
        secret = secret.strip().upper()
        if len(secret) != self.code_len:
            raise ValueError(f"Secret must be {self.code_len} letters.")
        if any(ch not in self.ingredients for ch in secret):
            raise ValueError(f"Secret letters must be in {self.ingredients}.")
        if len(set(secret)) != self.code_len:
            raise ValueError("Secret must have distinct letters (no repeats).")
        return secret


# ---------------- CLI helpers ---------------- #

def interactive_mode() -> None:
    """Play the solver with unknown secret; user provides feedback each round."""
    solver = IngredientOrderSolver()
    print("=== Ingredient Order Solver (Interactive Mode) ===")
    print("Ingredients: A–J (no repeats), 3-letter order.")
    print("On each guess, enter feedback as:")
    print("  correct placements   = right ingredient, right position")
    print("  incorrect placements = right ingredient, wrong position")
    print(f"Max guesses (suggested): {solver.max_guesses}")
    print()

    while solver.status == "RUNNING" and len(solver.history) < solver.max_guesses:
        guess = solver.suggest()
        print(f"Suggested guess: {guess}")
        print("Tracker:")
        print(solver.tracker_str())
        print()

        # Get feedback
        while True:
            try:
                correct = int(input("Enter number of correct placements (0–3): ").strip() or "0")
                incorrect = int(input("Enter number of incorrect placements (0–3): ").strip() or "0")
            except ValueError:
                print("Please enter integers (0–3). Try again.")
                continue

            if not (0 <= correct <= 3 and 0 <= incorrect <= 3):
                print("Feedback out of range. Try again.")
                continue

            # Basic sanity: can't exceed 3 total
            if correct + incorrect > 3:
                print("Sum of correct + incorrect can't exceed 3. Try again.")
                continue

            break

        status = solver.step(correct, incorrect, guess)
        print(
            f"Recorded: correct={correct}, incorrect={incorrect}. "
            f"Status={status}, remaining candidates={len(solver.candidates)}"
        )
        print()

        if status == "SOLVED":
            print(f"🎉 Solved! The ingredient order is {solver.solution}.")
            break
        if status == "UNSOLVABLE":
            print("✖ No consistent ingredient orders remain. Check feedback for mistakes.")
            break

    if solver.status == "RUNNING":
        print("Reached max suggested guesses; you can continue reasoning manually if you like.")
        print(f"Remaining candidates: {len(solver.candidates)}")
        print(solver.candidates[:20], "..." if len(solver.candidates) > 20 else "")


def simulation_mode() -> None:
    """Run a simulation against a known secret."""
    solver = IngredientOrderSolver()
    print("=== Ingredient Order Solver (Simulation Mode) ===")
    print("Enter a secret 3-letter code using A–J (no repeats). Example: JAD")

    while True:
        secret = input("Secret: ").strip().upper()
        try:
            secret = solver._validate_secret(secret)
            break
        except ValueError as e:
            print(f"Invalid secret: {e}")

    print()
    solver.simulate(secret, verbose=True)


def main() -> None:
    print("Ingredient Order Solver")
    print("=======================")
    print("Choose mode:")
    print("  1) Interactive (unknown order; you enter feedback)")
    print("  2) Simulation (test solver against known order)")
    print()

    choice = input("Enter 1 or 2 [1]: ").strip() or "1"
    if choice == "2":
        simulation_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
