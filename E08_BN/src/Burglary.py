from pomegranate import *

Burglary = DiscreteDistribution({"B": 0.001, "~B": 0.999})
Earthquake = DiscreteDistribution({"E": 0.002, "~E": 0.998})

Alarm = ConditionalProbabilityTable(
    [
        ["B", "E", "A", 0.95],
        ["B", "E", "~A", 0.05],
        ["B", "~E", "A", 0.94],
        ["B", "~E", "~A", 0.06],
        ["~B", "E", "A", 0.29],
        ["~B", "E", "~A", 0.71],
        ["~B", "~E", "A", 0.001],
        ["~B", "~E", "~A", 0.999]
    ], [Burglary, Earthquake]
)

JohnCalls = ConditionalProbabilityTable(
    [
        ["A", "J", 0.9],
        ["A", "~J", 0.1],
        ["~A", "J", 0.05],
        ["~A", "~J", 0.95]
    ], [Alarm]
)

MaryCalls = ConditionalProbabilityTable(
    [
        ["A", "M", 0.7],
        ["A", "~M", 0.3],
        ["~A", "M", 0.01],
        ["~A", "~M", 0.99]
    ], [Alarm]
)

Burglary_state = State(Burglary, name="Burglary")
Earthquake_state = State(Earthquake, name="Earthquake")
Alarm_state = State(Alarm, name="Alarm")
JohnCalls_state = State(JohnCalls, name="JohnCalls")
MaryCalls_state = State(MaryCalls, name="MaryCalls")

model = BayesianNetwork("Burglary")
model.add_states(Burglary_state, Earthquake_state, Alarm_state, 
    JohnCalls_state, MaryCalls_state)
model.add_transition(Burglary_state, Alarm_state)
model.add_transition(Earthquake_state, Alarm_state)
model.add_transition(Alarm_state, JohnCalls_state)
model.add_transition(Alarm_state, MaryCalls_state)
model.bake()

print("P(A) = ", model.predict_proba({})[2].parameters[0]["A"])

print("P(J && ~M) = ", model.predict_proba({})[3].parameters[0]["J"] * 
    model.predict_proba({})[4].parameters[0]["~M"])

print("P(A | J && ~M) = ", model.predict_proba({"JohnCalls": "J", 
    "MaryCalls": "~M"})[2].parameters[0]["A"])

print("P(B | A) = ", model.predict_proba({"Alarm": "A"})[0].parameters[0]["B"])

print("P(B | J && ~M) = ", model.predict_proba({"JohnCalls": "J", 
    "MaryCalls": "~M"})[0].parameters[0]["B"])

print("P(J && ~M | ~B) = ", model.predict_proba({"Burglary": "~B"})[3].parameters[0]["J"] * 
    model.predict_proba({"Burglary": "~B", "JohnCalls": "J"})[4].parameters[0]["~M"])