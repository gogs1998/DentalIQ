"""
UK GDC Clinical Note-Taking Guidelines

Based on General Dental Council Standards for the Dental Team (2013)
and guidance on clinical record keeping.

Reference: https://www.gdc-uk.org/information-standards-guidance/standards-and-guidance/standards-for-the-dental-team
"""

# GDC Standards - What MUST be in clinical records
GDC_STANDARDS = """
GENERAL DENTAL COUNCIL - CLINICAL RECORD KEEPING STANDARDS

Clinical records must be:
1. Accurate and legible
2. Made at the time of treatment or as soon as possible afterwards
3. Contain sufficient detail to show the care provided
4. Include relevant clinical findings
5. Include diagnosis and treatment planning discussions
6. Record consent for treatment
7. Be updated when treatment is provided
8. Include information about risks and benefits discussed
9. Record any complications or adverse reactions

REQUIRED ELEMENTS FOR COMPLETE CLINICAL NOTES:

1. MEDICAL HISTORY
   - Must review and document at each visit
   - Any changes since last visit
   - Current medications
   - Allergies
   - Relevant medical conditions
   Example: "Medical history reviewed, no changes since last visit" OR "New medication: aspirin 75mg daily"

2. PATIENT COMPLAINT/PRESENTING COMPLAINT
   - Chief complaint in patient's own words
   - Duration and severity
   Example: "Patient complains of pain upper right first molar, sharp pain on biting, 3 days duration"

3. CLINICAL EXAMINATION
   - Extra-oral examination findings
   - Intra-oral soft tissue examination
   - Dental examination findings
   - Periodontal assessment where relevant
   Example: "Examined. Extra-oral: no abnormality detected. Intra-oral: mucosa normal. UR6 large carious cavity, occlusal surface, TTP"

4. SPECIAL TESTS
   - Vitality tests (hot, cold, EPT)
   - Percussion tests
   - Mobility assessment
   - Probing depths (if relevant)
   Example: "UR6 non-vital to cold test, TTP, no mobility"

5. RADIOGRAPHIC FINDINGS
   - Type of radiograph
   - Clinical justification (IR(ME)R requirement - MANDATORY in UK)
   - Findings
   Example: "Periapical radiograph UR6 justified by clinical presentation of non-vital tooth. Shows periapical radiolucency 5mm diameter"

6. DIAGNOSIS
   - Clear clinical diagnosis or working diagnosis
   - Differential diagnoses if applicable
   Example: "Diagnosis: Irreversible pulpitis UR6 with chronic apical periodontitis"

7. TREATMENT PLAN
   - Options discussed with patient
   - Recommended treatment
   - Alternative options mentioned
   - Costs discussed (if private/mixed practice)
   - Prognosis
   Example: "Treatment options discussed: root canal treatment vs extraction. Patient prefers to retain tooth. Plan: RCT UR6. Prognosis: good. Estimated cost £450 discussed and accepted"

8. CONSENT
   - Risks, benefits, alternatives discussed
   - Material risks explained
   - Patient understanding confirmed
   - Written consent obtained (for complex treatment)
   Example: "Risks of RCT discussed including: treatment failure, instrument fracture, perforation, post-operative pain. Patient understands and consents to proceed"

9. TREATMENT PROVIDED
   - Date and details of treatment
   - Materials used
   - Any complications
   - Post-operative instructions
   Example: "RCT UR6: Access cavity prepared under rubber dam, working length determined 21mm, canal shaped to size 40 .06 taper, obturation with gutta percha and AH Plus sealer. No complications. Post-op instructions given"

10. REVIEW/FOLLOW-UP
    - Review interval
    - What to monitor
    - When to return
    Example: "Review 6 months, assess periapical healing. Advised to return earlier if symptoms recur"
"""

