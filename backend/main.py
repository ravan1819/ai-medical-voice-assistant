from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import speech_recognition as sr
from deep_translator import GoogleTranslator

import shutil
import os
import re
import subprocess
import spacy

from pymongo import MongoClient

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MONGODB CONNECTION
# ==========================================

MONGO_URL = "mongodb+srv://sravani:Sravani%40123@cluster0.anzwhzn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URL)

db = client["medical_ai_db"]

collection = db["patient_reports"]

# ==========================================
# LOAD NLP MODEL
# ==========================================

nlp = spacy.load("en_core_web_sm")

# ==========================================
# NUMBER WORDS
# ==========================================

number_words = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}

# ==========================================
# EXTRACT INFO
# ==========================================

def extract_info(text):

    slots = {
        "name": "Not mentioned",
        "age": "Not mentioned",
        "gender": "Not mentioned",
        "symptoms": [],
        "duration": "Not mentioned",
        "medical_history": [],
        "family_history": [],
        "medications": [],
        "allergies": [],
        "social_history": [],
        "pain_score": "Not mentioned",
    }

    text_lower = text.lower()

    # ==========================================
    # NAME EXTRACTION
    # ==========================================

    name_patterns = [
        r"my name is ([a-zA-Z]+)",
        r"this is ([a-zA-Z]+)",
        r"name is ([a-zA-Z]+)",
        r"name of patient is ([a-zA-Z]+)"
    ]

    for pattern in name_patterns:

        match = re.search(pattern, text_lower)

        if match:

            slots["name"] = match.group(1).capitalize()

            break

    # ==========================================
    # AGE EXTRACTION
    # ==========================================

    age_patterns = [
        r"(\d+)\s*years old",
        r"(\d+)\s*year old",
        r"age is (\d+)",
        r"age (\d+)",
        r"aged (\d+)",
        r"of age (\d+)"
    ]

    for pattern in age_patterns:

        match = re.search(pattern, text_lower)

        if match:

            slots["age"] = match.group(1)

            break

    # ==========================================
    # GENDER EXTRACTION
    # ==========================================

    if any(word in text_lower for word in [
        "female",
        "woman",
        "girl"
    ]):

        slots["gender"] = "Female"

    elif any(word in text_lower for word in [
        "male",
        "man",
        "boy"
    ]):

        slots["gender"] = "Male"

    # ==========================================
    # SYMPTOMS EXTRACTION
    # ==========================================

    symptom_rules = {
        "fever": ["fever"],
        "cold": ["cold"],
        "cough": ["cough"],
        "headache": ["headache"],
        "body pain": ["body pain", "body ache", "pains"],
        "stomach pain": [
            "stomach ache",
            "stomach pain",
            "stomachache",
            "abdominal pain"
        ],
        "weakness": ["weak", "weakness"],
        "fatigue": ["tired", "fatigue"],
        "loss of appetite": [
            "loss of appetite",
            "appetite loss",
            "lost my appetite",
            "appetite decreased"
        ],
        "vomiting": ["vomiting"],
        "nausea": ["nausea"],
        "dizziness": ["dizziness"],
        "chest pain": ["chest pain"],
        "back pain": ["back pain"],
        "throat pain": ["throat pain", "sore throat"],
        "breathing difficulty": [
            "breathing difficulty",
            "breathlessness"
        ],
        "diarrhea": ["diarrhea"],
        "constipation": ["constipation"],
    }

    for symptom, keywords in symptom_rules.items():

        for keyword in keywords:

            if keyword in text_lower:

                slots["symptoms"].append(symptom)

                break

    # ==========================================
    # DURATION EXTRACTION
    # ==========================================

    duration_patterns = [
        r"for (\w+ days)",
        r"for the past (\w+ days)",
        r"for past (\w+ days)",
        r"past (\w+ days)",
        r"for last (\w+ days)",
        r"since (\w+ days)",
        r"for (\w+ weeks)",
        r"for (\w+ months)",
        r"since (\w+ weeks)",
        r"since (\w+ months)"
    ]

    for pattern in duration_patterns:

        match = re.search(pattern, text_lower)

        if match:

            slots["duration"] = match.group(1)

            break

    # ==========================================
    # MEDICAL HISTORY
    # ==========================================

    disease_keywords = [
        "diabetes",
        "hypertension",
        "bp",
        "asthma",
        "thyroid",
        "heart disease",
        "cancer",
        "tuberculosis",
        "covid",
        "arthritis",
        "migraine",
        "kidney disease",
        "liver disease",
        "chicken pox",
    ]

    for disease in disease_keywords:

        if disease in text_lower:

            slots["medical_history"].append(disease)

    # ==========================================
    # FAMILY HISTORY
    # ==========================================

    family_patterns = [
        r"father has ([a-zA-Z ]+)",
        r"mother has ([a-zA-Z ]+)",
        r"my father has ([a-zA-Z ]+)",
        r"my mother has ([a-zA-Z ]+)",
        r"family history of ([a-zA-Z ]+)"
    ]

    for pattern in family_patterns:

        matches = re.findall(pattern, text_lower)

        for m in matches:

            cleaned = m.strip()

            if len(cleaned) > 2:

                slots["family_history"].append(cleaned)

    # ==========================================
    # MEDICATIONS
    # ==========================================

    medication_patterns = [
        r"taking ([a-zA-Z0-9 ]+)",
        r"using ([a-zA-Z0-9 ]+)",
        r"on ([a-zA-Z0-9 ]+) medication",
    ]

    for pattern in medication_patterns:

        match = re.search(pattern, text_lower)

        if match:

            medicine = match.group(1).strip()

            slots["medications"].append(medicine)

    # ==========================================
    # ALLERGIES
    # ==========================================

    allergy_patterns = [
        r"allergic to ([a-zA-Z ]+?)(?: i have| pain|$)",
        r"allergy to ([a-zA-Z ]+?)(?: i have| pain|$)",
    ]

    for pattern in allergy_patterns:

        match = re.search(pattern, text_lower)

        if match:

            allergy_text = match.group(1).strip()

            allergy_text = allergy_text.replace("and", "").strip()

            slots["allergies"].append(allergy_text)

    # ==========================================
    # SOCIAL HISTORY
    # ==========================================

    if any(word in text_lower for word in [
        "smoke",
        "smoking",
        "cigarette",
        "cigarettes",
        "tobacco"
    ]):

        slots["social_history"].append("Smoking")

    if any(word in text_lower for word in [
        "alcohol",
        "drink",
        "drinking"
    ]):

        slots["social_history"].append("Alcohol consumption")

    if "drug" in text_lower:

        slots["social_history"].append("Drug use")

    # ==========================================
    # PAIN SCORE EXTRACTION
    # ==========================================

    pain_patterns = [
        r"pain score is (\w+)",
        r"pain level is (\w+)",
        r"pain score (\w+)",
        r"pain scale (\w+)",
    ]

    for pattern in pain_patterns:

        match = re.search(pattern, text_lower)

        if match:

            pain_value = match.group(1)

            if pain_value.isdigit():

                slots["pain_score"] = pain_value + "/10"

            elif pain_value in number_words:

                slots["pain_score"] = (
                    number_words[pain_value] + "/10"
                )

    if "seven out of ten" in text_lower:
        slots["pain_score"] = "7/10"

    elif "eight out of ten" in text_lower:
        slots["pain_score"] = "8/10"

    elif "eight on the pain scale" in text_lower:
        slots["pain_score"] = "8/10"

    elif "nine out of ten" in text_lower:
        slots["pain_score"] = "9/10"

    # ==========================================
    # CLEANUP
    # ==========================================

    for key in slots:

        if isinstance(slots[key], list):

            if len(slots[key]) == 0:

                slots[key] = "Not mentioned"

            else:

                slots[key] = ", ".join(
                    list(set(slots[key]))
                )

    return slots

