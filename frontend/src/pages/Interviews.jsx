import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { CalendarDays, Clock, User, Star } from 'lucide-react';
import { motion } from 'framer-motion';

const Interviews = () => {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedInterview, setSelectedInterview] = useState(null);

  const [evalData, setEvalData] = useState({ score: '', comment: '' });

  const fetchInterviews = async () => {
    try {
      const res = await api.get('/interviews/');
      setInterviews(res.data.results || res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInterviews();
  }, []);

  const handleEvaluate = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/interviews/${selectedInterview.id}/evaluate/`, {
         score: parseInt(evalData.score),
         comment: evalData.comment
      });
      setSelectedInterview(null);
      fetchInterviews();
    } catch (err) {
      alert("Evaluation failed. Ensure score is between 1 and 10.");
    }
  };

  const sampleInterviews = interviews.length > 0 ? interviews : [
    { id: 1, candidate_name: 'Oleksii Reznikov', scheduled_at: new Date().toISOString(), score: 8, notes: 'Strong technical background' },
    { id: 2, candidate_name: 'Daria Ivanova', scheduled_at: new Date(Date.now() + 86400000).toISOString(), score: null, notes: 'System Design phase' }
  ];

  return (
    <div>
      <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Interviews</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Upcoming and completed interviews scheduling.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {sampleInterviews.map((interview, idx) => (
          <motion.div 
            key={interview.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass-card"
            style={{ padding: '1.25rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}
          >
            <div style={{ 
              width: 50, height: 50, borderRadius: '12px', 
              background: 'rgba(168, 85, 247, 0.1)', color: 'var(--accent)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <CalendarDays size={24} />
            </div>
            
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>
                {interview.candidate_name || `Interview #${interview.id}`}
              </h3>
              <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={14} /> {new Date(interview.scheduled_at).toLocaleDateString()}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><User size={14} /> Tech Round</span>
              </div>
            </div>

            <div>
              {interview.score ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--warning)' }}>
                  <Star size={16} fill="var(--warning)" />
                  <span style={{ fontWeight: 700 }}>{interview.score}/10</span>
                </div>
              ) : (
                <span className="badge badge-neutral">Pending</span>
              )}
            </div>
            
            <button 
              onClick={() => setSelectedInterview(interview)}
              className="btn btn-secondary" 
              style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
            >
              Details
            </button>
          </motion.div>
        ))}
      </div>

      {/* Simple Details Modal Overlay */}
      {selectedInterview && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }} onClick={() => setSelectedInterview(null)}>
          <motion.div 
             initial={{ scale: 0.95, opacity: 0 }}
             animate={{ scale: 1, opacity: 1 }}
             className="glass-card" 
             style={{ padding: '2rem', maxWidth: '450px', width: '90%' }}
             onClick={(e) => e.stopPropagation()}
          >
             <h2 style={{ marginBottom: '1rem' }}>Interview Details</h2>
             <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Overview of record #{selectedInterview.id}</p>
             
             <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Candidate</div>
                  <div style={{ fontWeight: 600 }}>{selectedInterview.candidate_name || `Interviewee #${selectedInterview.candidate_id}`}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Scheduled Time</div>
                  <div>{new Date(selectedInterview.scheduled_at).toLocaleString()}</div>
                </div>
                {selectedInterview.score ? (
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Result</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--warning)', fontWeight: 700 }}>
                      <Star size={16} fill="var(--warning)" /> {selectedInterview.score}/10
                    </div>
                    {selectedInterview.comment && <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>"{selectedInterview.comment}"</div>}
                  </div>
                ) : (
                  <form onSubmit={handleEvaluate} style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginTop: '0.5rem' }}>
                     <h4 style={{ marginBottom: '0.75rem', fontSize: '0.875rem' }}>Record Evaluation</h4>
                     <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                          <label className="form-label" style={{ fontSize: '0.7rem' }}>Score (1-10)</label>
                          <input type="number" required min="1" max="10" className="form-control" style={{ padding: '0.5rem' }} value={evalData.score} onChange={(e) => setEvalData({...evalData, score: e.target.value})} />
                        </div>
                        <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                          <label className="form-label" style={{ fontSize: '0.7rem' }}>Comment</label>
                          <input className="form-control" style={{ padding: '0.5rem' }} value={evalData.comment} onChange={(e) => setEvalData({...evalData, comment: e.target.value})} placeholder="Internal notes..." />
                        </div>
                     </div>
                     <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.5rem', fontSize: '0.8rem' }}>Submit Evaluation</button>
                  </form>
                )}
             </div>
             
             <button className="btn btn-secondary" style={{ width: '100%' }} onClick={() => { setSelectedInterview(null); setEvalData({score:'', comment:''}); }}>
                Close Window
             </button>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Interviews;
