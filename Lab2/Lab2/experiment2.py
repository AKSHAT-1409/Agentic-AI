

from collections import deque
import heapq

# ---------------------------------------------------------------------------
# The world:  S = start, G = goal, # = obstacle, . = free
# Two gaps in each wall - a near one and a far one. The near gap gives the
# shortest path in steps; the far gap gives the cheapest path once terrain
# costs are introduced in Exercise 1.
# ---------------------------------------------------------------------------
GRID = [
    "S........",
    "##.####.#",
    ".........",
    "#.####.##",
    "........G",
]

# Cost of *entering* each cell (Exercise 1). The near corridor is a swamp.
TERRAIN = [
    "111111111",
    "##9####1#",
    "119111111",
    "#1####1##",
    "111111111",
]

PITS = [(2, 1)]          # Exercise 3
SURPRISE_OBSTACLE = (2, 2)   # Exercise 2: appears after planning

UP, DOWN, LEFT, RIGHT = "Up", "Down", "Left", "Right"
MOVES = [(UP, (-1, 0)), (DOWN, (1, 0)), (LEFT, (0, -1)), (RIGHT, (0, 1))]


# ---------------------------------------------------------------------------
# 1. The world model (also used as the true environment)
# ---------------------------------------------------------------------------
class GridModel:
    """A character grid. The agent plans over an instance of this; the
    environment holds its own instance. They need not agree."""

    def __init__(self, rows, terrain=None, blocked=()):
        self.rows = list(rows)
        self.h = len(self.rows)
        self.w = len(self.rows[0])
        self.blocked = set(blocked)
        self.terrain = terrain
        self.start = self.find("S")
        self.goal = self.find("G")

    def find(self, ch):
        for r, row in enumerate(self.rows):
            c = row.find(ch)
            if c >= 0:
                return (r, c)
        return None

    def passable(self, cell):
        r, c = cell
        if not (0 <= r < self.h and 0 <= c < self.w):
            return False
        if cell in self.blocked:
            return False
        return self.rows[r][c] != "#"

    def cost(self, cell):
        if self.terrain is None:
            return 1
        r, c = cell
        ch = self.terrain[r][c]
        return int(ch) if ch.isdigit() else 1

    def neighbours(self, cell):
        r, c = cell
        for name, (dr, dc) in MOVES:
            nxt = (r + dr, c + dc)
            if self.passable(nxt):
                yield name, nxt

    def render(self, path=(), agent=None, pits=()):
        path = set(path)
        out = []
        for r, row in enumerate(self.rows):
            line = []
            for c, ch in enumerate(row):
                cell = (r, c)
                if cell == agent:
                    line.append("A")
                elif cell in pits:
                    line.append("P")
                elif cell in self.blocked:
                    line.append("X")
                elif ch in "SG#":
                    line.append(ch)
                elif cell in path:
                    line.append("*")
                else:
                    line.append(".")
            out.append(" ".join(line))
        return "\n".join(out)


# ---------------------------------------------------------------------------
# 2. Planners
# ---------------------------------------------------------------------------
def bfs(model, start=None, goal=None):
    """Breadth-first search. The parent map IS the plan: walk it backwards
    from the goal and reverse. Returns (plan, path, stats)."""
    start = start or model.start
    goal = goal or model.goal
    frontier = deque([start])
    parent = {start: (None, None)}      # cell -> (previous cell, action taken)
    expanded = 0
    max_frontier = 1

    while frontier:
        cell = frontier.popleft()
        expanded += 1
        if cell == goal:
            break
        for action, nxt in model.neighbours(cell):
            if nxt not in parent:
                parent[nxt] = (cell, action)
                frontier.append(nxt)
        max_frontier = max(max_frontier, len(frontier))

    stats = {"expanded": expanded, "max_frontier": max_frontier,
             "visited": len(parent)}
    if goal not in parent:
        return None, None, stats
    return _reconstruct(parent, start, goal) + (stats,)


def uniform_cost(model, start=None, goal=None):
    """Exercise 1: uniform-cost search over per-cell terrain costs."""
    start = start or model.start
    goal = goal or model.goal
    frontier = [(0, start)]
    parent = {start: (None, None)}
    best = {start: 0}
    expanded = 0
    max_frontier = 1

    while frontier:
        g, cell = heapq.heappop(frontier)
        if g > best.get(cell, float("inf")):
            continue
        expanded += 1
        if cell == goal:
            break
        for action, nxt in model.neighbours(cell):
            ng = g + model.cost(nxt)
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                parent[nxt] = (cell, action)
                heapq.heappush(frontier, (ng, nxt))
        max_frontier = max(max_frontier, len(frontier))

    stats = {"expanded": expanded, "max_frontier": max_frontier,
             "visited": len(parent)}
    if goal not in parent:
        return None, None, stats
    return _reconstruct(parent, start, goal) + (stats,)


