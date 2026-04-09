const events = [
  {
    id: 1,
    riskLevel: 'CRITICAL',
    user: 'user@example.com',
    stock: '삼성전자',
    summary: '신규 디바이스에서 최근 평균 주문금액 대비 8.3배 높은 주문이 접수되었습니다.',
    action: '검토 필요',
  },
  {
    id: 2,
    riskLevel: 'SUSPICIOUS',
    user: 'user2@example.com',
    stock: '감시종목',
    summary: '해외 IP 로그인 후 5분 내 감시종목에 대한 고빈도 주문이 발생했습니다.',
    action: '추가인증',
  },
];

export default function AdminDashboard() {
  return (
    <section>
      <header className="page-header">
        <div>
          <h2>관리자 운영 콘솔</h2>
          <p>위험 이벤트, 룰 히트, 관리자 조치 이력</p>
        </div>
      </header>
      <div className="card-grid">
        <article className="card stat-card"><h3>일일 탐지 건수</h3><strong>24</strong></article>
        <article className="card stat-card"><h3>CRITICAL</h3><strong>3</strong></article>
        <article className="card stat-card"><h3>동일 IP 다계정</h3><strong>2</strong></article>
      </div>
      <article className="card">
        <h3>위험 이벤트</h3>
        <table>
          <thead>
            <tr><th>ID</th><th>위험도</th><th>사용자</th><th>종목</th><th>탐지 사유</th><th>조치</th></tr>
          </thead>
          <tbody>
            {events.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td><span className={`badge ${row.riskLevel.toLowerCase()}`}>{row.riskLevel}</span></td>
                <td>{row.user}</td>
                <td>{row.stock}</td>
                <td>{row.summary}</td>
                <td>{row.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}
