class VacuumEnvironment:
    def __init__(self, state):
        # state example: {'A': 'Dirty', 'B': 'Clean'}
        self.state = state
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


def simple_reflex_agent(percept):
    location, status = percept

    if status == "Dirty":
        return "Suck"

    if location == 'A':
        return "Right"

    return "Left"


# -----------------------------
# Initial Environment
# -----------------------------
env = VacuumEnvironment({
    'A': 'Dirty',
    'B': 'Dirty'
})

steps = 10

print("Initial State")
print(f"Location: {env.location}")
print(f"World: {env.state}")
print("-" * 40)

for step in range(1, steps + 1):
    percept = env.percept()
    action = simple_reflex_agent(percept)

    print(f"Step {step}")
    print("Percept :", percept)
    print("Action  :", action)

    env.execute(action)

    print("Location:", env.location)
    print("World   :", env.state)
    print("Performance:", env.performance)
    print("-" * 40)

print("\nFinal State")
print("Location:", env.location)
print("World:", env.state)
print("Performance Score:", env.performance)