def _reconstruct(parent, start, goal):
    plan, path, cell = [], [goal], goal
    while cell != start:
        prev, action = parent[cell]
        plan.append(action)
        path.append(prev)
        cell = prev
    plan.reverse()
    path.reverse()
    return plan, path


def path_cost(model, path):
    return sum(model.cost(cell) for cell in path[1:])


# ---------------------------------------------------------------------------
# 3. Execution
# ---------------------------------------------------------------------------
def step_of(action):
    return dict(MOVES)[action]


def execute(world, plan, start, trace=True, indent="  "):
    """Walk the committed plan in the real world. Returns (final cell, steps,
    failure) where failure is the blocked cell that stopped execution."""
    cell = start
    for i, action in enumerate(plan, 1):
        dr, dc = step_of(action)
        nxt = (cell[0] + dr, cell[1] + dc)
        if not world.passable(nxt):
            if trace:
                print("%sstep %-3d %-6s -> %s BLOCKED - plan has failed"
                      % (indent, i, action, str(nxt)))
            return cell, i - 1, nxt
        cell = nxt
        if trace:
            print("%sstep %-3d %-6s -> %s%s"
                  % (indent, i, action, cell, "   GOAL REACHED"
                     if cell == world.goal else ""))
    return cell, len(plan), None


# ---------------------------------------------------------------------------
# 4. Exercise 3 - hybrid agent
# ---------------------------------------------------------------------------
def unsafe_cells(pits):
    """Reactive rule: never step into a cell adjacent to a pit. Adjacency is
    taken as 8-connected, which is the conservative reading."""
    unsafe = set()
    for pr, pc in pits:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                unsafe.add((pr + dr, pc + dc))
    return unsafe


