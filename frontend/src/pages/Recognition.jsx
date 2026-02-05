import { useState, useRef, useEffect, useCallback } from "react";
import {
  Camera,
  RefreshCw,
  ShieldCheck,
  User,
  UserX,
  AlertCircle,
  ArrowLeft,
  Globe,
  Zap,
  Fingerprint,
  Activity,
  ShieldAlert,
} from "lucide-react";
import api from "../services/api";
import { Link } from "react-router-dom";

const Recognition = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [lastRecognized, setLastRecognized] = useState({ id: null, time: 0 });
  const [attemptCount, setAttemptCount] = useState(0);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
        setError(null);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      setError(
        "Unable to access camera. Please ensure permissions are granted.",
      );
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || isProcessing) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append("file", file, "upload.jpg");

    try {
      const response = await api.post("/recognition/identify", formData);
      setRecognitionResult(response.data);
      setError(null);
    } catch (err) {
      console.error("Upload error:", err);
      setError("Failed to process uploaded image.");
    } finally {
      setIsProcessing(false);
      // Reset input
      event.target.value = "";
    }
  };

  const captureAndIdentify = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || isProcessing) return;

    const now = Date.now();
    if (
      recognitionResult?.identity === "known" &&
      recognitionResult?.staff_id === lastRecognized.id &&
      now - lastRecognized.time < 60000
    ) {
      console.log("Cooldown active for:", recognitionResult.name);
      return;
    }

    setIsProcessing(true);
    const context = canvasRef.current.getContext("2d");
    context.drawImage(videoRef.current, 0, 0, 640, 480);

    canvasRef.current.toBlob(
      async (blob) => {
        if (!blob) {
          setIsProcessing(false);
          return;
        }

        const formData = new FormData();
        formData.append("file", blob, "capture.jpg");

        try {
          const response = await api.post("/recognition/identify", formData);
          const data = response.data;

          setRecognitionResult(data);

          if (data.identity === "known") {
            setLastRecognized({ id: data.staff_id, time: Date.now() });
            setAttemptCount(0); // Reset failures on success
          } else {
            setAttemptCount((prev) => prev + 1);
          }

          setError(null);
        } catch (err) {
          console.error("Identification error:", err);
        } finally {
          setIsProcessing(false);
        }
      },
      "image/jpeg",
      0.8,
    );
  }, [isProcessing, recognitionResult, lastRecognized]);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  useEffect(() => {
    let interval;
    if (isCameraActive && !isProcessing) {
      interval = setInterval(() => {
        captureAndIdentify();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [isCameraActive, isProcessing, captureAndIdentify]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden">
      {/* Ambient Background Elements */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] -mr-64 -mt-64" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] -ml-64 -mb-64" />

      {/* Header */}
      <header className="glass-morphism border-b border-white/5 p-6 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center border border-white/10 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </Link>
            <div className="h-6 w-px bg-white/10 mx-2" />
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center border border-blue-500/30">
                <Zap className="w-5 h-5 text-blue-400" />
              </div>
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                Sentinel Vision
              </h1>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <div className="flex items-center gap-2 px-4 py-1.5 bg-green-500/10 rounded-full border border-green-500/20">
              <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
              <span className="text-[10px] font-bold uppercase tracking-widest text-green-400">
                System Active
              </span>
            </div>
            <div className="flex items-center gap-2 text-slate-400"></div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col lg:flex-row p-6 lg:p-12 gap-8 items-center justify-center max-w-7xl mx-auto w-full">
        {/* Camera Feed Section */}
        <div className="relative group w-full lg:flex-1 aspect-video bg-slate-900 rounded-3xl border border-white/10 overflow-hidden shadow-2xl ring-1 ring-white/5">
          {!isCameraActive && !error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 z-20 backdrop-blur-sm">
              <Camera className="w-20 h-20 text-slate-700 mb-6 animate-pulse" />
              <button
                onClick={startCamera}
                className="btn-primary px-8 h-12 rounded-2xl shadow-lg shadow-blue-900/40"
              >
                <RefreshCw className="w-5 h-5" /> Initialize Optical Sensor
              </button>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/90 z-20 backdrop-blur-md">
              <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mb-6 border border-red-500/20">
                <AlertCircle className="w-10 h-10 text-red-500" />
              </div>
              <p className="text-red-400 mb-8 px-6 text-center font-semibold text-lg">
                {error}
              </p>

              <div className="flex gap-4">
                <button
                  onClick={startCamera}
                  className="px-8 h-12 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl font-bold transition-all active:scale-95"
                >
                  Retry Camera
                </button>

                <label className="px-8 h-12 bg-blue-600 hover:bg-blue-500 rounded-2xl font-bold flex items-center justify-center cursor-pointer transition-all active:scale-95 shadow-lg shadow-blue-900/40">
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                  Upload Photo Manual
                </label>
              </div>
            </div>
          )}

          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className={`w-full h-full object-cover transition-opacity duration-1000 ${!isCameraActive ? "opacity-0" : "opacity-100"}`}
          />
          <canvas ref={canvasRef} width="640" height="480" className="hidden" />

          {/* Futuristic HUD Overlay */}
          <div className="absolute inset-0 pointer-events-none z-10 border-[16px] border-transparent p-4">
            {/* Corners */}
            <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-blue-500/50 rounded-tl-2xl" />
            <div className="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-blue-500/50 rounded-tr-2xl" />
            <div className="absolute bottom-0 left-0 w-16 h-16 border-b-2 border-l-2 border-blue-500/50 rounded-bl-2xl" />
            <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-blue-500/50 rounded-br-2xl" />

            {/* Target Box */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 border border-blue-500/20 rounded-3xl" />

            {/* Scanning Line */}
            {isCameraActive && (
              <div className="absolute inset-x-8 h-0.5 bg-gradient-to-r from-transparent via-blue-500/80 to-transparent shadow-[0_0_20px_rgba(59,130,246,0.8)] animate-scan-line top-0 z-20" />
            )}

            {/* Telemetry */}
            <div className="absolute top-8 left-8 text-blue-400 font-mono text-[10px] space-y-1 opacity-50">
              <p>FPS: 30.0</p>
              <p>RES: 1080P</p>
              <p>ISO: AUTO</p>
            </div>
            <div className="absolute top-8 right-8 text-blue-400 font-mono text-[10px] text-right space-y-1 opacity-50">
              <p>LAT: 27.5MS</p>
              <p>ENC: H.264</p>
              <p>SIG: STRONG</p>
            </div>
          </div>

          {/* Bottom HUD info */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-6 px-6 py-3 glass-morphism rounded-2xl border-white/10 z-20 min-w-[300px] justify-center">
            <div className="flex items-center gap-3">
              <div
                className={`w-2.5 h-2.5 rounded-full ${isProcessing ? "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)] animate-pulse" : "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"}`}
              />
              <span className="text-xs font-bold uppercase tracking-[0.2em] w-32">
                {isProcessing ? "Analyzing Hash" : "Sensor Ready"}
              </span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <div className="flex items-center gap-2">
              <Fingerprint className="w-4 h-4 text-blue-400" />
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">
                Biometric Engine v2.0
              </span>
            </div>
          </div>
        </div>

        {/* Identification Result Section */}
        <div className="w-full lg:w-96 space-y-6">
          <div className="glass-card p-10 min-h-[400px] flex flex-col items-center justify-center text-center relative overflow-hidden group border-white/5 transition-all">
            {/* Background Decoration */}
            <div className="absolute -top-12 -right-12 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl group-hover:bg-blue-500/10 transition-all duration-500" />

            {!recognitionResult ? (
              isProcessing ? (
                <div className="space-y-6 animate-pulse">
                  <div className="relative mx-auto">
                    <div className="w-32 h-32 bg-blue-500/10 rounded-3xl flex items-center justify-center mx-auto border border-blue-500/30 shadow-[0_0_40px_rgba(59,130,246,0.15)] ring-1 ring-blue-500/20">
                      <div className="absolute inset-2 border-2 border-blue-500/20 border-t-blue-500 rounded-2xl animate-spin" />
                      <Activity className="w-12 h-12 text-blue-400 animate-pulse" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-blue-400 uppercase tracking-widest animate-pulse">
                      Processing Biometrics
                    </h3>
                    <p className="text-sm text-slate-500 mt-2 font-medium font-mono">
                      Analyzing Facial Features...
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-6 animate-pulse">
                  <div className="w-32 h-32 bg-slate-800/50 rounded-3xl flex items-center justify-center mx-auto border-2 border-dashed border-slate-700">
                    <User className="w-12 h-12 text-slate-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-500 uppercase tracking-widest">
                      Awaiting Identity
                    </h3>
                    <p className="text-sm text-slate-600 mt-2 font-medium">
                      Position Subject in Frame
                    </p>
                  </div>
                </div>
              )) : (
              <div className="relative w-full">
                {isProcessing && (
                  <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center rounded-3xl border border-blue-500/20 animate-fade-in">
                    <div className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 rounded-full border border-blue-500/30">
                      <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
                      <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Re-Scanning...</span>
                    </div>
                  </div>
                )}
                {recognitionResult.identity === "known" ? (
                  <div className="space-y-8 w-full animate-fade-in">
                    <div className="relative mx-auto">
                      <div className="w-36 h-36 bg-green-500/10 rounded-3xl flex items-center justify-center mx-auto border border-green-500/30 shadow-[0_0_40px_rgba(34,197,94,0.15)] ring-1 ring-green-500/20">
                        <div className="absolute inset-2 border-2 border-green-500/20 rounded-2xl animate-pulse" />
                        <User className="w-16 h-16 text-green-400" />
                      </div>
                      <div className="absolute -bottom-3 -right-3 bg-green-500 rounded-2xl p-2 border-[6px] border-slate-900 shadow-xl">
                        <ShieldCheck className="w-7 h-7 text-slate-950" />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="space-y-2">
                        <p className="text-xs font-bold text-green-400 uppercase tracking-[0.3em] mb-3">
                          Identity Verified
                        </p>
                        <h3 className="text-4xl font-bold text-white tracking-tight">
                          {recognitionResult.name}
                        </h3>
                        <div className="flex flex-col items-center gap-2 pt-2">
                          <div className="flex gap-2">
                            <span className="px-4 py-1 bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20 rounded-full text-[10px] uppercase tracking-widest">
                              {recognitionResult.role}
                            </span>
                            <span className="px-4 py-1 bg-slate-500/10 text-slate-400 font-bold border border-slate-500/20 rounded-full text-[10px] uppercase tracking-widest">
                              ID: {recognitionResult.staff_id}
                            </span>
                          </div>
                          {recognitionResult.is_low_confidence && (
                            <div className="mt-4 px-4 py-2 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center gap-2 animate-pulse">
                              <ShieldAlert className="w-4 h-4 text-amber-500" />
                              <span className="text-[10px] font-black text-amber-500 uppercase tracking-widest">
                                Low Confidence Match
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-px bg-white/5 rounded-2xl overflow-hidden border border-white/5">
                      <div className="p-4 bg-slate-900/50 text-left">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1 font-mono">
                          Decision
                        </p>
                        <p className="font-bold text-blue-400 text-xs uppercase">
                          {recognitionResult.decision_type || "Verified"}
                        </p>
                      </div>
                      <div className="p-4 bg-slate-900/50 text-left">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1 font-mono">
                          Match Score
                        </p>
                        <p className="font-bold text-slate-200">
                          {recognitionResult.distance !== undefined ?
                            Math.max(0, (1 - (Math.pow(recognitionResult.distance, 2) / 2)) * 100).toFixed(1) + '%' :
                            'N/A'}
                        </p>
                      </div>
                    </div>

                    <div className="py-2.5 bg-green-500/10 text-green-400 text-xs rounded-xl font-bold uppercase tracking-widest border border-green-500/20 shadow-lg shadow-green-950/20">
                      Access Granted
                    </div>
                  </div>
                ) : recognitionResult.candidate_name ? (
                  <div className="space-y-8 w-full animate-fade-in">
                    <div className="relative mx-auto">
                      <div className="w-36 h-36 bg-amber-500/10 rounded-3xl flex items-center justify-center mx-auto border border-amber-500/30 shadow-[0_0_40px_rgba(245,158,11,0.15)] ring-1 ring-amber-500/20">
                        <div className="absolute inset-2 border-2 border-amber-500/20 rounded-2xl animate-pulse" />
                        <User className="w-16 h-16 text-amber-500" />
                      </div>
                      <div className="absolute -bottom-3 -right-3 bg-amber-500 rounded-2xl p-2 border-[6px] border-slate-900 shadow-xl">
                        <ShieldAlert className="w-7 h-7 text-slate-950" />
                      </div>
                    </div>

                    <div className="space-y-4 text-center">
                      <div className="space-y-2">
                        <p className="text-xs font-bold text-amber-500 uppercase tracking-[0.3em] mb-3">
                          Possible Match
                        </p>
                        <h3 className="text-3xl font-bold text-white tracking-tight">
                          {recognitionResult.candidate_name}?
                        </h3>
                        <p className="text-slate-500 text-xs font-medium  max-w-[200px] mx-auto">
                          Low confidence score detected. Manual verification suggested.
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-px bg-white/5 rounded-2xl overflow-hidden border border-white/5">
                      <div className="p-4 bg-slate-900/50 text-left">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1 font-mono">
                          Confidence
                        </p>
                        <p className="font-bold text-amber-500 text-xs uppercase">
                          Uncertain
                        </p>
                      </div>
                      <div className="p-4 bg-slate-900/50 text-left">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1 font-mono">
                          Match Score
                        </p>
                        <p className="font-bold text-slate-200">
                          {recognitionResult.distance !== undefined ?
                            Math.max(0, (1 - (Math.pow(recognitionResult.distance, 2) / 2)) * 100).toFixed(1) + '%' :
                            'N/A'}
                        </p>
                      </div>
                    </div>

                    <div className="py-2.5 bg-amber-500/10 text-amber-500 text-xs rounded-xl font-bold uppercase tracking-widest border border-amber-500/20">
                      Access Restricted (Retry Suggested)
                    </div>
                  </div>
                ) : (
                  <div className="space-y-8 animate-fade-in w-full">
                    <div className="w-32 h-32 bg-red-500/10 rounded-3xl flex items-center justify-center mx-auto border border-red-500/30 shadow-[0_0_40px_rgba(239,68,68,0.1)] ring-1 ring-red-500/20">
                      <div className="absolute inset-2 border-2 border-red-500/10 rounded-2xl" />
                      <UserX className="w-14 h-14 text-red-500" />
                    </div>
                    <div className="space-y-3">
                      <h3 className="text-2xl font-bold text-white tracking-tight">
                        Access Protocol Failure
                      </h3>
                      <p className="text-slate-400 text-sm font-medium leading-relaxed max-w-[240px] mx-auto">
                        Subject identity not found in administrative records.
                      </p>
                    </div>

                    <div className="py-2.5 bg-red-500/10 text-red-500 text-xs rounded-xl font-bold uppercase tracking-widest border border-red-500/20 shadow-lg shadow-red-950/20">
                      Restriction Active
                    </div>

                    <div className="flex items-center gap-2 justify-center text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                      <ShieldAlert className="w-3 h-3" /> Report Logged
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer Branding */}

      <style>{`
                @keyframes scan-line {
                    0% { transform: translateY(0); opacity: 0; }
                    5% { opacity: 1; }
                    95% { opacity: 1; }
                    100% { transform: translateY(580px); opacity: 0; }
                }
                .animate-scan-line {
                    height: 2px;
                    animation: scan-line 3s linear infinite;
                }
                .animate-fade-in {
                    animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `}</style>
    </div>
  );
};

export default Recognition;
