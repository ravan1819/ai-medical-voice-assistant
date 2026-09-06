# AI Medical Voice Assistant

An AI-powered healthcare application that converts Telugu patient speech into structured medical reports using Speech Recognition, Translation, Natural Language Processing (NLP), and automated report generation.

## Live Demo

Frontend:
https://mediaclreport.vercel.app/

Backend:
https://ai-medical-voice-assistant-1.onrender.com/

API Documentation:
https://ai-medical-voice-assistant-1.onrender.com/docs

## Project Overview

The AI Medical Voice Assistant is a full-stack Artificial Intelligence application designed to reduce the manual effort involved in documenting patient information.

Patients can speak about their symptoms in Telugu. The application processes the voice input, converts it into Telugu text, translates the text into English, extracts important medical information using NLP techniques, and generates a structured medical report.

## Basic Workflow

Patient Voice
↓
Speech Recognition
↓
Telugu Text
↓
Telugu to English Translation
↓
NLP Information Extraction
↓
Structured Medical Report
↓
PDF Report

## Problem Statement

In many rural and semi-urban healthcare environments, patients communicate primarily in regional languages such as Telugu.

Healthcare professionals may need to manually listen to patient information, record symptoms, translate information, and prepare medical documentation.

This can be time-consuming and may result in incomplete documentation.

The objective of this project is to develop an AI-based system that can automate the initial documentation process from patient speech.

## Proposed Solution

The system provides a web-based interface where users can:

1. Record Telugu patient speech using a microphone.
2. Upload an existing audio file.
3. Convert the audio into text using Speech Recognition.
4. Translate Telugu text into English.
5. Extract relevant medical information using NLP.
6. Generate a structured medical report.
7. Download the generated report as a PDF.

## System Architecture

```text
                 Patient
                    |
                    v
          Telugu Voice / Audio
                    |
                    v
        React + Vite Frontend
                    |
                    | Axios REST API
                    v
              FastAPI Backend
                    |
                    v
                  FFmpeg
             Audio Conversion
                    |
                    v
          Speech Recognition
                    |
                    v
              Telugu Text
                    |
                    v
          Google Translation
                    |
                    v
             English Text
                    |
                    v
          NLP Information
             Extraction
                    |
                    v
        Structured Medical Report
                    |
                    v
             JSON Response
                    |
                    v
          React Frontend
                    |
                    v
                jsPDF
                    |
                    v
              PDF Report