class HybridAgent:
    """Deliberative planner underneath, reactive safety layer on top. The
    safety layer both filters the model before planning and vetoes any move
    at execution time - belt and braces, so an unsafe plan can never run."""

    def __init__(self, model, pits):
        self.pits = set(pits)
        self.unsafe = unsafe_cells(pits)
        safe_model = GridModel(model.rows, model.terrain,
                               blocked=set(model.blocked) | self.unsafe)
        self.model = safe_model

    def plan(self):
        return bfs(self.model)

    def veto(self, cell):
        return cell in self.unsafe


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def banner(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def main():
    world = GridModel(GRID, TERRAIN)

    # ---------------- Experiment 2 ---------------------------------------
    banner("EXPERIMENT 2 - Deliberative agent: plan with BFS, then execute")
    print("The agent's internal model of the world "
          "(S start, G goal, # obstacle):")
    print(world.render())
    print("\nStart %s   Goal %s   Grid %dx%d"
          % (world.start, world.goal, world.h, world.w))

    print("\n-- PLAN phase (BFS over the internal model) " + "-" * 26)
    plan, path, stats = bfs(world)
    print("Nodes expanded      : %d" % stats["expanded"])
    print("Cells reached       : %d" % stats["visited"])
    print("Max frontier size   : %d" % stats["max_frontier"])
    print("Plan length         : %d actions" % len(plan))
    print("Plan                : %s" % " ".join(plan))
    print("\nThe planned path through the model (* = path):")
    print(world.render(path))

    print("\n-- ACT phase (executing the committed plan) " + "-" * 26)
    final, steps, failure = execute(world, plan, world.start)
    print("Final cell          : %s" % (final,))
    print("Goal reached        : %s" % (final == world.goal))
    print("Steps executed      : %d" % steps)
    print("Path cost (terrain) : %d" % path_cost(world, path))

    # ---------------- Exercise 1 -----------------------------------------
    banner("EXERCISE 1 - Uniform-cost search with terrain costs")
    print("Cost of entering each cell (walls shown as #):")
    print("\n".join(" ".join(row) for row in TERRAIN))
    print("\nThe near corridor is a swamp (cost 9). BFS cannot see cost - it")
    print("only counts steps - so it walks straight into it.")

    uplan, upath, ustats = uniform_cost(world)
    print("\nUCS plan length     : %d actions" % len(uplan))
    print("UCS plan            : %s" % " ".join(uplan))
    print("\nThe UCS path (* = path):")
    print(world.render(upath))

    print("\nComparison over the same world:")
    print("%-22s %10s %10s %12s" % ("Search", "Steps", "Cost", "Expanded"))
    print("%-22s %10d %10d %12d"
          % ("Breadth-first", len(plan), path_cost(world, path),
             stats["expanded"]))
    print("%-22s %10d %10d %12d"
          % ("Uniform-cost", len(uplan), path_cost(world, upath),
             ustats["expanded"]))
    print("\nBFS is optimal in STEPS, UCS is optimal in COST. They disagree")
    print("here because the two are not the same objective.")

    # ---------------- Exercise 2 -----------------------------------------
    banner("EXERCISE 2 - The world changes after planning: detect and re-plan")
    print("The agent plans over its model as before, but the real world has an")
    print("obstacle at %s that the model does not know about (shown as X):"
          % (SURPRISE_OBSTACLE,))
    real = GridModel(GRID, TERRAIN, blocked=[SURPRISE_OBSTACLE])
    print(real.render())

    print("\n-- First plan (over the stale model) " + "-" * 33)
    plan1, path1, _ = bfs(world)
    print("Plan (%d actions)    : %s" % (len(plan1), " ".join(plan1)))
    print("\n-- Execution in the real world " + "-" * 39)
    pos, done, failure = execute(real, plan1, world.start)
    print("Execution stopped at: %s after %d steps" % (pos, done))
    print("Blocked cell        : %s" % (failure,))

    print("\n-- Re-plan from the current position " + "-" * 33)
    print("The agent updates its model with what it just sensed and searches")
    print("again from where it is standing - not from the original start.")
    world.blocked.add(failure)
    plan2, path2, stats2 = bfs(world, start=pos)
    print("New plan (%d actions): %s" % (len(plan2), " ".join(plan2)))
    print("\nThe re-planned path from the agent's current position (A):")
    print(world.render(path2, agent=pos))
    print()
    pos2, done2, failure2 = execute(real, plan2, pos)
    print("Final cell          : %s" % (pos2,))
    print("Goal reached        : %s" % (pos2 == real.goal))
    print("Total steps walked  : %d  (%d before replan + %d after)"
          % (done + done2, done, done2))
    print("Ideal had the agent known in advance: %d steps"
          % len(bfs(GridModel(GRID, TERRAIN,
                              blocked=[SURPRISE_OBSTACLE]))[0]))
    world.blocked.discard(failure)

    # ---------------- Exercise 3 -----------------------------------------
    banner("EXERCISE 3 - Hybrid agent: reactive safety rule over a plan")
    print("A pit (P) is added at %s. The reactive rule is absolute:" % (PITS[0],))
    print("never step into a cell adjacent to a pit (8-connected).")
    unsafe = unsafe_cells(PITS)
    print("\nCells the reactive layer forbids: %s"
          % ", ".join(str(c) for c in sorted(unsafe)
                      if 0 <= c[0] < world.h and 0 <= c[1] < world.w))

    plain = GridModel(GRID, TERRAIN)
    pplan, ppath, _ = bfs(plain)
    violations = [c for c in ppath if c in unsafe]
    print("\nThe purely deliberative plan of %d actions passes through %d"
          % (len(pplan), len(violations)))
    print("forbidden cell(s): %s" % (violations or "none"))
    print("\nPurely deliberative path (P = pit, * = path):")
    print(plain.render(ppath, pits=PITS))

    agent = HybridAgent(plain, PITS)
    hplan, hpath, hstats = agent.plan()
    print("\nThe hybrid agent plans over a model with those cells removed.")
    print("Hybrid plan length  : %d actions" % len(hplan))
    print("Hybrid plan         : %s" % " ".join(hplan))
    print("Violations          : %d"
          % len([c for c in hpath if agent.veto(c)]))
    print("\nHybrid path (P = pit, * = path):")
    print(plain.render(hpath, pits=PITS))

    print("\n%-26s %8s %8s" % ("Agent", "Steps", "Unsafe"))
    print("%-26s %8d %8d" % ("Deliberative only", len(pplan), len(violations)))
    print("%-26s %8d %8d" % ("Hybrid (reactive + plan)", len(hplan), 0))
    print("\nSafety is not free: the hybrid agent pays %d extra steps to keep"
          % (len(hplan) - len(pplan)))
    print("its distance from the pit.")


if __name__ == "__main__":
    main()
