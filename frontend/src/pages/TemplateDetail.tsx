import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'

interface TemplateDetail {
  id: string
  name: string
  description: string | null
  category: string | null
  tags: string[]
  status: string
  current_version: number
  updated_at: string
}

interface Variable {
  id?: string
  name: string
  label: string
  var_type: string
  default_value: string | null
  description: string | null
  enum_options: string[] | null
  is_required: boolean
}

const VAR_TYPES = ['text', 'number', 'date', 'enum', 'boolean', 'object', 'list']

export default function TemplateDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [template, setTemplate] = useState<TemplateDetail | null>(null)
  const [variables, setVariables] = useState<Variable[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [activeTab, setActiveTab] = useState<'info' | 'variables' | 'preview'>('info')

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.getTemplate(id),
      api.getVariables(id),
    ]).then(([tpl, vars]) => {
      setTemplate(tpl as any)
      setVariables((vars as any) || [])
    }).catch(console.error).finally(() => setLoading(false))
  }, [id])

  const addVariable = () => {
    setVariables([...variables, {
      name: '',
      label: '',
      var_type: 'text',
      default_value: null,
      description: null,
      enum_options: null,
      is_required: false,
    }])
    setEditing(true)
  }

  const updateVariable = (index: number, field: string, value: any) => {
    const updated = [...variables]
    ;(updated[index] as any)[field] = value
    setVariables(updated)
  }

  const removeVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index))
  }

  const saveVariables = async () => {
    if (!id) return
    try {
      await api.updateVariables(id, variables)
      setEditing(false)
    } catch (err) {
      console.error('Failed to save variables:', err)
    }
  }

  const handleGenerate = () => {
    navigate(`/generate/${id}`)
  }

  if (loading) return <div>加载中...</div>
  if (!template) return <div>模板不存在</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 600 }}>{template.name}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            {template.category} · v{template.current_version} · {template.status}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={handleGenerate}
            style={{ background: 'var(--primary)', color: '#fff', padding: '8px 20px', borderRadius: 6, fontSize: 14 }}>
            生成文档
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
        {(['info', 'variables', 'preview'] as const).map(tab => (
          <button key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 16px',
              background: 'none',
              color: activeTab === tab ? 'var(--primary)' : 'var(--text-secondary)',
              borderBottom: activeTab === tab ? '2px solid var(--primary)' : '2px solid transparent',
              fontWeight: activeTab === tab ? 600 : 400,
              fontSize: 14,
            }}>
            {{ info: '基本信息', variables: '变量配置', preview: '模板预览' }[tab]}
          </button>
        ))}
      </div>

      {activeTab === 'info' && (
        <div style={{ background: '#fff', borderRadius: 8, padding: 24, border: '1px solid var(--border)' }}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>描述</label>
            <p>{template.description || '暂无描述'}</p>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>标签</label>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {template.tags.length > 0 ? template.tags.map((tag, i) => (
                <span key={i} style={{ background: '#f0f5ff', color: 'var(--primary)', padding: '2px 10px', borderRadius: 12, fontSize: 12 }}>
                  {tag}
                </span>
              )) : <span style={{ color: 'var(--text-secondary)', fontSize: 14 }}>无标签</span>}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'variables' && (
        <div style={{ background: '#fff', borderRadius: 8, padding: 24, border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 600 }}>变量列表（{variables.length}）</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={addVariable}
                style={{ background: 'var(--bg)', color: 'var(--text)', padding: '6px 16px', borderRadius: 6, border: '1px solid var(--border)', fontSize: 13 }}>
                + 添加变量
              </button>
              {editing && (
                <button onClick={saveVariables}
                  style={{ background: 'var(--primary)', color: '#fff', padding: '6px 16px', borderRadius: 6, fontSize: 13 }}>
                  保存
                </button>
              )}
            </div>
          </div>

          {variables.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>
              暂无变量，点击"添加变量"开始配置
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', fontSize: 13, color: 'var(--text-secondary)' }}>
                  <th style={{ textAlign: 'left', padding: '8px 12px' }}>变量名</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px' }}>显示名</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px' }}>类型</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px' }}>必填</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px' }}>默认值</th>
                  <th style={{ width: 60 }}></th>
                </tr>
              </thead>
              <tbody>
                {variables.map((v, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '8px 12px' }}>
                      <input value={v.name} onChange={e => updateVariable(i, 'name', e.target.value)}
                        style={{ fontSize: 13, padding: '4px 8px' }} />
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <input value={v.label} onChange={e => updateVariable(i, 'label', e.target.value)}
                        style={{ fontSize: 13, padding: '4px 8px' }} />
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <select value={v.var_type} onChange={e => updateVariable(i, 'var_type', e.target.value)}
                        style={{ fontSize: 13, padding: '4px 8px', width: 'auto' }}>
                        {VAR_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <input type="checkbox" checked={v.is_required}
                        onChange={e => updateVariable(i, 'is_required', e.target.checked)} />
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <input value={v.default_value || ''} onChange={e => updateVariable(i, 'default_value', e.target.value)}
                        style={{ fontSize: 13, padding: '4px 8px' }} />
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <button onClick={() => removeVariable(i)}
                        style={{ color: 'var(--error)', background: 'none', fontSize: 16 }}>×</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'preview' && (
        <div style={{ background: '#fff', borderRadius: 8, padding: 24, border: '1px solid var(--border)', textAlign: 'center', color: 'var(--text-secondary)' }}>
          模板预览功能（需服务端支持 OOXML → HTML 渲染）
        </div>
      )}
    </div>
  )
}
