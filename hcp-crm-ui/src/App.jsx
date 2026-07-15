import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import axios from 'axios';
import { MessageCircle, Send } from 'lucide-react';
import { addChatMessage, updateEntireForm } from './redux/interactionSlice';
import InteractionForm from './InteractionForm';

function App() {
  const dispatch = useDispatch();
  const formData = useSelector((state) => state.interaction.formData);
  const chatMessages = useSelector((state) => state.interaction.chatMessages);

  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    // 1. Add user message to UI
    dispatch(addChatMessage({ role: 'user', text: chatInput }));
    const currentMessage = chatInput;
    setChatInput('');
    setIsLoading(true);

    try {
      // 2. Send to our FastAPI backend
      const response = await axios.post('http://127.0.0.1:8000/api/chat', {
        message: currentMessage,
        current_form_state: formData
      });

      // 3. Update Form with extracted AI data (ignoring nulls)
      const extractedData = response.data.extracted_data;
      const cleanData = Object.fromEntries(
        Object.entries(extractedData).filter(([_, v]) => v != null)
      );

      dispatch(updateEntireForm(cleanData));

      // 4. Add AI reply to chat - but if the DB write failed, say so.
      // response.data.reply is always the happy-path text, it has no idea
      // whether tool_log_interaction actually succeeded.
      const dbResult = response.data.database;
      const replyText = dbResult && dbResult.status === 'error'
        ? `${response.data.reply} (Heads up though - saving this to the database failed: ${dbResult.message})`
        : response.data.reply;

      dispatch(addChatMessage({ role: 'ai', text: replyText }));

    } catch (error) {
      console.error("Error communicating with AI:", error);
      dispatch(addChatMessage({ role: 'ai', text: 'Sorry, I encountered an error connecting to the server.' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* LEFT COLUMN: The Structured Form */}
      <div className="form-section">
        <h2 className="page-title">Log HCP Interaction</h2>
        <InteractionForm />
      </div>

      {/* RIGHT COLUMN: The AI Chat Assistant */}
      <div className="chat-section">
        <div className="chat-header">
          <div className="chat-header-icon">
            <MessageCircle size={15} />
          </div>
          <div className="chat-header-titles">
            <h3>AI Assistant</h3>
            <span>Log interaction via chat</span>
          </div>
        </div>

        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-bubble ai">
              Log interaction details here (e.g., "Met Dr. Smith, discussed
              Product X efficacy, positive sentiment, shared brochure") or ask
              for help.
            </div>
          )}
          {chatMessages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.role === 'user' ? 'user' : 'ai'}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && <div className="chat-thinking">AI is thinking...</div>}
        </div>

        <div className="chat-input-row">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Describe interaction..."
          />
          <button
            className="btn-send"
            onClick={handleSendMessage}
            disabled={isLoading}
          >
            <Send size={14} />
            Log
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;