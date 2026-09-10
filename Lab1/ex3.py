import random


class DynamicVacuumEnvironment:

    def __init__(self, n):
        self.n = n

        # Random initial state
        self.state = [
            random.choice(["Dirty", "Clean"])
            for _ in range(n)
        ]

        self.location = 0
        self.performance = 0

    def percept(self):
        return (self.location, self.state[self.location])

    def execute(self, action):

        # Perform action
        if action == "Suck":
            if self.state[self.location] == "Dirty":
                self.state[self.location] = "Clean"
                self.performance += 10

        elif action == "Right":
            if self.location < self.n - 1:
                self.location += 1
                self.performance -= 1

        elif action == "Left":
            if self.location > 0:
                self.location -= 1
                self.performance -= 1

        # Dirt reappears with probability 0.1
        if random.random() < 0.1:
            index = random.randint(0, self.n - 1)
            self.state[index] = "Dirty"
            print(f"*** Dirt reappeared at location {index} ***")


class ReflexAgent:

    def __init__(self, n):
        self.n = n
        self.direction = "Right"

    def program(self, percept):

        location, status = percept

        # Clean if dirty
        if status == "Dirty":
            return "Suck"

        # Move right
        if self.direction == "Right":

            if location == self.n - 1:
                self.direction = "Left"
                return "Left"

            return "Right"

        # Move left
        else:

            if location == 0:
                self.direction = "Right"
                return "Right"

            return "Left"


# ----------------------------
# Main Program
# ----------------------------

N = 5
STEPS = 20

env = DynamicVacuumEnvironment(N)
agent = ReflexAgent(N)

print("=" * 55)
print("Dynamic Vacuum Cleaner World")
print("=" * 55)

print("Initial State")
print(env.state)
print()

for step in range(1, STEPS + 1):

    percept = env.percept()
    action = agent.program(percept)

    print(f"Step {step}")
    print("Location :", percept[0])
    print("Status   :", percept[1])
    print("Action   :", action)

    env.execute(action)

    print("World    :", env.state)
    print("Performance :", env.performance)
    print("-" * 45)

print("\nFinal State :", env.state)
print("Final Performance Score :", env.performance)