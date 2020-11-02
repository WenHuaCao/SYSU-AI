from pomegranate import *

PatientAge = DiscreteDistribution(
    {
        "0-30": 0.1, 
        "31-65": 0.3, 
        "65+": 0.6
    }
)

CTScanResult = DiscreteDistribution(
    {
        "Ischemic Stroke": 0.7,
        "Hemmorraghic Stroke": 0.3
    }
)

MRIScanResult = DiscreteDistribution(
    {
        "Ischemic Stroke": 0.7,
        "Hemmorraghic Stroke": 0.3
    }
)

Anticoagulants = DiscreteDistribution(
    {
        "Used": 0.5,
        "Not Used": 0.5
    }
)

StrokeType = ConditionalProbabilityTable(
    [
        ["Ischemic Stroke",     "Ischemic Stroke",      "Ischemic Stroke", 0.8],
        ["Ischemic Stroke",     "Hemmorraghic Stroke",  "Ischemic Stroke", 0.5],
        ["Hemmorraghic Stroke", "Ischemic Stroke",      "Ischemic Stroke", 0.5],
        ["Hemmorraghic Stroke", "Hemmorraghic Stroke",  "Ischemic Stroke", 0], 

        ["Ischemic Stroke",     "Ischemic Stroke",      "Hemmorraghic Stroke", 0],
        ["Ischemic Stroke",     "Hemmorraghic Stroke",  "Hemmorraghic Stroke", 0.4], 
        ["Hemmorraghic Stroke", "Ischemic Stroke",      "Hemmorraghic Stroke", 0.4],
        ["Hemmorraghic Stroke", "Hemmorraghic Stroke",  "Hemmorraghic Stroke", 0.9],

        ["Ischemic Stroke",     "Ischemic Stroke",      "Stroke Mimic", 0.2],
        ["Ischemic Stroke",     "Hemmorraghic Stroke",  "Stroke Mimic", 0.1],   
        ["Hemmorraghic Stroke", "Ischemic Stroke",      "Stroke Mimic", 0.1],
        ["Hemmorraghic Stroke", "Hemmorraghic Stroke",  "Stroke Mimic", 0.1]
    ], [CTScanResult, MRIScanResult]
)

Mortality = ConditionalProbabilityTable(
    [
        ["Ischemic Stroke",     "Used",     "False", 0.28],
        ["Hemmorraghic Stroke", "Used",     "False", 0.99],
        ["Stroke Mimic",        "Used",     "False", 0.1],
        ["Ischemic Stroke",     "Not Used", "False", 0.56],
        ["Hemmorraghic Stroke", "Not Used", "False", 0.58],
        ["Stroke Mimic",        "Not Used", "False", 0.05],

        ["Ischemic Stroke",     "Used" ,    "True", 0.72],
        ["Hemmorraghic Stroke", "Used",     "True", 0.01],
        ["Stroke Mimic",        "Used",     "True", 0.9],
        ["Ischemic Stroke",     "Not Used", "True", 0.44],
        ["Hemmorraghic Stroke", "Not Used", "True", 0.42],
        ["Stroke Mimic",        "Not Used", "True", 0.95]
    ], [StrokeType, Anticoagulants]
)

Disability = ConditionalProbabilityTable(
    [
        ["Ischemic Stroke",     "0-30",  "Negligible", 0.80],
        ["Hemmorraghic Stroke", "0-30",  "Negligible", 0.70],
        ["Stroke Mimic",        "0-30",  "Negligible", 0.9],
        ["Ischemic Stroke",     "31-65", "Negligible", 0.60],
        ["Hemmorraghic Stroke", "31-65", "Negligible", 0.50],
        ["Stroke Mimic",        "31-65", "Negligible", 0.4],
        ["Ischemic Stroke",     "65+"  , "Negligible", 0.30],
        ["Hemmorraghic Stroke", "65+"  , "Negligible", 0.20],
        ["Stroke Mimic",        "65+"  , "Negligible", 0.1],

        ["Ischemic Stroke",     "0-30" , "Moderate", 0.1],
        ["Hemmorraghic Stroke", "0-30" , "Moderate", 0.2],
        ["Stroke Mimic",        "0-30" , "Moderate", 0.05],
        ["Ischemic Stroke",     "31-65", "Moderate", 0.3],
        ["Hemmorraghic Stroke", "31-65", "Moderate", 0.4],
        ["Stroke Mimic",        "31-65", "Moderate", 0.3],
        ["Ischemic Stroke",     "65+"  , "Moderate", 0.4],
        ["Hemmorraghic Stroke", "65+"  , "Moderate", 0.2],
        ["Stroke Mimic",        "65+"  , "Moderate", 0.1],

        ["Ischemic Stroke",     "0-30" , "Severe", 0.1],
        ["Hemmorraghic Stroke", "0-30" , "Severe", 0.1],
        ["Stroke Mimic",        "0-30" , "Severe", 0.05],
        ["Ischemic Stroke",     "31-65", "Severe", 0.1],
        ["Hemmorraghic Stroke", "31-65", "Severe", 0.1],
        ["Stroke Mimic",        "31-65", "Severe", 0.3],
        ["Ischemic Stroke",     "65+"  , "Severe", 0.3],
        ["Hemmorraghic Stroke", "65+"  , "Severe", 0.6],
        ["Stroke Mimic",        "65+"  , "Severe", 0.8]
    ], [StrokeType, PatientAge]
)

PatientAge_state = State(PatientAge, name="PatientAge")
CTScanResult_state = State(CTScanResult, name="CTScanResult")
MRIScanResult_state = State(MRIScanResult, name="MRIScanResult")
Anticoagulants_state = State(Anticoagulants, name="Anticoagulants")
StrokeType_state = State(StrokeType, name="StrokeType")
Mortality_state = State(Mortality, name="Mortality")
Disability_state = State(Disability, name="Disability")

model = BayesianNetwork("Diagnosing")
model.add_states(PatientAge_state, CTScanResult_state, MRIScanResult_state, 
    Anticoagulants_state, StrokeType_state, Mortality_state, Disability_state)
model.add_transition(CTScanResult_state, StrokeType_state)
model.add_transition(MRIScanResult_state, StrokeType_state)
model.add_transition(StrokeType_state, Mortality_state)
model.add_transition(Anticoagulants_state, Mortality_state)
model.add_transition(StrokeType_state, Disability_state)
model.add_transition(PatientAge_state, Disability_state)
model.bake()

print("P(Mortality=\"True\" | PatientAge=\"31-65\" && CTScanResult=\"Ischemic Stroke\") = ", 
    model.predict_proba({"PatientAge": "31-65", "CTScanResult": "Ischemic Stroke"})[5].parameters[0]["True"])

print("P(Disability=\"Moderate\" | PatientAge=\"65+\" && MRIScanResult=\"Hemmorraghic Stroke\") = ", 
    model.predict_proba({"PatientAge": "65+", "MRIScanResult": "Hemmorraghic Stroke"})[6].parameters[0]["Moderate"])

print("P(StrokeType=\"Stroke Mimic\" | PatientAge=\"65+\" && CTScanResult=\"Hemmorraghic Stroke\" && MRIScanResult=\"Ischemic Stroke\") = ",
    model.predict_proba({"PatientAge": "65+", "CTScanResult": "Hemmorraghic Stroke", "MRIScanResult": "Ischemic Stroke"})[4].parameters[0]["Stroke Mimic"])

print("P(Anticoagulants=\"Not Used\" | PatientAge=\"0-30\") = ", 
    model.predict_proba({"PatientAge": "0-30"})[3].parameters[0]["Not Used"])