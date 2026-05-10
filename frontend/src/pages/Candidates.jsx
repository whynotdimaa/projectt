import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import { Search, Plus, MoreVertical, Mail, Phone, ExternalLink, Trash2, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';

const getStatusBadge = (status) => {
  switch (status) {
    case 'NEW': return <span className="badge badge-info">New</span>;
    case 'SCREENING': return <span className="badge badge-warning">Screening</span>;
    case 'INTERVIEW': return <span className="badge badge-primary" style={{background: 'rgba(168, 85, 247, 0.2)', color: 'var(--accent)'}}>Interview</span>;
    case 'OFFER': return <span className="badge badge-warning" style={{color: '#fbbf24'}}>Offer</span>;
    case 'HIRED': return <span className="badge badge-success">Hired</span>;
    case 'REJECTED': return <span className="badge badge-danger">Rejected</span>;
    default: return <span className="badge badge-neutral">{status}</span>;
  }
};

const Candidates = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';

  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(initialSearch);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', email: '', phone: '', resume_url: '', desired_position: ''
  });

  const fetchCandidates = async () => {
    try {
      const res = await api.get('/candidates/');
      setCandidates(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to load candidates", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (searchTerm) {
       setSearchParams({ search: searchTerm }, { replace: true });
    } else if (initialSearch && !searchTerm) {
       setSearchParams({}, { replace: true });
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleCreateCandidate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.post('/candidates/', formData);
      setIsModalOpen(false);
      setFormData({ first_name: '', last_name: '', email: '', phone: '', resume_url: '', desired_position: '' });
      fetchCandidates();
    } catch (err) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to add candidate';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleChangeStatus = async (id, nextStatus) => {
    try {
      await api.patch(`/candidates/${id}/status/`, { status: nextStatus });
      fetchCandidates();
    } catch (err) {
      alert(err.response?.data?.detail || err.response?.data?.error || "Invalid status transition. Candidate flow must follow NEW -> SCREENING -> INTERVIEW -> OFFER -> HIRED.");
    }
  };

  const handleDeleteCandidate = async (id) => {
    if (!window.confirm("Are you sure you want to remove this candidate?")) return;
    try {
      await api.delete(`/candidates/${id}/`);
      fetchCandidates();
    } catch (err) {
      alert("Failed to delete candidate.");
    }
  };

  const [activeActionMenu, setActiveActionMenu] = useState(null);

  const filteredCandidates = candidates.filter(c => 
    (c.first_name || "").toLowerCase().includes(searchTerm.toLowerCase()) || 
    (c.last_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.email || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.desired_position || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Candidates</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage your candidate pipeline</p>
        </div>
        <button onClick={() => { setError(''); setIsModalOpen(true); }} className="btn btn-primary">
          <Plus size={18} /> Add Candidate
        </button>
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '1rem' }}>
          <div style={{ position: 'relative', flex: 1, maxWidth: '400px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              placeholder="Search candidates..." 
              className="form-control" 
              style={{ paddingLeft: '2.5rem', width: '100%' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading candidates...</div>
          ) : filteredCandidates.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No candidates found.</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Contacts</th>
                  <th>Current Status</th>
                  <th>Applied On</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCandidates.map((candidate, index) => (
                  <motion.tr 
                    key={candidate.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                  >
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{ 
                          width: 36, height: 36, borderRadius: '50%', 
                          background: 'var(--bg-card-hover)', 
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 600, color: 'var(--primary)', fontSize: '0.875rem'
                        }}>
                          {candidate.first_name[0]}{candidate.last_name[0]}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600 }}>{candidate.first_name} {candidate.last_name}</div>
                          {candidate.resume_url && (
                            <a href={candidate.resume_url} target="_blank" style={{ fontSize: '0.75rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                              Resume <ExternalLink size={10} />
                            </a>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Mail size={12} /> {candidate.email}</div>
                        {candidate.phone && <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Phone size={12} /> {candidate.phone}</div>}
                      </div>
                    </td>
                    <td>
                      <div style={{ position: 'relative', display: 'inline-block' }}>
                        <select 
                          value={candidate.status}
                          onChange={(e) => handleChangeStatus(candidate.id, e.target.value)}
                          style={{
                            appearance: 'none',
                            WebkitAppearance: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '0.25rem 1.5rem 0.25rem 0.75rem',
                            borderRadius: '99px',
                            background: 'rgba(255,255,255,0.05)',
                            color: 'var(--text-primary)',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            border: '1px solid rgba(255,255,255,0.1)'
                          }}
                        >
                          <option value="NEW">NEW</option>
                          <option value="SCREENING">SCREENING</option>
                          <option value="INTERVIEW">INTERVIEW</option>
                          <option value="OFFER">OFFER</option>
                          <option value="HIRED">HIRED</option>
                          <option value="REJECTED">REJECTED</option>
                        </select>
                        <ChevronDown size={12} style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                      </div>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {candidate.created_at ? new Date(candidate.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button 
                          onClick={() => handleDeleteCandidate(candidate.id)}
                          style={{ background: 'transparent', color: 'rgba(239,68,68,0.7)', padding: '4px', cursor: 'pointer' }}
                          title="Delete Candidate"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Creation Modal */}
      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, backdropFilter: 'blur(5px)', overflowY: 'auto', padding: '2rem 0'
        }} onClick={() => setIsModalOpen(false)}>
          <motion.div 
             initial={{ scale: 0.9, opacity: 0 }}
             animate={{ scale: 1, opacity: 1 }}
             className="glass-card" 
             style={{ padding: '2rem', maxWidth: '500px', width: '90%', maxHeight: '90vh', overflowY: 'auto' }}
             onClick={(e) => e.stopPropagation()}
          >
             <h2 style={{ marginBottom: '1.5rem' }}>Add New Candidate</h2>
             
             {error && <div style={{ color: 'var(--danger)', fontSize: '0.8rem', marginBottom: '1rem', background: 'rgba(239,68,68,0.1)', padding: '0.75rem', borderRadius: '8px' }}>{error}</div>}
             
             <form onSubmit={handleCreateCandidate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                   <div className="form-group">
                      <label className="form-label">First Name*</label>
                      <input className="form-control" required value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})} />
                   </div>
                   <div className="form-group">
                      <label className="form-label">Last Name*</label>
                      <input className="form-control" required value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})} />
                   </div>
                </div>
                <div className="form-group">
                   <label className="form-label">Email*</label>
                   <input type="email" className="form-control" required value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
                </div>
                <div className="form-group">
                   <label className="form-label">Phone</label>
                   <input className="form-control" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
                </div>
                <div className="form-group">
                   <label className="form-label">Desired Position</label>
                   <input className="form-control" value={formData.desired_position} onChange={(e) => setFormData({...formData, desired_position: e.target.value})} placeholder="e.g. Senior Python dev" />
                </div>
                <div className="form-group">
                   <label className="form-label">Resume URL</label>
                   <input type="url" className="form-control" value={formData.resume_url} onChange={(e) => setFormData({...formData, resume_url: e.target.value})} placeholder="https://..." />
                </div>
                
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                   <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setIsModalOpen(false)}>Cancel</button>
                   <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
                      {saving ? 'Saving...' : 'Create'}
                   </button>
                </div>
             </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Candidates;
