export default function Dashboard() {
  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 20 }}>工作台</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
        <StatCard title="模板总数" value="0" />
        <StatCard title="本月生成文档" value="0" />
        <StatCard title="进行中任务" value="0" />
        <StatCard title="已完成任务" value="0" />
      </div>
    </div>
  )
}

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <div style={{ background: '#fff', borderRadius: 8, padding: 20, border: '1px solid var(--border)' }}>
      <div style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 32, fontWeight: 600 }}>{value}</div>
    </div>
  )
}
