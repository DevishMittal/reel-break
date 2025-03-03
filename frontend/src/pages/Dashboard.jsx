import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
  );
  
  const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
  
    const BACKEND_URL = 'http://localhost:8000';
  
    useEffect(() => {
      const fetchStats = async () => {
        try {
          const response = await axios.get(`${BACKEND_URL}/usage_stats`);
          setStats(response.data.data);
          setLoading(false);
        } catch (err) {
          console.error('Error fetching stats:', err);
          setError('Failed to load statistics');
          setLoading(false);
        }
      };
  
      fetchStats();
      // Poll for updates every 30 seconds
      const interval = setInterval(fetchStats, 30000);
      return () => clearInterval(interval);
    }, [BACKEND_URL]);
  
    // Prepare chart data if stats are available
    const preparePlatformData = () => {
      if (!stats || !stats.platforms) return null;
  
      const platforms = stats.platforms;
      const labels = Object.keys(platforms);
      const data = Object.values(platforms);
  
      return {
        labels,
        datasets: [
          {
            label: 'Minutes Spent',
            data,
            backgroundColor: [
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
              'rgba(75, 192, 192, 0.6)',
              'rgba(153, 102, 255, 0.6)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1,
          },
        ],
      };
    };
  
    // Creating mock weekly data since our backend doesn't provide this yet
    const weeklyData = {
      labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      datasets: [
        {
          label: 'Daily Usage (minutes)',
          data: [45, 59, 80, 81, 56, 55, stats?.today_minutes || 0],
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1,
        },
        {
          label: 'Daily Goal',
          data: Array(7).fill(stats?.daily_goal_minutes || 60),
          fill: false,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderDash: [5, 5],
          tension: 0.1,
        },
      ],
    };
  
    // For demo purposes - progress toward daily goal
    const progressData = {
      labels: ['Used', 'Remaining'],
      datasets: [
        {
          data: [
            stats?.today_minutes || 0,
            Math.max(0, (stats?.daily_goal_minutes || 60) - (stats?.today_minutes || 0)),
          ],
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(200, 200, 200, 0.6)',
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(200, 200, 200, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };
  
    if (loading) {
      return (
        <div className="flex-1 p-10 flex items-center justify-center">
          <div className="text-lg font-medium text-gray-600">Loading dashboard data...</div>
        </div>
      );
    }
  
    if (error) {
      return (
        <div className="flex-1 p-10 flex items-center justify-center">
          <div className="text-lg font-medium text-red-600">{error}</div>
        </div>
      );
    }
  
    return (
      <div className="flex-1 p-8 ml-64">
        <h1 className="text-2xl font-semibold text-gray-800 mb-6">ScreenBreak Dashboard</h1>
        
        {/* Stats summary cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm mb-1">Today's Usage</div>
            <div className="flex items-end space-x-2">
              <div className="text-3xl font-bold text-gray-800">{stats?.today_minutes || 0}</div>
              <div className="text-gray-600 mb-1">minutes</div>
            </div>
            <div className="text-sm mt-2">
              {((stats?.today_minutes || 0) >= (stats?.daily_goal_minutes || 60)) ? 
                <span className="text-red-500">Exceeded daily goal</span> : 
                <span className="text-green-500">{Math.max(0, (stats?.daily_goal_minutes || 60) - (stats?.today_minutes || 0))} minutes remaining</span>
              }
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm mb-1">Current Session</div>
            <div className="flex items-end space-x-2">
              <div className="text-3xl font-bold text-gray-800">{stats?.current_session_minutes || 0}</div>
              <div className="text-gray-600 mb-1">minutes</div>
            </div>
            <div className="text-sm mt-2">
              {((stats?.current_session_minutes || 0) >= (stats?.session_goal_minutes || 15)) ? 
                <span className="text-red-500">Exceeded session goal</span> : 
                <span className="text-green-500">{Math.max(0, (stats?.session_goal_minutes || 15) - (stats?.current_session_minutes || 0))} minutes remaining</span>
              }
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm mb-1">Session Count</div>
            <div className="flex items-end space-x-2">
              <div className="text-3xl font-bold text-gray-800">{stats?.times_opened_today || 0}</div>
              <div className="text-gray-600 mb-1">today</div>
            </div>
            <div className="text-sm mt-2">
              {(stats?.times_opened_today || 0) > 10 ? 
                <span className="text-orange-500">Frequent app opening detected</span> : 
                <span className="text-green-500">Healthy usage pattern</span>
              }
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm mb-1">Daily Goal</div>
            <div className="flex items-end space-x-2">
              <div className="text-3xl font-bold text-gray-800">{stats?.daily_goal_minutes || 60}</div>
              <div className="text-gray-600 mb-1">minutes</div>
            </div>
            <div className="text-sm mt-2 text-blue-500">
              Set in settings
            </div>
          </div>
        </div>
        
        {/* Charts section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Platform breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-800 mb-4">Platform Breakdown</h2>
            {stats?.platforms && Object.keys(stats.platforms).length > 0 ? (
              <div className="h-64">
                <Bar 
                  data={preparePlatformData()} 
                  options={{
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                      title: {
                        display: false,
                      },
                    },
                  }} 
                />
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No platform data available yet
              </div>
            )}
          </div>
          
          {/* Daily progress */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-800 mb-4">Daily Goal Progress</h2>
            <div className="h-64">
              <Doughnut 
                data={progressData} 
                options={{
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                  cutout: '70%',
                }} 
              />
            </div>
          </div>
        </div>
        
        {/* Weekly trend */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-medium text-gray-800 mb-4">Weekly Usage Trend</h2>
          <div className="h-80">
            <Line 
              data={weeklyData} 
              options={{
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Minutes'
                    }
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
    );
  };
  
  export default Dashboard;