# IR(ME)R Regulations - CRITICAL for UK compliance
IRMER_GUIDELINES = """
IONISING RADIATION (MEDICAL EXPOSURE) REGULATIONS 2017 - IR(ME)R

MANDATORY REQUIREMENTS FOR DENTAL RADIOGRAPHS:

Every radiograph must have:
1. CLINICAL JUSTIFICATION - Why is this radiograph necessary?
   - Must be recorded BEFORE exposure
   - Based on clinical history and examination
   - Generic phrases NOT acceptable ("routine check-up" is INVALID)

   VALID justifications:
   - "Justified by clinical symptoms of irreversible pulpitis UR6"
   - "Justified by clinical presentation of periapical swelling"
   - "Justified to assess bone levels due to periodontal pocketing >6mm"
   - "Justified by clinical caries visible on mesial surface requiring extent assessment"

   INVALID justifications:
   - "Routine"
   - "Regular check-up"
   - "Patient request"
   - "Insurance requirement"

2. CLINICAL EVALUATION - What did the radiograph show?
   - Must be recorded by a dentist
   - Findings documented
   - How it affected treatment planning

Example complete radiograph record:
"Periapical radiograph UR6 justified by clinical presentation of TTP and non-vitality on testing.
Clinical evaluation: Periapical radiolucency 5mm diameter associated with distal root apex.
Supports diagnosis of chronic apical periodontitis. Treatment plan: root canal treatment indicated."
"""

# Specialty-specific requirements
SPECIALTY_GUIDELINES = {
    "General Dentistry": """
- Document recall interval and justification
- Include BPE scores for adults
- Record caries risk assessment
- Document oral hygiene instruction given
""",

    "Orthodontics": """
- IOTN score documented
- Growth assessment recorded
- Treatment objectives clearly stated
- Retention plan documented
- Patient compliance noted
""",

    "Periodontics": """
- Full periodontal charting (6-point pocket depths)
- BPE scores
- Furcation involvement
- Mobility assessment
- Plaque and bleeding scores
- Oral hygiene instruction documented
""",

    "Endodontics": """
- Vitality test results documented
- Working length determination method
- Irrigation protocol used
- Obturation technique and materials
- Post-operative instructions specific to RCT
""",

    "Oral Surgery": """
- Indication for extraction documented
- Difficulty assessment
- Anaesthesia type and batch number
- Surgical technique
- Sutures placed (type and number)
- Post-operative instructions and warnings
""",

    "Prosthodontics": """
- Tooth preparation design
- Impression materials and technique
- Shade selection and method
- Provisional restoration details
- Laboratory used and technician name
- Try-in assessment and adjustments
"""
}

