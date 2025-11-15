**Algorithm Overview**

The solver uses:

1. Feedback Partitioning
	- Each guess partitions remaining candidates by (correct placements, incorrect placements).
	- The guess that minimizes the worst-case partition is selected (minimax).

2. Knowledge Deduction
	- From remaining candidates, the solver infers:
		- Ingredients guaranteed to be present
		- Ingredients guaranteed to be absent
		- Ingredients with fixed positions
		- Ingredients with unknown but required presence

This is visualized in the color-coded tracker.

3. Efficient Search
	- With only 720 possible sequences (10 choose 3 × permutations), the solver converges rapidly in simulation and interactive play.
 	- We expect solutions within the allotted number of guesses (confirmed, see histogram!

