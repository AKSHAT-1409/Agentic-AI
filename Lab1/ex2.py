import random


class CorridorEnvironment:

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

        elif action == "NoOp":
            pass

    def all_clean(self):
        return all(square == "Clean" for square in self.state)


class CorridorAgent:

    def __init__(self, n):
        self.n = n
        self.direction = "Right"

    def program(self, percept):

        location, status = percept

        # Clean current square if dirty
        if status == "Dirty":
            return "Suck"

        # Move in corridor
        if self.direction == "Right":

            if location == self.n - 1:
                self.direction = "Left"
                return "Left"

            return "Right"

        else:

            if location == 0:
                self.direction = "Right"
                return "Right"

            return "Left"


# ----------------------------
# Main Program
# ----------------------------

N = 5

env = CorridorEnvironment(N)
agent = CorridorAgent(N)

print("=" * 50)
print("1 × N Vacuum Cleaner World")
print("=" * 50)

print("Initial State")
print(env.state)
print()

step = 1

while not env.all_clean():

    percept = env.percept()
    action = agent.program(percept)

    print(f"Step {step}")
    print("Location :", percept[0])
    print("Status   :", percept[1])
    print("Action   :", action)

    env.execute(action)

    print("World    :", env.state)
    print("Performance :", env.performance)
    print("-" * 40)

    step += 1

print("\nAll squares are clean.")
print("Final State :", env.state)
print("Final Performance Score :", env.performance)