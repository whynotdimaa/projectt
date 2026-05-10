import React, { useState, useEffect } from 'react';
import { 
  Users, UserCheck, Clock, CalendarRange, 
  TrendingUp, TrendingDown, DollarSign 
} from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../api/axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StatCard = ({ icon: Icon, title, value, trend, color, index }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3, delay: index * 0.1 }}
    className="glass-card stats-card"
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <p className="stats-card-title">{title}</p>
        <h3 className="stats-card-value" style={{ margin: '0.25rem 0' }}>{value}</h3>
      </div>
      <div className="stats-card-icon" style={{ backgroundColor: `${color}20`, color: color }}>
        <Icon size={20} />
      </div>
    </div>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', marginTop: '0.5rem' }}>
      <span style={{ color: trend > 0 ? 'var(--success)' : trend < 0 ? 'var(--danger)' : 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
        {trend > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />} {Math.abs(trend)}%
      </span>
      <span style={{ color: 'var(--text-muted)' }}>vs last month</span>
    </div>
  </motion.div>
);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState({
    funnel: [],
    timeToHire: { avg_seconds: 0, hired_count: 0 },
    statusDistribution: {},
    totalCandidates: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Prepopulate loading state just in case endpoint doesn't fully return data yet.
        const [funnelRes, tthRes, statusRes, candRes] = await Promise.allSettled([
          api.get('/analytics/funnel/'),
          api.get('/analytics/time-to-hire/'),
          api.get('/analytics/candidates-by-status/'),
          api.get('/candidates/')
        ]);

        const getVal = (res, def) => res.status === 'fulfilled' ? res.value.data : def;
        
        const candidatesList = getVal(candRes, []);
        
        setAnalytics({
          funnel: getVal(funnelRes, []),
          timeToHire: getVal(tthRes, { avg_seconds: 0, avg_human: '0:00:00' }),
          statusDistribution: getVal(statusRes, {}),
          totalCandidates: Array.isArray(candidatesList) ? candidatesList.length : (candidatesList.results?.length || 0)
        });
      } catch (err) {
        console.error("Error loading analytics:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#a1a1aa', font: { family: 'Plus Jakarta Sans', size: 11 } }
      },
      tooltip: {
        backgroundColor: '#18181b',
        titleColor: '#f4f4f5',
        bodyColor: '#a1a1aa',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
      }
    },
    scales: {
      y: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#71717a', stepSize: 1, beginAtZero: true }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#71717a' }
      }
    }
  };

  // Format funnel properly (backend sends a list of dicts)
  const funnelLabels = analytics.funnel.length > 0 ? analytics.funnel.map(f => f.status) : ['NEW', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED'];
  const funnelData = analytics.funnel.length > 0 ? analytics.funnel.map(f => f.count) : [0, 0, 0, 0, 0];

  const barData = {
    labels: funnelLabels,
    datasets: [{
      label: 'Total Reach',
      data: funnelData,
      backgroundColor: 'rgba(99, 102, 241, 0.8)',
      borderRadius: 6,
    }]
  };

  // Pipeline status distribution - simple dict from backend
  const statusDistLabels = Object.keys(analytics.statusDistribution || {});
  const statusDistValues = Object.values(analytics.statusDistribution || {});

  const donutData = {
    labels: statusDistLabels.length > 0 ? statusDistLabels : ['None'],
    datasets: [{
      data: statusDistValues.length > 0 ? statusDistValues : [1],
      backgroundColor: ['#6366f1', '#a855f7', '#10b981', '#f59e0b', '#ef4444', '#71717a'],
      borderWidth: 0,
    }]
  };
  
  // Convert seconds from backend to printable days/hours
  const getDays = (sec) => sec ? (sec / 86400).toFixed(1) : "0";

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Recruitment Analytics</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Insights overview across the company pipeline.</p>
      </div>

      <div className="grid-stats">
        <StatCard icon={Users} title="Total Candidates" value={analytics.totalCandidates} trend={0} color="#6366f1" index={0} />
        <StatCard icon={Clock} title="Avg. Time to Hire" value={`${getDays(analytics.timeToHire?.avg_seconds)} Days`} trend={0} color="#a855f7" index={1} />
        <StatCard icon={UserCheck} title="Success Hires" value={analytics.timeToHire?.hired_count || "0"} trend={0} color="#10b981" index={2} />
        <StatCard icon={CalendarRange} title="Pending Action" value={Math.max(0, analytics.totalCandidates - (analytics.timeToHire?.hired_count || 0))} trend={0} color="#3b82f6" index={3} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card" 
          style={{ padding: '1.5rem' }}
        >
          <h3 style={{ marginBottom: '1.5rem' }}>Candidate Funnel</h3>
          <div style={{ height: '300px' }}>
            <Bar options={chartOptions} data={barData} />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card" 
          style={{ padding: '1.5rem' }}
        >
          <h3 style={{ marginBottom: '1.5rem' }}>Pipeline Status</h3>
          <div style={{ height: '260px', display: 'flex', justifyContent: 'center' }}>
            <Doughnut 
              data={donutData} 
              options={{
                cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { color: '#a1a1aa', usePointStyle: true } } }
              }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
