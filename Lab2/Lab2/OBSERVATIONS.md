# Lab 2 / Experiment 2 — Observations (draft for the report)

Run `python experiment2_deliberative_agent.py` and paste the traces into the
result section; the notes below cover the observations and the viva questions.

## The world used

A 5×9 grid with two walls, each pierced by two gaps — a near one and a far one.
Start `S` is at (0,0), goal `G` at (4,8). This layout matters: a reactive agent
following "move towards the goal" walks into the first wall and stops, because
the correct first move is *away* from the goal in the vertical sense. Only an
agent that searches the whole model can see that the detour exists.

## 1. Plan then act

BFS expands 31 of the 33 free cells and returns a plan of **12 actions**:

```
Right Right Down Down Right Right Right Right Down Down Right Right
```

Execution is trivial — the agent replays the list and arrives at (4,8). That
triviality is the point. All the intelligence has moved into the planning
phase; the acting phase is a for-loop. This is **sense–plan–act**, as opposed
to the sense–react loop of Experiment 1, where there was no plan at all and
every step was decided from scratch.

Note also that the **parent map is the plan**. BFS never builds a path
explicitly — it records, for each cell it reaches, which cell it came from and
which move got it there. Walking that map backwards from the goal and reversing
gives the action sequence for free.

## 2. Exercise 1 — uniform-cost search

Adding a terrain cost per cell (the near corridor is a swamp of cost 9) splits
"shortest" into two different questions:

| Search | Steps | Cost | Nodes expanded |
|---|---:|---:|---:|
| Breadth-first | 12 | 28 | 31 |
| Uniform-cost | 14 | **14** | 23 |

BFS is still optimal — in *steps*, which is all it can count. It walks straight
into the swamp because it treats every move as equally good. UCS takes two extra
steps around the long way and halves the cost. Neither is wrong; they are
optimal with respect to different objectives, and the choice of objective is a
modelling decision, not an algorithmic one.

BFS is the special case of UCS where every action costs the same. When that
holds, BFS is preferable because it needs only a FIFO queue instead of a
priority queue.

## 3. Exercise 2 — the world changes after planning

The agent plans over its model, but the real world has an obstacle at (2,2) that
the model does not contain. Execution proceeds three steps and then fails:

```
step 4   Down   -> (2, 2) BLOCKED - plan has failed
```

The agent detects the failure by *attempting* the move, updates its model with
what it just sensed, and re-plans **from its current position** (1,2) rather
than from the start. The new plan of 13 actions goes around through the far gap
and reaches the goal.

| | Steps |
|---|---:|
| Walked before the failure | 3 |
| Walked after re-planning | 13 |
| **Total** | **16** |
| Optimal, had the agent known in advance | 14 |

The 2-step gap is the **price of a wrong model**. This is the assumption
deliberative planning silently makes: that the model is accurate and the world
holds still while the plan is executed. A plan is a commitment made under that
assumption, and re-planning is what you do when the commitment is invalidated.

The parallel with Experiment 1 is exact. There, a model-based vacuum agent that
trusted a stale memory was beaten by a reflex agent that kept re-checking. Here,
a planner that trusts a stale map walks into a wall. Same failure, larger scale:
**a model is only worth as much as its accuracy.**

## 4. Exercise 3 — the hybrid agent

A pit is placed at (2,1) and the reactive rule is absolute: *never step into a
cell adjacent to a pit*, taking adjacency as 8-connected. That forbids nine
cells, two of which — (1,2) and (2,2) — lie on the deliberative agent's optimal
path.

| Agent | Steps | Unsafe cells entered |
|---|---:|---:|
| Deliberative only | 12 | 2 |
| Hybrid (reactive + deliberative) | 14 | 0 |

The hybrid agent applies the safety rule in two places: it removes unsafe cells
from the model *before* planning, so no unsafe plan is ever produced, and it
vetoes unsafe moves *during* execution, so a plan made from a stale model can
still be stopped. The reactive layer overrides the deliberative one — that is
the defining property of a hybrid architecture, and it is the right ordering,
because a hazard is immediate while a plan is a prediction.

Safety costs 2 extra steps. That is not a defect; it is the trade being made
explicit. A layered agent buys guaranteed hazard avoidance at the price of
optimality.

## Viva answers

**1. Contrast reactive, deliberative and hybrid architectures.**
A *reactive* agent maps the current percept directly to an action through
condition–action rules — fast, cheap, and stateless, but it cannot pursue a goal
that requires temporarily moving away from it (Experiment 1). A *deliberative*
agent maintains an internal model, searches it for a complete action sequence
that reaches the goal, commits to that plan and executes it — it handles
long-horizon goals, but is slow, and is only as correct as its model. A *hybrid*
agent layers both: deliberation chooses the route, while reactive rules retain
override authority for immediate hazards. Exercise 3 is exactly that layering.

**2. Why does BFS guarantee the shortest path here, and when is A\* preferred?**
BFS explores in order of increasing depth, so the first time it reaches the
goal, it has done so by a minimum number of moves — and here every move costs
the same (one step), so minimum depth equals minimum cost. It stops guaranteeing
optimality the moment the moves have different costs, which is what Exercise 1
demonstrates. A\* is preferred when the state space is large: it uses a
heuristic estimate of the remaining distance (Manhattan distance on a
4-connected grid) to expand goal-ward cells first, and if that heuristic is
admissible — never overestimating — A\* is still optimal while expanding far
fewer nodes. Here BFS expanded 31 cells out of 33 free ones, essentially the
whole map; A\* would expand a fraction of that on a large grid.

**3. What assumption of deliberative planning does re-planning address?**
That the model is correct and the environment is static — that nothing changes
between the moment the plan is made and the moment it finishes executing.
Re-planning is the admission that this assumption fails: the agent detects the
discrepancy at execution time, corrects its model with what it has sensed, and
searches again from where it now stands. It converts a brittle open-loop plan
into a closed loop of plan–act–sense–re-plan.