# Note structure templates
NOTE_STRUCTURE_TEMPLATE = """
IDEAL UK GDC-COMPLIANT CLINICAL NOTE STRUCTURE:

[DATE & TIME]
[PATIENT NAME/ID]

MEDICAL HISTORY: [Reviewed/Updated]
[Any changes or relevant conditions]

PRESENTING COMPLAINT: [Patient's chief complaint]
[Duration, severity, characteristics]

CLINICAL EXAMINATION:
Extra-oral: [Findings]
Intra-oral: [Soft tissues, mucosa]
Dental: [Specific findings]
[Special tests: vitality, percussion, mobility]

RADIOGRAPHIC FINDINGS: [If applicable]
[Type of radiograph + IR(ME)R justification + findings]

DIAGNOSIS: [Clinical diagnosis]

TREATMENT PLAN:
[Options discussed]
[Recommended treatment]
[Prognosis]
[Costs if applicable]

CONSENT: [Risks, benefits, alternatives discussed]

TREATMENT PROVIDED: [If treatment done same visit]
[Details, materials, complications]

FOLLOW-UP: [Review interval and instructions]

Examples of EXCELLENT vs POOR notes:

POOR NOTE (GDC Score: 30/100):
"pt c/o pain ul6, cavity seen, filling done"

IMPROVED NOTE (GDC Score: 70/100):
"Patient complains of pain upper left first molar. Clinical examination: UL6 large occlusal cavity, TTP.
Diagnosis: dental caries. Treatment: composite filling placed. Patient consented."

EXCELLENT NOTE (GDC Score: 95/100):
"Medical history reviewed, patient reports new medication: aspirin 75mg daily for cardiovascular prophylaxis. No other changes.

Presenting complaint: Patient complains of sharp pain upper left first molar on biting, 5 days duration, keeping awake at night.

Clinical examination: Extra-oral examination normal. Intra-oral soft tissues normal. UL6 large occlusal carious cavity extending to dentine, TTP++, vital to cold test, no mobility.

Radiographic findings: Bitewing radiograph UL6 justified by clinical presentation of deep caries to assess proximity to pulp. Shows carious lesion extending into inner third of dentine, pulp chamber not exposed.

Diagnosis: Deep dental caries UL6, reversible pulpitis.

Treatment plan discussed: Composite restoration vs indirect onlay. Patient prefers direct composite. Explained small risk of pulpal involvement requiring future RCT (estimated 10%). Private fee £120 discussed and accepted.

Consent: Risks explained including post-operative sensitivity, potential need for RCT if symptoms worsen, marginal leakage requiring replacement. Patient understands and consents.

Treatment provided: UL6 composite restoration. Carious tissue removed under rubber dam isolation. Calcium hydroxide liner placed over deep area. Etch and bond (Optibond FL), composite restoration (Tetric EvoCeram A2) placed in increments. Occlusion adjusted. No complications. Post-operative instructions: avoid hard foods 24 hours, use warm salt water rinses if sensitive.

Review: 6 months routine recall. Advised to return sooner if increased pain or sensitivity."
"""


def get_gdc_prompt_guidelines(user_profile: dict) -> str:
    """Generate personalized GDC guidelines based on user profile"""

    specialty = user_profile.get("specialty", "General Dentistry")
    practice_type = user_profile.get("practice_type", "Mixed")
    notation = user_profile.get("notation_system", "FDI")
    verbose = user_profile.get("verbose_notes", False)

    guidelines = f"""
UK GDC CLINICAL DOCUMENTATION STANDARDS

You are helping a {specialty} dentist in a {practice_type} practice.
Use {notation} tooth notation system.
Note style: {"Detailed and comprehensive" if verbose else "Concise but complete"}.

MANDATORY ELEMENTS (Must be present for GDC compliance):

1. MEDICAL HISTORY - "Medical history reviewed" as minimum
2. CLINICAL EXAMINATION - Findings described
3. DIAGNOSIS - Clear diagnosis or clinical impression
4. TREATMENT PLAN - What was discussed/recommended
5. CONSENT - Risks/benefits discussed and patient agreement

CRITICAL UK REQUIREMENT - IR(ME)R:
If ANY radiograph is mentioned (PA, BW, OPG, etc.), you MUST include:
- Clinical justification (NOT "routine")
- Valid reason: symptoms, clinical signs, treatment planning need
Example: "Periapical radiograph justified by clinical presentation of non-vital tooth"

SPECIALTY-SPECIFIC REQUIREMENTS:
{SPECIALTY_GUIDELINES.get(specialty, "")}

ABBREVIATION EXPANSION:
- pt → Patient
- c/o → complains of
- Mhx → Medical history
- O/E → On examination
- ttp → tender to percussion
- TTP → tender to percussion
- NAD → no abnormality detected
- WNL → within normal limits
- RCT → root canal treatment
"""

    # Add user's custom abbreviations
    custom_abbrevs = user_profile.get("custom_abbreviations", {})
    if custom_abbrevs:
        guidelines += "\n\nUSER'S CUSTOM ABBREVIATIONS:\n"
        for abbrev, expansion in custom_abbrevs.items():
            guidelines += f"- {abbrev} → {expansion}\n"

    return guidelines
