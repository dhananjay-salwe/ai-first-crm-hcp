import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  formData: {
    hcp_name: '',
    interaction_type: 'Meeting',
    date: '',
    time: '',
    attendees: [],
    topics_discussed: '',
    materials_shared: [],
    samples_distributed: [],
    sentiment: 'Neutral',
    outcomes: '',
    follow_up_actions: '',
    ai_suggested_followups: []
  },
  chatMessages: [
    { role: 'ai', text: 'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy...")' }
  ]
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    updateEntireForm: (state, action) => {
      // Merge AI extracted data with existing form data
      state.formData = { ...state.formData, ...action.payload };
    },
    addChatMessage: (state, action) => {
      state.chatMessages.push(action.payload);
    }
  }
});

export const { updateFormField, updateEntireForm, addChatMessage } = interactionSlice.actions;
export default interactionSlice.reducer;