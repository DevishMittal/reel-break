import React from 'react';
import { useIntervention } from '../context/InterventionContext';
import { XMarkIcon } from '@heroicons/react/24/outline';

// Notification component (less intrusive)
export function InterventionNotification() {
  const { intervention, dismissIntervention } = useIntervention();
  
  if (!intervention || intervention.type !== 'notification') {
    return null;
  }
  
  return (
    <div className="fixed bottom-4 right-4 max-w-sm bg-white rounded-lg shadow-lg p-4 border-l-4 border-indigo-500 animate-slide-in">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">Time Check</h3>
          <p className="text-sm text-gray-700 mt-1">{intervention.message}</p>
          <div className="mt-2 text-xs text-gray-500">
            Current session: {intervention.usage_stats.current_session_minutes} minutes
          </div>
        </div>
        <button onClick={dismissIntervention} className="ml-4 text-gray-400 hover:text-gray-500">
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

// Overlay component (more intrusive)
export function InterventionOverlay() {
  const { intervention, dismissIntervention } = useIntervention();
  
  if (!intervention || intervention.type !== 'overlay') {
    return null;
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6 m-4">
        <div className="flex justify-between items-start">
          <h2 className="text-xl font-bold text-gray-900">Time to Take a Break</h2>
          <button onClick={dismissIntervention} className="text-gray-400 hover:text-gray-500">
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        <p className="mt-4 text-gray-600">{intervention.message}</p>
        <div className="mt-4 bg-gray-50 p-3 rounded-md">
          <h4 className="text-sm font-medium text-gray-700">Your Usage Today</h4>
          <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
            <div className="text-gray-500">Session time:</div>
            <div className="text-gray-900 font-medium">{intervention.usage_stats.current_session_minutes} minutes</div>
            <div className="text-gray-500">Daily total:</div>
            <div className="text-gray-900 font-medium">{intervention.usage_stats.today_minutes} minutes</div>
            <div className="text-gray-500">Daily goal:</div>
            <div className="text-gray-900 font-medium">{intervention.usage_stats.daily_goal_minutes} minutes</div>
          </div>
        </div>
        <div className="mt-5 flex justify-end space-x-3">
          <button 
            onClick={dismissIntervention}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Take a Break (5 min)
          </button>
          <button 
            onClick={dismissIntervention}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
}