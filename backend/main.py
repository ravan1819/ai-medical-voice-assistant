from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import speech_recognition as sr
from deep_translator import GoogleTranslator

import shutil
import os
import re
import subprocess

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

    # NAME

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

    # AGE

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

    # GENDER

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

    # SYMPTOMS

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
        "vomiting": ["vomiting"],
        "nausea": ["nausea"],
        "dizziness": ["dizziness"],
        "chest pain": ["chest pain"],
        "back pain": ["back pain"],
        "throat pain": ["throat pain", "sore throat"],
    }

    for symptom, keywords in symptom_rules.items():

        for keyword in keywords:

            if keyword in text_lower:

                slots["symptoms"].append(symptom)

                break

    # DURATION

    duration_patterns = [
        r"for (\w+ days)",
        r"for (\w+ weeks)",
        r"for (\w+ months)"
    ]

    for pattern in duration_patterns:

        match = re.search(pattern, text_lower)

        if match:

            slots["duration"] = match.group(1)

            break

    # PAIN SCORE

    pain_patterns = [
        r"pain score is (\w+)",
        r"pain level is (\w+)",
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

    # CLEANUP

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

# ==========================================
# PROCESS AUDIO API
# ==========================================

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"
    wav_path = "converted.wav"

    try:

        print("STEP 1: Saving audio")

        # SAVE FILE
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("STEP 2: Converting audio")

        # CONVERT AUDIO
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                file_path,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                wav_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("STEP 3: Loading recognizer")

        recognizer = sr.Recognizer()

        # READ AUDIO
        with sr.AudioFile(wav_path) as source:

            audio_data = recognizer.record(source)

        print("STEP 4: Speech recognition")

        telugu_text = recognizer.recognize_google(
            audio_data,
            language="te-IN"
        )

        print("STEP 5: Translation")

        # TRANSLATION
        english_translation = GoogleTranslator(
            source="te",
            target="en"
        ).translate(telugu_text)

        print("STEP 6: NLP Extraction")

        # NLP EXTRACTION
        slots = extract_info(english_translation)

        print("STEP 7: Report generation")

        # REPORT
        medical_report = generate_report(slots)

        print("STEP 8: Database save")


        # DELETE TEMP FILES
        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        print("STEP 9: Completed")

        return {
            "telugu_text": telugu_text,
            "english_translation": english_translation,
            "medical_report": medical_report
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "error": str(e)
        }
