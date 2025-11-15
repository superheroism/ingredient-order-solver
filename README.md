# Ingredient Order Solver

A Mastermind-style deduction puzzle where the goal is to discover the correct
**3-ingredient sequence (A–J)** using feedback about **correct** and **incorrect** placements.

This project includes:

- **A fully interactive, browser-based solver** — *no server required*  
- **An optimal solving algorithm** using minimax feedback partitioning  
- **A color-coded deduction tracker** that updates in real time  
- **Light/Dark mode toggle**  
- **A reference Python implementation** of the solver algorithm  
- **Simulation mode** to test the solver against known sequences  
---

## Live Implementation: [Click here!](https://superheroism.github.io/ingredient-order-solver/)
---

## Features

- **Optimal Guessing Strategy**  
  - Uses a minimax feedback-bucketing approach (similar to Knuth’s Mastermind algorithm).
  - Guaranteed to find a solution in [7 or fewer steps](https://github.com/superheroism/ingredient-order-solver/blob/main/notes/CAS%20Algorithm%20Histogram.png).

- **Real-Time Deduction Grid**  
  - 🟩 Green: ingredient is in the correct position
  - 🟨 Yellow: ingredient is in the correct set, but the position is unknown
  - ⬛ Gray: ingredient is *not* in the correct set.
  - Uncolored: unknown

- **Theme Toggle**  
    Dark and Light mode built in.

- **Two Modes**  
  - **Interactive Mode** — user enters feedback about each successive guess, and receives recommendations.
  - **Simulation Mode** — the solver automatically selects the recommended guess at each step, and tracks its progress.

- **No Server Required**  
    Works entirely in the browser (HTML + JS).  
---

## Project Structure
```
ingredient-order-solver/
│
├── index.html              # Main web app (JS, CSS, solver logic)
│
├── python/
│ └── ingredient_solver.py  # Reference Python implementation
│
├── docs/
│ └── algorithm-notes.md    # Explanation of deduction logic
│
├── README.md               # You are here!
└── LICENSE                 # MIT License
```
---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/superheroism/ingredient-order-solver.git
cd ingredient-order-solver
```

### 2. Run the solver (Web App)

Use the live implementation, hosted here on GitHub:
[Click here!](https://superheroism.github.io/ingredient-order-solver/)

Or, open the following file from the repo in any browser:
```index.html```

Or, run the Python solver:
```bash
cd python
python ingredient_solver.py
```

### License

This project is licensed under the MIT License.
