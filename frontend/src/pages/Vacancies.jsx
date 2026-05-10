import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { Briefcase, Building2, MapPin, Plus } from 'lucide-react';
import { motion } from 'framer-motion';

const Vacancies = () => {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newVac, setNewVac] = useState({ title: '', department: '', description: '' });
  
  const navigate = useNavigate();

  const fetchVacancies = async () => {
    try {
      const res = await api.get('/vacancies/');
      setVacancies(res.data.results || res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVacancies();
  }, []);

  const handleCloseVacancy = async (id) => {
    if (!window.confirm("Are you sure you want to close this vacancy?")) return;
    try {
      await api.post(`/vacancies/${id}/close/`);
      fetchVacancies();
    } catch (err) {
      alert("Failed to close vacancy.");
    }
  };

  const handleCreateVacancy = async (e) => {
    e.preventDefault();
    try {
      await api.post('/vacancies/', newVac);
      setNewVac({ title: '', department: '', description: '' });
      setIsModalOpen(false);
      fetchVacancies();
    } catch (err) {
      alert("Failed to create vacancy.");
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Vacancies</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Active job positions available.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary">
          <Plus size={18} /> Add Vacancy
        </button>
      </div>
      
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {(vacancies.length > 0 ? vacancies : [
            { id: 1, title: 'Senior React Developer', department: 'Engineering', is_open: true },
            { id: 2, title: 'Product Designer', department: 'Product', is_open: true },
            { id: 3, title: 'Python Backend Engineer', department: 'Engineering', is_open: true }
          ]).map((vacancy) => (
            <motion.div 
              key={vacancy.id}
              whileHover={{ y: -4 }}
              className="glass-card" 
              style={{ padding: '1.5rem' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ padding: '0.5rem', background: 'rgba(99,102,241,0.1)', borderRadius: '8px', color: 'var(--primary)' }}>
                  <Briefcase size={24} />
                </div>
                <span className={`badge badge-${vacancy.is_open ? 'success' : 'neutral'}`} style={{ fontSize: '0.65rem' }}>
                  {vacancy.is_open ? 'Active' : 'Closed'}
                </span>
              </div>
              
              <h3 style={{ marginBottom: '0.5rem', fontSize: '1.1rem' }}>{vacancy.title}</h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Building2 size={14} /> {vacancy.department || 'General'}
                </div>
              </div>
              
              <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                 <button 
                   onClick={() => navigate(`/candidates?search=${encodeURIComponent(vacancy.title)}`)}
                   className="btn btn-secondary" 
                   style={{ flex: 1, fontSize: '0.8rem' }}
                 >
                   Candidates
                 </button>
                 {vacancy.is_open && (
                   <button 
                     onClick={() => handleCloseVacancy(vacancy.id)}
                     className="btn btn-primary" 
                     style={{ flex: 1, fontSize: '0.8rem', background: 'var(--danger)', boxShadow: 'none' }}
                   >
                     Close
                   </button>
                 )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, backdropFilter: 'blur(5px)'
        }} onClick={() => setIsModalOpen(false)}>
          <motion.div 
             initial={{ scale: 0.9, opacity: 0 }}
             animate={{ scale: 1, opacity: 1 }}
             className="glass-card" 
             style={{ padding: '2rem', maxWidth: '450px', width: '90%' }}
             onClick={(e) => e.stopPropagation()}
          >
             <h2 style={{ marginBottom: '1.5rem' }}>Open New Vacancy</h2>
             <form onSubmit={handleCreateVacancy} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className="form-group">
                   <label className="form-label">Job Title*</label>
                   <input className="form-control" required placeholder="e.g. DevOps Lead" value={newVac.title} onChange={(e) => setNewVac({...newVac, title: e.target.value})} />
                </div>
                <div className="form-group">
                   <label className="form-label">Department</label>
                   <input className="form-control" placeholder="e.g. Product" value={newVac.department} onChange={(e) => setNewVac({...newVac, department: e.target.value})} />
                </div>
                <div className="form-group">
                   <label className="form-label">Brief Description</label>
                   <textarea className="form-control" rows="3" style={{ resize: 'none' }} value={newVac.description} onChange={(e) => setNewVac({...newVac, description: e.target.value})} />
                </div>
                
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                   <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setIsModalOpen(false)}>Cancel</button>
                   <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Create</button>
                </div>
             </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Vacancies;
