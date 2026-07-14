import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import axios from 'axios';
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

      // 4. Add AI reply to chat
      dispatch(addChatMessage({ role: 'ai', text: response.data.reply }));

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
        <h2>Log HCP Interaction</h2>
        <InteractionForm />
      </div>

      {/* RIGHT COLUMN: The AI Chat Assistant */}
      <div className="chat-section">
        <h3 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '10px' }}>
          🌐 AI Assistant
        </h3>
        
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {chatMessages.map((msg, idx) => (
            <div key={idx} style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.role === 'user' ? '#007bff' : '#f1f1f1',
              color: msg.role === 'user' ? 'white' : 'black',
              padding: '10px',
              borderRadius: '8px',
              maxWidth: '80%'
            }}>
              {msg.text}
            </div>
          ))}
          {isLoading && <div style={{ alignSelf: 'flex-start', color: 'gray' }}>AI is thinking...</div>}
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <input 
            type="text" 
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Describe interaction..."
            style={{ flex: 1, padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
          <button 
            onClick={handleSendMessage}
            disabled={isLoading}
            style={{ padding: '10px 20px', background: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Log
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;