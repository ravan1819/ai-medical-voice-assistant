import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {

  const [file, setFile] = useState(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [recording, setRecording] = useState(false);

  const mediaRecorderRef = useRef(null);

  const audioChunksRef = useRef([]);

  // =========================
  // RECORD AUDIO
  // =========================

  const startRecording = async () => {

    // STOP RECORDING

    if (recording && mediaRecorderRef.current) {

      mediaRecorderRef.current.stop();

      setRecording(false);

      return;
    }

    try {

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {

        if (event.data.size > 0) {

          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {

        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        const audioFile = new File(
          [audioBlob],
          "recording.webm",
          {
            type: "audio/webm",
          }
        );

        console.log(audioFile);

        setFile(audioFile);

        alert("Recording completed successfully!");
      };

      mediaRecorder.start();

      setRecording(true);

      alert("Recording started... Speak now");

    } catch (error) {

      console.log(error);

      alert("Microphone permission denied");
    }
  };

  // =========================
  // GENERATE REPORT
  // =========================

  const handleUpload = async () => {

    if (!file) {

      alert("Please record or upload audio first");

      return;
    }

    try {

      setLoading(true);

      const formData = new FormData();

      formData.append("file", file);

      console.log(file);

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/process-audio`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log(response.data);

      setResult(response.data);

      setLoading(false);

   } catch (error) {

  console.log(error);

  console.log(error.response);

  alert(
    error.response?.data?.error ||
    "Backend Processing Failed"
  );

  setLoading(false);
}
  };

  return (

    <div className="min-h-screen bg-slate-100">

      {/* HERO SECTION */}

      <div className="bg-gradient-to-r from-blue-900 via-cyan-700 to-blue-500 text-white py-28 px-6 text-center shadow-2xl">

        <h1 className="text-6xl font-extrabold mb-8 tracking-wide">
          AI Medical Voice Assistant
        </h1>

        <p className="text-2xl max-w-5xl mx-auto leading-relaxed text-slate-100">
          Transform Telugu patient speech into structured medical reports
          using Artificial Intelligence, NLP and Speech Recognition.
        </p>

        <div className="mt-10 flex flex-wrap justify-center gap-5">

          <div className="bg-white/20 backdrop-blur-md px-8 py-4 rounded-2xl text-xl font-semibold shadow-xl">
            NLP Powered
          </div>

          <div className="bg-white/20 backdrop-blur-md px-8 py-4 rounded-2xl text-xl font-semibold shadow-xl">
            Healthcare AI
          </div>

          <div className="bg-white/20 backdrop-blur-md px-8 py-4 rounded-2xl text-xl font-semibold shadow-xl">
            Speech Recognition
          </div>
        </div>
      </div>

      {/* FEATURES */}

      <div className="max-w-7xl mx-auto px-6 py-20">

        <h2 className="text-5xl font-bold text-center mb-16 text-slate-800">
          Project Features
        </h2>

        <div className="grid md:grid-cols-3 gap-10">

          <div className="bg-white rounded-3xl p-10 shadow-2xl border-t-8 border-blue-600">

            <h3 className="text-3xl font-bold mb-6 text-blue-700">
              Voice Recording
            </h3>

            <p className="text-xl text-gray-600 leading-relaxed">
              Record Telugu patient speech directly from browser.
            </p>
          </div>

          <div className="bg-white rounded-3xl p-10 shadow-2xl border-t-8 border-green-600">

            <h3 className="text-3xl font-bold mb-6 text-green-700">
              AI Translation
            </h3>

            <p className="text-xl text-gray-600 leading-relaxed">
              Convert Telugu speech into English text automatically.
            </p>
          </div>

          <div className="bg-white rounded-3xl p-10 shadow-2xl border-t-8 border-red-600">

            <h3 className="text-3xl font-bold mb-6 text-red-700">
              Medical Report
            </h3>

            <p className="text-xl text-gray-600 leading-relaxed">
              Generate structured medical reports using NLP.
            </p>
          </div>
        </div>
      </div>

      {/* MAIN APP */}

      <div className="max-w-6xl mx-auto px-6 pb-20">

        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">

          {/* HEADER */}

          <div className="bg-slate-900 text-white p-12 text-center">

            <h2 className="text-5xl font-bold mb-5">
              Smart Medical Report Generator
            </h2>

            <p className="text-2xl text-slate-300">
              Upload or record Telugu patient audio
            </p>
          </div>

          {/* CONTENT */}

          <div className="p-12">

            {/* RECORD BUTTON */}

            <div className="text-center mb-12">

              <button
                onClick={startRecording}
                className={`px-14 py-5 rounded-2xl text-2xl font-bold shadow-2xl transition-all duration-300 ${
                  recording
                    ? "bg-red-800 text-white"
                    : "bg-red-600 hover:bg-red-700 text-white"
                }`}
              >

                {recording
                  ? "⏹ Stop Recording"
                  : "🎤 Start Voice Recording"}

              </button>

              <p className="mt-5 text-xl text-gray-500">
                Click again to stop recording
              </p>
            </div>

            {/* FILE UPLOAD */}

            <div className="bg-slate-50 border-2 border-dashed border-blue-300 rounded-3xl p-10 mb-12">

              <h3 className="text-3xl font-bold text-center mb-8 text-slate-700">
                Upload Audio File
              </h3>

              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full border p-5 rounded-2xl bg-white text-lg shadow-sm"
              />
            </div>

            {/* GENERATE BUTTON */}

            <div className="text-center mb-16">

              <button
                onClick={handleUpload}
                className="bg-blue-700 hover:bg-blue-800 transition-all duration-300 text-white px-16 py-5 rounded-2xl text-2xl font-bold shadow-2xl"
              >

                {loading
                  ? "Processing Audio..."
                  : "Generate Medical Report"}

              </button>
            </div>

            {/* RESULTS */}

            {result && (

              <div className="space-y-10">

                {/* TELUGU */}

                <div className="bg-blue-50 border-l-8 border-blue-700 rounded-3xl p-10 shadow-xl">

                  <h2 className="text-4xl font-bold mb-6 text-blue-800">
                    Telugu Transcript
                  </h2>

                  <p className="text-2xl leading-relaxed text-slate-700">
                    {result.telugu_text}
                  </p>
                </div>

                {/* ENGLISH */}

                <div className="bg-green-50 border-l-8 border-green-700 rounded-3xl p-10 shadow-xl">

                  <h2 className="text-4xl font-bold mb-6 text-green-800">
                    English Translation
                  </h2>

                  <p className="text-2xl leading-relaxed text-slate-700">
                    {result.english_translation}
                  </p>
                </div>

                {/* REPORT */}

                <div className="bg-red-50 border-l-8 border-red-700 rounded-3xl p-10 shadow-xl">

                  <h2 className="text-4xl font-bold mb-6 text-red-800">
                    Medical Report
                  </h2>

                  <pre className="whitespace-pre-wrap text-xl leading-relaxed bg-white p-8 rounded-2xl overflow-auto shadow-inner">

                    {result.medical_report}

                  </pre>
                </div>
              </div>
            )}

            {/* TECHNOLOGIES */}

            <div className="mt-20">

              <h2 className="text-5xl font-bold text-center mb-14 text-slate-800">
                Technologies Used
              </h2>

              <div className="grid md:grid-cols-4 gap-8">

                <div className="bg-blue-50 rounded-3xl p-8 text-center shadow-xl border-b-8 border-blue-600">
                  <h3 className="text-3xl font-bold text-blue-700">
                    React
                  </h3>

                  <p className="mt-5 text-lg text-gray-600">
                    Frontend UI Development
                  </p>
                </div>

                <div className="bg-green-50 rounded-3xl p-8 text-center shadow-xl border-b-8 border-green-600">
                  <h3 className="text-3xl font-bold text-green-700">
                    FastAPI
                  </h3>

                  <p className="mt-5 text-lg text-gray-600">
                    Backend API Services
                  </p>
                </div>

                <div className="bg-red-50 rounded-3xl p-8 text-center shadow-xl border-b-8 border-red-600">
                  <h3 className="text-3xl font-bold text-red-700">
                    NLP
                  </h3>

                  <p className="mt-5 text-lg text-gray-600">
                    Medical Information Extraction
                  </p>
                </div>

                <div className="bg-purple-50 rounded-3xl p-8 text-center shadow-xl border-b-8 border-purple-600">
                  <h3 className="text-3xl font-bold text-purple-700">
                    Speech AI
                  </h3>

                  <p className="mt-5 text-lg text-gray-600">
                    Telugu Speech Recognition
                  </p>
                </div>
              </div>
            </div>

            {/* ABOUT DEVELOPER */}

            <div className="mt-24 bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-3xl p-14 shadow-2xl text-center">

              <h2 className="text-5xl font-bold mb-10">
                About Developer
              </h2>

              <h3 className="text-4xl font-bold mb-5 text-cyan-300">
                Sravani Ramadugu
              </h3>

              <p className="text-2xl text-slate-300 mb-8">
                Data Science & NLP Enthusiast
              </p>

              <p className="text-xl leading-relaxed max-w-5xl mx-auto text-slate-200">
                This AI Medical Voice Assistant project was developed using
                FastAPI, React, NLP, Speech Recognition and Translation AI.
              </p>

              <div className="mt-10 text-2xl font-semibold text-cyan-300">
                📧 sravaniramadugu123@gmail.com
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* FOOTER */}

      <footer className="bg-slate-950 text-white text-center py-14">

        <h2 className="text-4xl font-bold mb-5">
          AI Medical Voice Assistant
        </h2>

        <p className="text-2xl text-slate-300">
          Developed by Sravani Ramadugu
        </p>

      </footer>
    </div>
  );
}

export default App;