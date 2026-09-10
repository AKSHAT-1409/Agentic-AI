class VacuumEnvironment:
    def __init__(self, state):
        self.state = state.copy()
        self.location = 'A'
        self.performance = 0

    def percept(self):
        return (self.location, self.state[self.location])

    def execute(self, action):
        if action == "Suck":
            if self.state[self.location] == "Dirty":
                self.state[self.location] = "Clean"
                self.performance += 10

        elif action == "Right":
            if self.location == 'A':
                self.location = 'B'
                self.performance -= 1

        elif action == "Left":
            if self.location == 'B':
                self.location = 'A'
                self.performance -= 1

        elif action == "NoOp":
            pass


# -----------------------------
# Simple Reflex Agent
# -----------------------------
def simple_reflex_agent(percept):
    location, status = percept

    if status == "Dirty":
        return "Suck"

    if location == "A":
        return "Right"

    return "Left"


# -----------------------------
# Model-Based Agent
# -----------------------------
class ModelBasedAgent:

    def __init__(self):
        self.model = {
            'A': 'Unknown',
            'B': 'Unknown'
        }

    def program(self, percept):
        location, status = percept

        # Update internal model
        self.model[location] = status

        # If current square is dirty
        if status == "Dirty":
            self.model[location] = "Clean"
            return "Suck"

        # If both locations are known to be clean
        if self.model['A'] == "Clean" and self.model['B'] == "Clean":
            return "NoOp"

        # Otherwise move to other square
        if location == "A":
            return "Right"

        return "Left"


# -----------------------------
# Function to run simulation
# -----------------------------
def run_simple_reflex(initial_state, steps):

    env = VacuumEnvironment(initial_state)

    print("\n===== SIMPLE REFLEX AGENT =====")

    for step in range(1, steps + 1):

        percept = env.percept()
        action = simple_reflex_agent(percept)

        print(f"Step {step}")
        print("Percept :", percept)
        print("Action  :", action)

        env.execute(action)

        print("State   :", env.state)
        print("Location:", env.location)
        print("Score   :", env.performance)
        print("-" * 35)

    return env.performance


def run_model_based(initial_state, steps):

    env = VacuumEnvironment(initial_state)
    agent = ModelBasedAgent()

    print("\n===== MODEL-BASED AGENT =====")

    for step in range(1, steps + 1):

        percept = env.percept()
        action = agent.program(percept)

        print(f"Step {step}")
        print("Percept :", percept)
        print("Action  :", action)

        env.execute(action)

        print("State   :", env.state)
        print("Memory  :", agent.model)
        print("Location:", env.location)
        print("Score   :", env.performance)
        print("-" * 35)

    return env.performance


# -----------------------------
# Main Program
# -----------------------------
initial_state = {
    'A': 'Dirty',
    'B': 'Dirty'
}

steps = 20

simple_score = run_simple_reflex(initial_state, steps)

model_score = run_model_based(initial_state, steps)

print("\n==============================")
print("Performance Comparison")
print("==============================")
print("Simple Reflex Agent :", simple_score)
print("Model-Based Agent   :", model_score)