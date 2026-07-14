import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateFormField } from './redux/interactionSlice';

const InteractionForm = () => {
  const dispatch = useDispatch();
  const formData = useSelector((state) => state.interaction.formData);

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch(updateFormField({ field: name, value }));
  };

  const handleSentimentChange = (sentiment) => {
    dispatch(updateFormField({ field: 'sentiment', value: sentiment }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
      <h3 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Interaction Details</h3>
      
      <div style={{ display: 'flex', gap: '15px' }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>HCP Name</label>
          <input 
            type="text" name="hcp_name" value={formData.hcp_name || ''} 
            onChange={handleChange} style={inputStyle} placeholder="Search or select HCP..."
          />
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Interaction Type</label>
          <select 
            name="interaction_type" value={formData.interaction_type || 'Meeting'} 
            onChange={handleChange} style={inputStyle}
          >
            <option value="Meeting">Meeting</option>
            <option value="Call">Call</option>
            <option value="Email">Email</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '15px' }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Date</label>
          <input 
            type="date" name="date" value={formData.date || ''} 
            onChange={handleChange} style={inputStyle}
          />
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Time</label>
          <input 
            type="time" name="time" value={formData.time || ''} 
            onChange={handleChange} style={inputStyle}
          />
        </div>
      </div>

      <div>
        <label style={labelStyle}>Topics Discussed</label>
        <textarea 
          name="topics_discussed" value={formData.topics_discussed || ''} 
          onChange={handleChange} style={{ ...inputStyle, minHeight: '80px' }} 
          placeholder="Enter key discussion points..."
        />
      </div>

      <div>
        <h4 style={{ margin: '15px 0 5px 0', fontSize: '14px', color: '#555' }}>Materials & Samples</h4>
        <div style={{ background: '#f9f9f9', padding: '10px', borderRadius: '4px', border: '1px solid #eee', marginBottom: '10px' }}>
          <label style={labelStyle}>Materials Shared</label>
          <p style={valueStyle}>{formData.materials_shared?.length > 0 ? formData.materials_shared.join(', ') : 'No materials added.'}</p>
        </div>
        <div style={{ background: '#f9f9f9', padding: '10px', borderRadius: '4px', border: '1px solid #eee' }}>
          <label style={labelStyle}>Samples Distributed</label>
          <p style={valueStyle}>{formData.samples_distributed?.length > 0 ? formData.samples_distributed.join(', ') : 'No samples added.'}</p>
        </div>
      </div>

      <div>
        <label style={labelStyle}>Observed/Inferred HCP Sentiment</label>
        <div style={{ display: 'flex', gap: '15px', marginTop: '5px' }}>
          {['Positive', 'Neutral', 'Negative'].map((sentiment) => (
            <label key={sentiment} style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '14px' }}>
              <input 
                type="radio" 
                name="sentiment" 
                checked={formData.sentiment === sentiment} 
                onChange={() => handleSentimentChange(sentiment)} 
              />
              {sentiment}
            </label>
          ))}
        </div>
      </div>

      <div>
        <label style={labelStyle}>Outcomes</label>
        <textarea 
          name="outcomes" value={formData.outcomes || ''} 
          onChange={handleChange} style={{ ...inputStyle, minHeight: '60px' }} 
          placeholder="Key outcomes or agreements..."
        />
      </div>

      <div>
        <label style={labelStyle}>Follow-up Actions</label>
        <textarea 
          name="follow_up_actions" value={formData.follow_up_actions || ''} 
          onChange={handleChange} style={{ ...inputStyle, minHeight: '60px' }} 
          placeholder="Enter next steps or tasks..."
        />
      </div>

      {formData.ai_suggested_followups?.length > 0 && (
        <div style={{ background: '#eef5ff', padding: '10px', borderRadius: '4px', border: '1px solid #cce0ff' }}>
          <label style={{ ...labelStyle, color: '#0056b3' }}>AI Suggested Follow-ups:</label>
          <ul style={{ paddingLeft: '20px', marginTop: '5px', fontSize: '13px', color: '#0056b3' }}>
            {formData.ai_suggested_followups.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// Simple reusable inline styles for the form
const labelStyle = { display: 'block', fontSize: '12px', fontWeight: '600', color: '#555', marginBottom: '5px' };
const inputStyle = { width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px', fontSize: '14px', fontFamily: 'inherit' };
const valueStyle = { fontSize: '14px', color: '#333', fontStyle: 'italic' };

export default InteractionForm;