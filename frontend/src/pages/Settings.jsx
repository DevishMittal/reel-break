import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = () => {
  const [settings, setSettings] = useState({
    daily_limit_minutes: 60,
    session_limit_minutes: 15,
    intervention_frequency: 'medium'
  });
  const [loading, setLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState({ type: '', message: '' });

  const BACKEND_URL = 'http://localhost:8000';

  // Get current settings when the component mounts
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/usage_stats`);
        const stats = response.data.data;
        
        setSettings({
          daily_limit_minutes: stats.daily_goal_minutes || 60,
          session_limit_minutes: stats.session_goal_minutes || 15,
          intervention_frequency: 'medium' // This might not be in the stats, so we use default
        });
      } catch (err) {
        console.error('Error fetching settings:', err);
        setSaveMessage({ type: 'error', message: 'Failed to load settings' });
      }
    };

    fetchSettings();
  }, [BACKEND_URL]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: name.includes('minutes') ? parseInt(value, 10) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSaveMessage({ type: '', message: '' });

    try {
      await axios.post(`${BACKEND_URL}/update_settings`, settings);
      setSaveMessage({ type: 'success', message: 'Settings saved successfully!' });
    } catch (err) {
      console.error('Error saving settings:', err);
      setSaveMessage({ type: 'error', message: 'Failed to save settings' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 p-8 ml-64">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Settings</h1>
      
      <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="daily_limit_minutes">
              Daily Usage Limit (minutes)
            </label>
            <input
              id="daily_limit_minutes"
              name="daily_limit_minutes"
              type="number"
              min="1"
              max="480"
              value={settings.daily_limit_minutes}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Set your target maximum daily screen time for short-form videos
            </p>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="session_limit_minutes">
              Session Limit (minutes)
            </label>
            <input
              id="session_limit_minutes"
              name="session_limit_minutes"
              type="number"
              min="1"
              max="120"
              value={settings.session_limit_minutes}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Set how long you'd like each continuous viewing session to be
            </p>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="intervention_frequency">
              Intervention Frequency
            </label>
            <select
              id="intervention_frequency"
              name="intervention_frequency"
              value={settings.intervention_frequency}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="low">Low - Less frequent reminders</option>
              <option value="medium">Medium - Balanced reminders</option>
              <option value="high">High - More frequent reminders</option>
            </select>
            <p className="mt-1 text-sm text-gray-500">
              Choose how often you'd like to receive notifications or interventions
            </p>
          </div>
          
          {saveMessage.message && (
            <div className={`mb-4 p-3 rounded-md ${saveMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {saveMessage.message}
            </div>
          )}
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`px-4 py-2 rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;