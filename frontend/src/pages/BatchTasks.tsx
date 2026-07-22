import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface BatchTask {
  id: string
  title: string
  status: string
  total_count: number
  completed_count: number
  failed_count: number
  created_at: string
}

export default function BatchTasks() {
  const [tasks, setTasks] = useState<BatchTask[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState<string | null>(null)
  const [taskDetail, setTaskDetail] = useState<any>(null)

  const loadTasks = () => {
    setLoading(true)
    api.getBatchTasks().then((data: any) => setTasks(data || []))
      .catch(console.error).finally(() => setLoading(false))
  }

  useEffect(() => { loadTasks() }, [])

  useEffect(() => {
    if (!selectedTask) { setTaskDetail(null); return }
    api.getBatchTask(selectedTask).then(setTaskDetail).catch(console.error)
  }, [selectedTask])

  const handleCancel = async (id: string) => {
    await api.cancelBatchTask(id)
    loadTasks()
  }

  const handleRetry = async (id: string) => {
    await api.retryBatchTask(id)
    loadTasks()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1 style={{ fontSize: 24, fontWeight: 600 }}>批量任务</h1>
        <button onClick={loadTasks}
          style={{ background: 'var(--bg)', border: '1px solid var(--border)', padding: '8px 16px', borderRadius: 6, fontSize: 13 }}>
          ↻ 刷新
        </button>
      </div>

      {loading ? <div style={{ color: 'var(--text-secondary)' }}>加载中...</div> : tasks.length === 0 ? (
        <div style={{ background: '#fff', borderRadius: 8, padding: 40, textAlign: 'center', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
          <h3 style={{ marginBottom: 8 }}>暂无批量任务</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>通过批量生成功能创建任务</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: selectedTask ? '1fr 1fr' : '1fr', gap: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {tasks.map(task => (
              <div key={task.id}
                onClick={() => setSelectedTask(task.id)}
                style={{
                  background: '#fff', borderRadius: 8, padding: 16, border: '1px solid var(--border)',
                  cursor: 'pointer',
                  borderColor: selectedTask === task.id ? 'var(--primary)' : 'var(--border)',
                }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{task.title}</div>
                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                      {task.completed_count}/{task.total_count} 完成 · {task.failed_count} 失败
                    </div>
                  </div>
                  <span style={{
                    padding: '2px 10px', borderRadius: 12, fontSize: 12,
                    background: task.status === 'completed' ? '#f6ffed' : task.status === 'failed' ? '#fff2f0' : '#fffbe6',
                    color: task.status === 'completed' ? 'var(--success)' : task.status === 'failed' ? 'var(--error)' : 'var(--warning)',
                  }}>
                    {{ pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败', cancelled: '已取消' }[task.status] || task.status}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {taskDetail && (
            <div style={{ background: '#fff', borderRadius: 8, padding: 16, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>任务详情</h3>
              <div style={{ fontSize: 14, marginBottom: 12 }}>
                <div style={{ marginBottom: 4 }}>状态：{taskDetail.status}</div>
                <div style={{ marginBottom: 4 }}>总计：{taskDetail.total_count} 条</div>
                <div style={{ marginBottom: 4 }}>已完成：{taskDetail.completed_count}</div>
                <div style={{ marginBottom: 12 }}>失败：{taskDetail.failed_count}</div>
              </div>

              <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                {taskDetail.status === 'processing' && (
                  <button onClick={() => handleCancel(taskDetail.id)}
                    style={{ background: 'var(--error)', color: '#fff', padding: '6px 16px', borderRadius: 6, fontSize: 13 }}>
                    取消任务
                  </button>
                )}
                {taskDetail.failed_count > 0 && (
                  <button onClick={() => handleRetry(taskDetail.id)}
                    style={{ background: 'var(--warning)', color: '#fff', padding: '6px 16px', borderRadius: 6, fontSize: 13 }}>
                    重试失败项
                  </button>
                )}
              </div>

              {taskDetail.items && taskDetail.items.length > 0 && (
                <>
                  <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>处理记录</h4>
                  <div style={{ maxHeight: 300, overflow: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                          <th style={{ textAlign: 'left', padding: '6px 8px' }}>行</th>
                          <th style={{ textAlign: 'left', padding: '6px 8px' }}>状态</th>
                          <th style={{ textAlign: 'left', padding: '6px 8px' }}>错误</th>
                        </tr>
                      </thead>
                      <tbody>
                        {taskDetail.items.map((item: any, i: number) => (
                          <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                            <td style={{ padding: '6px 8px' }}>{item.row + 1}</td>
                            <td style={{ padding: '6px 8px' }}>{item.status}</td>
                            <td style={{ padding: '6px 8px', color: 'var(--error)' }}>{item.error || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
