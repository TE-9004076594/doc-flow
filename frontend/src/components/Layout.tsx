import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { clearToken } from '../services/api'

const navItems = [
  { path: '/', label: '工作台', icon: '📊' },
  { path: '/templates', label: '模板中心', icon: '📄' },
  { path: '/generate', label: '文档生成', icon: '🔧' },
  { path: '/tasks', label: '批量任务', icon: '📋' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    clearToken()
    navigate('/login', { replace: true })
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside
        style={{
          width: 'var(--sidebar-width)',
          background: 'var(--bg-white)',
          borderRight: '1px solid var(--border)',
          padding: '16px 0',
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            padding: '0 20px 20px',
            fontSize: 18,
            fontWeight: 700,
            borderBottom: '1px solid var(--border)',
            marginBottom: 8,
          }}
        >
          📄 Doc Flow
        </div>
        <nav>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 20px',
                color: isActive ? 'var(--primary)' : 'var(--text)',
                background: isActive ? 'rgba(22, 119, 255, 0.06)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                borderRight: isActive ? '3px solid var(--primary)' : '3px solid transparent',
                fontSize: 14,
              })}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div style={{ flex: 1 }} />
        <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border)' }}>
          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              padding: '8px 0',
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: 6,
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            退出登录
          </button>
        </div>
      </aside>
      <main
        style={{
          marginLeft: 'var(--sidebar-width)',
          flex: 1,
          padding: 24,
        }}
      >
        {children}
      </main>
    </div>
  )
}
