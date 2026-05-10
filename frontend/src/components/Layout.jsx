import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Briefcase, 
  CalendarDays, 
  LogOut, 
  UserCircle,
  BriefcaseBusiness
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Candidates', href: '/candidates', icon: Users },
    { name: 'Vacancies', href: '/vacancies', icon: Briefcase },
    { name: 'Interviews', href: '/interviews', icon: CalendarDays },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <BriefcaseBusiness size={28} className="gradient-text" style={{color: 'var(--primary)'}}/>
        <span className="gradient-text">HR Core</span>
      </div>
      
      <nav className="sidebar-nav">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href || 
                          (item.href !== '/' && location.pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      <div className="sidebar-footer">
        <button onClick={logout} className="nav-item" style={{ width: '100%', background: 'none', border: 'none', color: '#ef4444' }}>
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

const Header = () => {
  const { user } = useAuth();

  return (
    <header className="header">
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Overview</h2>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>{user?.username || 'Admin'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>HR Manager</div>
        </div>
        <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--primary-light)', display: 'flex', alignItems: 'center', justify: 'center', color: 'var(--primary)' }}>
          <UserCircle size={36} strokeWidth={1.5} />
        </div>
      </div>
    </header>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Header />
        <div className="page-content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
