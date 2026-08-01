import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BrainCircuit,
  Upload,
  FileText,
  HeartPulse,
  X,
  Image as ImageIcon,
  Send,
  Mic,
  MicOff,
  Trash2,
  File,
  AlertCircle,
  CheckCircle
} from "lucide-react";
import {
  sendMessage,
  uploadPDF,
  uploadImage,
  askQuestion,
  getConversation,
  uploadAndAsk,
} from "../api/api";
import { useAuth } from "../context/AuthContext";
import MessageBubble from "../components/chat/MessageBubble";
import ChatInput from "../components/chat/ChatInput";
import TypingLoader from "../components/chat/TypingLoader";
import FollowupOptions from "../components/chat/FollowupOptions";

export default function ChatPage({ reportMode = false }) {
  const { user } = useAuth();
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [followupOptions, setFollowupOptions] = useState([]);
  const [location, setLocation] = useState(null);
  const [reportId, setReportId] = useState(null);
  const [reportName, setReportName] = useState(null);
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState("");
  const [hasDocument, setHasDocument] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [firstQuestionAsked, setFirstQuestionAsked] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [questionForFile, setQuestionForFile] = useState("");
  const [uploadError, setUploadError] = useState(null);
  const [visionUsed, setVisionUsed] = useState(false);
  const [modelUsed, setModelUsed] = useState(null);
  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Load conversation if ID exists
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => setLocation({ latitude: coords.latitude, longitude: coords.longitude }),
      () => setLocation(null),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  }, []);

  const loadConversation = async (id) => {
    try {
      const response = await getConversation(id);
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      console.error("Failed to load conversation:", error);
    }
  };

  // Speech
  const speak = (text) => {
    if (!text) return;
    try {
      window.speechSynthesis.cancel();
      const speech = new SpeechSynthesisUtterance(text);
      speech.lang = "en-US";
      speech.rate = 1;
      speech.pitch = 1;
      window.speechSynthesis.speak(speech);
    } catch (error) {
      console.error("Speech error:", error);
    }
  };

  // Voice recording
  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;

    setIsRecording(true);

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setInput(transcript);
          setIsRecording(false);
          handleSendMessage(transcript);
        }
      }
    };

    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);
    recognition.start();
  };

  // ─────────────────────────────────────────────
  // SEND MESSAGE
  // ─────────────────────────────────────────────

  const handleSendMessage = async (customMessage = null) => {
    const finalMessage = customMessage || input;
    if (!finalMessage.trim() || loading) return;

    // Add user message
    const userMessage = { role: "user", content: finalMessage };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setUploadError(null);
    setFollowupOptions([]);

    try {
      let response;
      let data;

      // If we have a document loaded, ask about it
      if (hasDocument && reportId) {
        response = await askQuestion({
          report_id: reportId,
          question: finalMessage,
          user_id: user.id,
          conversation_id: conversationId
        });
        data = response.data;
      } 
      // Otherwise regular chat
      else {
        response = await sendMessage({
          user_id: user.id,
          message: finalMessage,
          conversation_id: conversationId,
          latitude: location?.latitude,
          longitude: location?.longitude,
        });
        data = response.data;
      }

      // Update conversation ID
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Track if vision was used
      if (data.vision_enabled) {
        setVisionUsed(true);
        setModelUsed(data.model_used);
      }

      // Add AI response
      const aiMessage = {
        role: "assistant",
        content: data.answer || data.response || data.message || "No response",
        reportId: data.report_id || null,
        visionUsed: data.vision_enabled || false,
        modelUsed: data.model_used || null
      };
      setMessages(prev => [...prev, aiMessage]);

      // The API returns the full assessment separately from its short status message.
      // Keep it as its own message so it is rendered in the chat before it is downloaded.
      if (data.report_ready && data.report) {
        setMessages(prev => [
          ...prev,
          {
            role: "assistant",
            content: data.report,
            report: data.report,
            is_report: true,
            report_ready: true,
            severity: data.severity,
            severity_reason: data.severity_reason,
            hospitals: data.hospitals || [],
            google_maps_link: data.google_maps_link || null,
            pdfUrl: data.pdf_url || null,
          },
        ]);
      } else {
        setFollowupOptions(data.followup_options || []);
      }

      // Speak if short
      if (aiMessage.content.length < 200) {
        speak(aiMessage.content);
      }

    } catch (err) {
      console.error("Error:", err);
      const errorMsg = err.response?.data?.detail || err.message || "Failed to process";
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `❌ Sorry, I couldn't process that. Error: ${errorMsg}`
      }]);
      setUploadError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ─────────────────────────────────────────────
  // UPLOAD AND ASK (COMBINED FUNCTION)
  // ─────────────────────────────────────────────

  const handleUploadAndAsk = async (file, question) => {
    if (!file || !question) {
      setUploadError('Please select a file and ask a question');
      return;
    }

    // Reset states
    setUploadError(null);
    setVisionUsed(false);
    setModelUsed(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);
    formData.append("user_id", user.id);

    // Add user messages
    setMessages(prev => [...prev, {
      role: "user",
      content: `📄 **Uploaded:** ${file.name}`
    }]);

    setMessages(prev => [...prev, {
      role: "user",
      content: `❓ ${question}`
    }]);

    setIsUploading(true);
    setLoading(true);
    setUploadProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 300);

      const response = await uploadAndAsk(formData);
      const data = response.data;

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (data.success) {
        setReportId(data.report_id);
        setReportName(file.name);
        setHasDocument(true);
        setFirstQuestionAsked(true);
        setConversationId(data.conversation_id);
        
        // Track vision usage
        if (data.vision_enabled) {
          setVisionUsed(true);
          setModelUsed(data.model_used);
        }

        // Add AI response
        const aiMessage = {
          role: "assistant",
          content: data.answer,
          reportId: data.report_id,
          visionUsed: data.vision_enabled || false,
          modelUsed: data.model_used || null
        };
        setMessages(prev => [...prev, aiMessage]);

        // Add document info message
        let infoContent = `✅ **Document Loaded Successfully!**\n\n`;
        infoContent += `**File:** ${file.name}\n`;
        infoContent += `**Type:** ${data.file_type || 'document'}\n`;
        infoContent += `**Words Extracted:** ${data.word_count || 0}\n`;
        
        if (data.vision_enabled) {
          infoContent += `**Analysis Method:** Vision AI (${data.model_used || 'AI model'})\n`;
          infoContent += `**Note:** This image was analyzed using AI vision capabilities.\n\n`;
        } else {
          infoContent += `**Analysis Method:** Text-based (${data.model_used || 'AI model'})\n\n`;
        }
        
        infoContent += `💡 You can now continue asking questions about this document.`;
        
        const infoMessage = {
          role: "assistant",
          content: infoContent
        };
        setMessages(prev => [...prev, infoMessage]);

        // Speak the answer if short
        if (data.answer && data.answer.length < 200) {
          speak(data.answer);
        }

        // Close modal if open
        setShowUploadModal(false);
        setSelectedFile(null);
        setQuestionForFile("");

      } else {
        const errorMsg = data.message || data.error || 'Unknown error';
        setUploadError(errorMsg);
        setMessages(prev => [...prev, {
          role: "assistant",
          content: `❌ Failed to process: ${errorMsg}`
        }]);
      }

    } catch (err) {
      console.error("Upload and ask error:", err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to upload and ask';
      setUploadError(errorMsg);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `❌ Error: ${errorMsg}`
      }]);
    } finally {
      setIsUploading(false);
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  // ─────────────────────────────────────────────
  // HANDLE FILE SELECTION
  // ─────────────────────────────────────────────

  const handleFileSelect = (file) => {
    if (!file) return;
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setUploadError('File size exceeds 10MB limit');
      return;
    }

    setSelectedFile(file);
    setUploadError(null);
    
    // Let the user choose the first question for every uploaded file.
    setQuestionForFile("");
    
    // Automatically upload if question is set
    // Or show modal for user to modify question
    setShowUploadModal(true);
  };

  // ─────────────────────────────────────────────
  // UPLOAD FILE FROM INPUT
  // ─────────────────────────────────────────────

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
    // Reset input
    e.target.value = '';
  };

  // ─────────────────────────────────────────────
  // CLEAR DOCUMENT
  // ─────────────────────────────────────────────

  const clearDocument = () => {
    setHasDocument(false);
    setReportId(null);
    setReportName(null);
    setFirstQuestionAsked(false);
    setVisionUsed(false);
    setModelUsed(null);
    setMessages(prev => [...prev, {
      role: "assistant",
      content: "🗑️ Document cleared. You can now upload a new one or continue chatting."
    }]);
  };

  // ─────────────────────────────────────────────
  // CLEAR CHAT
  // ─────────────────────────────────────────────

  const clearChat = () => {
    setMessages([]);
    setHasDocument(false);
    setReportId(null);
    setReportName(null);
    setFirstQuestionAsked(false);
    setVisionUsed(false);
    setModelUsed(null);
    setConversationId(null);
    setUploadError(null);
  };

  // ─────────────────────────────────────────────
  // DRAG AND DROP HANDLERS
  // ─────────────────────────────────────────────

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // ─────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────

  return (
    <div className="medivoice-light-theme min-h-screen bg-[#F6F8F7] text-[#12231F] flex overflow-hidden">
      {/* Sidebar */}
      <div className="hidden xl:flex w-80 border-r border-white/10 bg-white/5 backdrop-blur-xl p-8 flex-col">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center">
            <HeartPulse className="text-black w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-black">MediZen AI</h1>
            <p className="text-slate-400 mt-1">{reportMode ? "Medical report analysis" : "AI health assistant"}</p>
          </div>
        </div>

        <div className="mt-12 bg-white/5 border border-white/10 rounded-3xl p-6">
          <h3 className="text-lg font-bold">User</h3>
          <p className="mt-4 text-cyan-300 font-bold">{user?.name || "Guest"}</p>
          <p className="text-slate-400 mt-1">{user?.email || "No email"}</p>
        </div>

        {/* Document Status */}
        {hasDocument && (
          <div className="mt-6 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4">
            <p className="text-emerald-300 font-medium flex items-center gap-2">
              <File className="w-4 h-4" />
              Document Loaded
            </p>
            <p className="text-xs text-emerald-400/70 mt-1 truncate">{reportName}</p>
            {visionUsed && (
              <p className="text-xs text-cyan-400 mt-1 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Vision Analysis Used
              </p>
            )}
            {modelUsed && (
              <p className="text-xs text-slate-400 mt-1">Model: {modelUsed}</p>
            )}
            <p className="text-xs text-slate-400 mt-1">
              {firstQuestionAsked ? "✅ First question answered" : "⏳ Waiting for question"}
            </p>
            <button
              onClick={clearDocument}
              className="mt-2 text-xs text-red-400 hover:text-red-300 transition"
            >
              Remove Document
            </button>
          </div>
        )}

        <button
          onClick={clearChat}
          className="mt-auto bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-4 text-slate-400 hover:text-white transition flex items-center justify-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Clear Chat
        </button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-white/10 bg-white/5 backdrop-blur-xl px-8 py-6 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-black">{reportMode ? "Medical Report Analysis" : "AI Health Chat"}</h2>
            <p className="text-slate-400 mt-1 flex items-center gap-2">
              {reportMode && hasDocument ? (
                <>
                  <FileText className="w-4 h-4 text-emerald-400" />
                  Working with: {reportName}
                </>
              ) : reportMode ? "Upload a report to begin analysis" : "Ask a question or describe your symptoms"}
              {visionUsed && (
                <span className="ml-2 text-xs bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded-full">
                  Vision AI
                </span>
              )}
            </p>
          </div>

          {isRecording && (
            <div className="flex items-center gap-2 bg-red-500/20 border border-red-500/30 rounded-2xl px-4 py-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-red-300 font-medium">Recording...</span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div 
          className="flex-1 overflow-y-auto px-6 py-8 space-y-6"
          onDragOver={reportMode ? handleDragOver : undefined}
          onDrop={reportMode ? handleDrop : undefined}
        >
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-5xl mx-auto text-center mt-20"
            >
              <div className="w-28 h-28 rounded-[40px] bg-cyan-400 mx-auto flex items-center justify-center shadow-[0_0_80px_rgba(0,255,255,0.2)]">
                <BrainCircuit className="text-black w-14 h-14" />
              </div>
              <h1 className="text-6xl font-black mt-10">MediZen AI</h1>
              <p className="text-slate-400 mt-6 text-xl leading-9 max-w-3xl mx-auto">
                {reportMode ? "Upload a medical report to receive a clear summary and ask follow-up questions about it." : "Describe your symptoms or ask a health question. MediVoice will guide you one question at a time."}
              </p>

              {reportMode && <div className="mt-8 flex flex-wrap justify-center gap-3">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 bg-cyan-500/20 border border-cyan-500/30 rounded-full hover:bg-cyan-500/30 transition text-sm flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Upload Document
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp,.webp"
                  onChange={handleFileInputChange}
                  className="hidden"
                />
              </div>}
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((msg, index) => (
              <div key={index}>
                <MessageBubble msg={msg} speak={speak} />
              </div>
            ))}
          </AnimatePresence>

          <FollowupOptions
            options={followupOptions}
            onSelect={handleSendMessage}
          />

          {uploadError && (
            <div className="max-w-2xl mx-auto bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-300 font-medium">Upload Error</p>
                <p className="text-red-200/70 text-sm">{uploadError}</p>
              </div>
            </div>
          )}

          {isUploading && (
            <div className="w-full max-w-md mx-auto">
              <div className="bg-white/5 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-cyan-400 h-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 text-center mt-1">
                Uploading and analyzing... {uploadProgress}%
              </p>
            </div>
          )}

          {loading && !isUploading && <TypingLoader />}
          <div ref={bottomRef} />
        </div>

        {/* Chat Input */}
        <ChatInput
          input={input}
          setInput={setInput}
          onSend={handleSendMessage}
          onVoiceRecord={startRecording}
          isRecording={isRecording}
          loading={loading}
        />
      </div>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && selectedFile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-zinc-900 border border-white/10 rounded-3xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold">
                  Ask Questions About {selectedFile.name}
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="p-2 hover:bg-white/10 rounded-full transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="bg-white/5 rounded-2xl p-4 mb-4">
                <p className="text-sm text-slate-400">Selected File</p>
                <p className="font-medium truncate">{selectedFile.name}</p>
                <p className="text-xs text-slate-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm text-slate-400 mb-2">
                  Your Question
                </label>
                <textarea
                  value={questionForFile}
                  onChange={(e) => setQuestionForFile(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400 transition resize-none"
                  rows="4"
                  placeholder="Ask a question about this document..."
                />
              </div>

              <button
                onClick={() => handleUploadAndAsk(selectedFile, questionForFile)}
                disabled={!questionForFile.trim() || isUploading}
                className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-cyan-500/30 disabled:cursor-not-allowed text-black font-bold py-3 rounded-2xl transition flex items-center justify-center gap-2"
              >
                {isUploading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Upload & Ask
                  </>
                )}
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
