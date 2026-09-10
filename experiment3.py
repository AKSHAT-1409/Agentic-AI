import json
import math
import csv
from datetime import datetime


# =========================
# 1. TOOLS
# =========================

def calculator(expression):
    allowed = {"sqrt": math.sqrt, "pow": pow, "pi": math.pi}
    return eval(expression, {"__builtins__": {}}, allowed)


def days_between(d1, d2):
    a = datetime.strptime(d1, "%Y-%m-%d")
    b = datetime.strptime(d2, "%Y-%m-%d")
    return abs((b - a).days)


def unit_convert(value, frm, to):
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x / 0.621371,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x / 2.20462,
        ("C", "F"): lambda x: x * 9 / 5 + 32,
        ("F", "C"): lambda x: (x - 32) * 5 / 9
    }

    if (frm, to) not in conversions:
        raise ValueError("Unsupported conversion")

    return conversions[(frm, to)](value)


# =========================
# 2. TOOL SCHEMAS
# =========================

schemas = [
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression.",
        "arguments": {"expression": "string"}
    },
    {
        "name": "days_between",
        "description": "Return days between two dates.",
        "arguments": {"d1": "string", "d2": "string"}
    },
    {
        "name": "unit_convert",
        "description": "Convert supported units.",
        "arguments": {
            "value": "number",
            "frm": "string",
            "to": "string"
        }
    }
]


# =========================
# 3. TOOL REGISTRY
# =========================

registry = {
    "calculator": calculator,
    "days_between": days_between,
    "unit_convert": unit_convert
}


# =========================
# 4. DISPATCH
# =========================

def dispatch(call):
    try:
        request = json.loads(call)

        name = request["name"]
        args = request["arguments"]

        if name not in registry:
            return {
                "status": "error",
                "error": f"Unknown tool: {name}"
            }

        result = registry[name](**args)

        return {
            "status": "success",
            "tool": name,
            "result": result
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Malformed JSON"
        }

    except TypeError as e:
        return {
            "status": "error",
            "error": f"Wrong arguments: {e}"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# =========================
# 5. MAIN EXPERIMENT
# =========================

print("TOOL SCHEMAS")
for s in schemas:
    print(json.dumps(s, indent=2))


calls = [
    {
        "name": "calculator",
        "arguments": {"expression": "10 + 5 * 2"}
    },
    {
        "name": "days_between",
        "arguments": {
            "d1": "2026-09-01",
            "d2": "2026-09-10"
        }
    },
    {
        "name": "unit_convert",
        "arguments": {
            "value": 10,
            "frm": "km",
            "to": "miles"
        }
    }
]

print("\nTOOL CALLS AND OBSERVATIONS")

for call in calls:
    call = json.dumps(call)
    print("\nCall:", call)
    print("Observation:", dispatch(call))


# =========================
# 6. EXERCISE 1
# =========================

print("\nEXERCISE 1: ERROR HANDLING")

errors = [
    '{"name": "calculator", "arguments":',
    json.dumps({"name": "weather", "arguments": {}}),
    json.dumps({
        "name": "calculator",
        "arguments": {"wrong": "10 + 5"}
    }),
    json.dumps({
        "name": "days_between",
        "arguments": {
            "d1": "hello",
            "d2": "world"
        }
    })
]

for error in errors:
    print("\nCall:", error)
    print("Observation:", dispatch(error))


# =========================
# 7. EXERCISE 2
# =========================

def csv_mean(file, column):
    with open(file, newline="") as f:
        rows = csv.DictReader(f)

        if column not in rows.fieldnames:
            raise ValueError("Column not found")

        values = [float(row[column]) for row in rows]

    return sum(values) / len(values)


registry["csv_mean"] = csv_mean

schemas.append({
    "name": "csv_mean",
    "description": "Return the mean of a named CSV column.",
    "arguments": {
        "file": "string",
        "column": "string"
    }
})


# Create sample CSV
with open("marks.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Marks"])
    writer.writerows([
        ["A", 80],
        ["B", 90],
        ["C", 70],
        ["D", 60]
    ])


call = json.dumps({
    "name": "csv_mean",
    "arguments": {
        "file": "marks.csv",
        "column": "Marks"
    }
})

print("\nEXERCISE 2")
print("Schema:", json.dumps(schemas[-1], indent=2))
print("Call:", call)
print("Observation:", dispatch(call))