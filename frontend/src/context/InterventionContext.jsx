import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const InterventionContext = createContext();

export function InterventionProvider({ children }) {
  const [intervention, setIntervention] = useState(null);
  const BACKEND_URL = 'http://localhost:8000';

  // Poll for interventions
  useEffect(() => {
    const checkForInterventions = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/check_intervention`);
        if (response.data.intervention_required) {
          setIntervention(response.data.intervention_data);
        } else {
          setIntervention(null);
        }
      } catch (error) {
        console.error("Failed to check for interventions", error);
      }
    };

    // Check immediately and then every 15 seconds
    checkForInterventions();
    const interval = setInterval(checkForInterventions, 15000);
    
    return () => clearInterval(interval);
  }, [BACKEND_URL]);

  const dismissIntervention = () => {
    setIntervention(null);
  };

  return (
    <InterventionContext.Provider value={{ intervention, dismissIntervention }}>
      {children}
    </InterventionContext.Provider>
  );
}

export const useIntervention = () => useContext(InterventionContext);