# ==========================================
# GENERATE REPORT
# ==========================================

def generate_report(slots):

    report = f'''
🩺 PATIENT MEDICAL REPORT
==================================================

👤 Patient Name:
{slots["name"]}

🎂 Age:
{slots["age"]}

⚧ Gender:
{slots["gender"]}

🤒 Symptoms:
{slots["symptoms"]}

⏳ Duration:
{slots["duration"]}

🏥 Medical History:
{slots["medical_history"]}

👨‍👩‍👧 Family History:
{slots["family_history"]}

💊 Medications:
{slots["medications"]}

⚠ Allergies:
{slots["allergies"]}

🍺 Social History:
{slots["social_history"]}

📊 Pain Score:
{slots["pain_score"]}

==================================================
'''

    return report

# ==========================================
# ROOT API
# ==========================================

@app.get("/")

def home():

    return {
        "message": "AI Medical Voice Assistant Backend Running"
    }

# ==========================================
# PROCESS AUDIO API
# ==========================================

@app.post("/process-audio")

async def process_audio(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    wav_path = "converted.wav"

    try:

        # SAVE AUDIO FILE

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(file.file, buffer)

        # CONVERT TO WAV

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i",
            file_path,
            wav_path
        ])

        recognizer = sr.Recognizer()

        # SPEECH RECOGNITION

        with sr.AudioFile(wav_path) as source:

            audio_data = recognizer.record(source)

            telugu_text = recognizer.recognize_google(
                audio_data,
                language="te-IN"
            )

        # TRANSLATION

        english_translation = GoogleTranslator(
            source='te',
            target='en'
        ).translate(telugu_text)

        # EXTRACT INFORMATION

        slots = extract_info(
            english_translation
        )

        # GENERATE REPORT

        medical_report = generate_report(
            slots
        )

        # SAVE TO DATABASE

        patient_data = {
            "telugu_text": telugu_text,
            "english_translation": english_translation,
            "medical_report": medical_report
        }

        collection.insert_one(patient_data)

        # DELETE TEMP FILES

        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        return {
            "telugu_text": telugu_text,
            "english_translation": english_translation,
            "medical_report": medical_report
        }

    except Exception as e:

        print(str(e))

        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        return {
            "error": str(e)
        }