import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateFormField } from './redux/interactionSlice';
import {
  Search,
  Users,
  Edit3,
  Mic,
  Plus,
  Smile,
  Meh,
  Frown,
} from 'lucide-react';

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

  // attendees comes back from the backend as an array, but it's a plain
  // text input on screen - keep the typed text in local state and only
  // push the parsed array up on blur. If we parsed on every keystroke the
  // trailing comma would get stripped mid-type and feel broken.
  const joinAttendees = (val) => (Array.isArray(val) ? val.join(', ') : val || '');
  const [attendeesText, setAttendeesText] = useState(joinAttendees(formData.attendees));

  useEffect(() => {
    setAttendeesText(joinAttendees(formData.attendees));
  }, [formData.attendees]);

  const handleAttendeesBlur = () => {
    const names = attendeesText.split(',').map((s) => s.trim()).filter(Boolean);
    dispatch(updateFormField({ field: 'attendees', value: names }));
  };

  // Placeholders - wire these up to your actual modal / search / voice flows
  const handleVoiceNoteClick = () => {
    console.log('Open voice note capture (requires consent)');
  };

  const handleSearchMaterials = () => {
    console.log('Open materials search/add modal');
  };

  const handleAddSample = () => {
    console.log('Open sample add modal');
  };

  const sentimentOptions = [
    { key: 'Positive', label: 'Positive', icon: Smile, cls: 'positive' },
    { key: 'Neutral', label: 'Neutral', icon: Meh, cls: 'neutral' },
    { key: 'Negative', label: 'Negative', icon: Frown, cls: 'negative' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <h3 className="form-card-header">Interaction Details</h3>

      <div className="field-row">
        <div className="field-group">
          <label className="field-label">HCP Name</label>
          <div className="field-with-icon">
            <Search size={15} />
            <input
              type="text"
              name="hcp_name"
              value={formData.hcp_name || ''}
              onChange={handleChange}
              className="field-input"
              placeholder="Search or select HCP..."
            />
          </div>
        </div>
        <div className="field-group">
          <label className="field-label">Interaction Type</label>
          <select
            name="interaction_type"
            value={formData.interaction_type || 'Meeting'}
            onChange={handleChange}
            className="field-select"
          >
            <option value="Meeting">Meeting</option>
            <option value="Call">Call</option>
            <option value="Email">Email</option>
          </select>
        </div>
      </div>

      <div className="field-row">
        <div className="field-group">
          <label className="field-label">Date</label>
          <input
            type="date"
            name="date"
            value={formData.date || ''}
            onChange={handleChange}
            className="field-input"
          />
        </div>
        <div className="field-group">
          <label className="field-label">Time</label>
          <input
            type="time"
            name="time"
            value={formData.time || ''}
            onChange={handleChange}
            className="field-input"
          />
        </div>
      </div>

      <div className="field-group">
        <label className="field-label">Attendees</label>
        <div className="field-with-icon">
          <Users size={15} />
          <input
            type="text"
            name="attendees"
            value={attendeesText}
            onChange={(e) => setAttendeesText(e.target.value)}
            onBlur={handleAttendeesBlur}
            className="field-input"
            placeholder="Enter names or search..."
          />
        </div>
      </div>

      <div className="field-group">
        <label className="field-label">Topics Discussed</label>
        <div className="textarea-wrapper">
          <textarea
            name="topics_discussed"
            value={formData.topics_discussed || ''}
            onChange={handleChange}
            className="field-textarea"
            placeholder="Enter key discussion points..."
          />
          <button
            type="button"
            className="textarea-icon-btn"
            title="Edit"
            onClick={() => {}}
          >
            <Edit3 size={15} />
          </button>
        </div>
      </div>

      <button type="button" className="btn-voice" onClick={handleVoiceNoteClick}>
        <Mic size={14} />
        Summarize from Voice Note (Requires Consent)
      </button>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h4 className="section-subheader">Materials & Samples</h4>

        <div className="asset-box">
          <div className="asset-box-header">
            <label className="field-label">Materials Shared</label>
            <button type="button" className="btn-outline-sm" onClick={handleSearchMaterials}>
              <Search size={13} />
              Search/Add
            </button>
          </div>
          <p className="asset-empty-text">
            {Array.isArray(formData.materials_shared) && formData.materials_shared.length > 0
              ? formData.materials_shared.join(', ')
              : 'No materials added.'}
          </p>
        </div>

        <div className="asset-box">
          <div className="asset-box-header">
            <label className="field-label">Samples Distributed</label>
            <button type="button" className="btn-outline-sm" onClick={handleAddSample}>
              <Plus size={13} />
              Add Sample
            </button>
          </div>
          <p className="asset-empty-text">
            {Array.isArray(formData.samples_distributed) && formData.samples_distributed.length > 0
              ? formData.samples_distributed.join(', ')
              : 'No samples added.'}
          </p>
        </div>
      </div>

      <div className="field-group">
        <label className="field-label">Observed/Inferred HCP Sentiment</label>
        <div className="sentiment-group">
          {sentimentOptions.map(({ key, label, icon: Icon, cls }) => {
            const selected = formData.sentiment === key;
            return (
              <label
                key={key}
                className={`sentiment-option ${cls}${selected ? ' selected' : ''}`}
              >
                <input
                  type="radio"
                  name="sentiment"
                  checked={selected}
                  onChange={() => handleSentimentChange(key)}
                  style={{ display: 'none' }}
                />
                <Icon size={15} />
                {label}
              </label>
            );
          })}
        </div>
      </div>

      <div className="field-group">
        <label className="field-label">Outcomes</label>
        <textarea
          name="outcomes"
          value={formData.outcomes || ''}
          onChange={handleChange}
          className="field-textarea"
          placeholder="Key outcomes or agreements..."
        />
      </div>

      <div className="field-group">
        <label className="field-label">Follow-up Actions</label>
        <textarea
          name="follow_up_actions"
          value={formData.follow_up_actions || ''}
          onChange={handleChange}
          className="field-textarea"
          placeholder="Enter next steps or tasks..."
        />
      </div>

      {formData.ai_suggested_followups?.length > 0 && (
        <div className="ai-followups-box">
          <label className="field-label">AI Suggested Follow-ups:</label>
          <ul>
            {formData.ai_suggested_followups.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default InteractionForm;