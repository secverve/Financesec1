const quotes = [
  { stockCode: '005930', stockName: '삼성전자', price: '83,500', status: '정상' },
  { stockCode: '000660', stockName: 'SK하이닉스', price: '201,000', status: '주의' },
];

export default function MtsDashboard() {
  return (
    <section>
      <header className="page-header">
        <div>
          <h2>모의투자 MTS</h2>
          <p>실제 시세 기반 가상 주문, 계좌, 포트폴리오 현황</p>
        </div>
      </header>
      <div className="card-grid">
        <article className="card stat-card">
          <h3>예수금</h3>
          <strong>₩50,000,000</strong>
        </article>
        <article className="card stat-card">
          <h3>평가손익</h3>
          <strong>+₩1,240,000</strong>
        </article>
      </div>
      <article className="card">
        <h3>관심 종목</h3>
        <table>
          <thead>
            <tr><th>종목코드</th><th>종목명</th><th>현재가</th><th>상태</th></tr>
          </thead>
          <tbody>
            {quotes.map((row) => (
              <tr key={row.stockCode}>
                <td>{row.stockCode}</td>
                <td>{row.stockName}</td>
                <td>{row.price}</td>
                <td><span className={`badge ${row.status === '주의' ? 'warning' : 'normal'}`}>{row.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}
