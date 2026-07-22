import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import UploadTemplateModal from '../components/UploadTemplateModal'

interface Template {
  id: string
  name: string
  category: string
  status: string
  version: string
  updated_at: string
}

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [showUpload, setShowUpload] = useState(false)

  const loadTemplates = () => {
    setLoading(true)
    api.getTemplates().then(setTemplates).catch(console.error).finally(() => setLoading(false))
  }

  useEffect(() => {
    loadTemplates()
  }, [])

  const handleUploadComplete = () => {
    setShowUpload(false)
    loadTemplates()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1 style={{ fontSize: 24, fontWeight: 600 }}>模板中心</h1>
        <button onClick={() => setShowUpload(true)}
          style={{ background: 'var(--primary)', color: '#fff', padding: '8px 20px', borderRadius: 6, fontSize: 14 }}>
          + 上传模板
        </button>
      </div>

      {showUpload && <UploadTemplateModal onClose={handleUploadComplete} />}

      {loading ? (
        <div style={{ color: 'var(--text-secondary)' }}>加载中...</div>
      ) : templates.length === 0 ? (
        <div style={{ background: '#fff', borderRadius: 8, padding: 40, textAlign: 'center', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📄</div>
          <h3 style={{ marginBottom: 8 }}>暂无模板</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>上传您的第一个 Word 模板开始使用</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {templates.map((t) => (
            <Link key={t.id} to={`/templates/${t.id}`}
              style={{ display: 'block', background: '#fff', borderRadius: 8, padding: 16, border: '1px solid var(--border)', color: 'inherit' }}>
              <div style={{ fontWeight: 600 }}>{t.name}</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                {t.category} · v{t.version} · {t.updated_at}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
