import { useEffect, useMemo, useState } from 'react';

import api, { setAuthToken } from '../../api/client';
import { formatCurrency, formatNumber, riskBadgeClass } from '../../utils';

const DEFAULT_LOGIN = {
  email: 'demo-user@example.com',
  password: 'User1234!',
  ip_address: '1.1.1.1',
  region: 'KR-SEOUL',
};

const DEFAULT_ORDER = {
  stock_code: '005930',
  side: 'BUY',
  order_type: 'LIMIT',
  quantity: 10,
  price: 83500,
  device_id: 'device-main',
  ip_address: '1.1.1.1',
  region: 'KR-SEOUL',
};

export default function MtsDashboard() {
  const [token, setToken] = useState(localStorage.getItem('mts_token') || '');
  const [loginForm, setLoginForm] = useState(DEFAULT_LOGIN);
  const [profile, setProfile] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [orderForm, setOrderForm] = useState(DEFAULT_ORDER);
  const [amendOrderId, setAmendOrderId] = useState('');
  const [amendForm, setAmendForm] = useState({ quantity: 10, price: 83500, order_type: 'LIMIT' });
  const [authCodes, setAuthCodes] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setAuthToken(token);
    loadDashboard(token);
  }, []);

  async function login(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const { data } = await api.post('/auth/login', loginForm);
      localStorage.setItem('mts_token', data.access_token);
      setToken(data.access_token);
      setAuthToken(data.access_token);
      await loadDashboard(data.access_token);
      setMessage('사용자 세션 로그인 완료');
    } catch (err) {
      setError(err.response?.data?.error?.message || '로그인 실패');
    } finally {
      setLoading(false);
    }
  }

  async function loadDashboard(currentToken = token) {
    if (!currentToken) return;
    setLoading(true);
    setError('');
    try {
      setAuthToken(currentToken);
      const [meResponse, dashboardResponse] = await Promise.all([
        api.get('/auth/me'),
        api.get('/dashboard/me'),
      ]);
      setProfile(meResponse.data);
      setDashboard(dashboardResponse.data);
      setOrderForm((previous) => ({
        ...previous,
        account_id: dashboardResponse.data.account_id,
      }));
    } catch (err) {
      setError(err.response?.data?.error?.message || '대시보드 조회 실패');
    } finally {
      setLoading(false);
    }
  }

  async function submitOrder(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      await api.post('/orders', orderForm);
      setMessage('주문이 접수됐다. 최신 상태를 다시 불러온다.');
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.error?.message || '주문 실패');
    } finally {
      setLoading(false);
    }
  }

  async function cancelOrder(orderId) {
    setLoading(true);
    setError('');
    try {
      await api.post(`/orders/${orderId}/cancel`);
      setMessage(`주문 ${orderId} 취소 완료`);
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.error?.message || '주문 취소 실패');
    } finally {
      setLoading(false);
    }
  }

  async function amendOrder(event) {
    event.preventDefault();
    if (!amendOrderId) {
      setError('정정할 주문 ID를 입력해');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await api.post(`/orders/${amendOrderId}/amend`, amendForm);
      setMessage(`주문 ${amendOrderId} 정정 완료`);
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.error?.message || '주문 정정 실패');
    } finally {
      setLoading(false);
    }
  }

  async function verifyAdditionalAuth(orderId) {
    setLoading(true);
    setError('');
    try {
      await api.post(`/orders/${orderId}/additional-auth/verify`, { code: authCodes[orderId] || '' });
      setMessage(`주문 ${orderId} 추가인증 완료`);
      await loadDashboard();
    } catch (err) {
      setError(err.response?.data?.error?.message || '추가인증 실패');
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem('mts_token');
    setToken('');
    setProfile(null);
    setDashboard(null);
    setAuthToken(null);
    setMessage('사용자 세션 로그아웃 완료');
  }

  const summaryCards = useMemo(() => {
    if (!dashboard) return [];
    return [
      { label: '예수금', value: formatCurrency(dashboard.cash_balance) },
      { label: '보유 평가금액', value: formatCurrency(dashboard.portfolio_value) },
      { label: '총 평가자산', value: formatCurrency(dashboard.total_evaluation_amount) },
    ];
  }, [dashboard]);

  return (
    <section>
      <header className="page-header page-header-column">
        <div>
          <p className="eyebrow">USER MTS</p>
          <h2>모의투자 사용자 화면</h2>
          <p>실제 시세 기반 주문, 포트폴리오, 추가인증, 주문 정정/취소 흐름까지 바로 시연 가능하게 구성했다.</p>
        </div>
        {profile && (
          <div className="header-actions">
            <div className="pill">{profile.full_name} / {profile.role}</div>
            <button className="button button-secondary" onClick={loadDashboard}>새로고침</button>
            <button className="button button-secondary" onClick={logout}>로그아웃</button>
          </div>
        )}
      </header>

      {!profile ? (
        <article className="card form-card">
          <h3>사용자 로그인</h3>
          <form className="form-grid" onSubmit={login}>
            <label>
              Email
              <input value={loginForm.email} onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })} placeholder="환경변수에 설정한 사용자 계정" />
            </label>
            <label>
              Password
              <input type="password" value={loginForm.password} onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })} placeholder="환경변수에 설정한 비밀번호" />
            </label>
            <label>
              IP
              <input value={loginForm.ip_address} onChange={(event) => setLoginForm({ ...loginForm, ip_address: event.target.value })} />
            </label>
            <label>
              Region
              <input value={loginForm.region} onChange={(event) => setLoginForm({ ...loginForm, region: event.target.value })} />
            </label>
            <button className="button" disabled={loading} type="submit">로그인</button>
          </form>
        </article>
      ) : (
        <>
          <div className="card-grid">
            {summaryCards.map((item) => (
              <article className="card stat-card" key={item.label}>
                <h3>{item.label}</h3>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>

          <div className="two-column-grid">
            <article className="card form-card">
              <h3>신규 주문</h3>
              <form className="form-grid" onSubmit={submitOrder}>
                <label>
                  계좌 ID
                  <input value={orderForm.account_id || ''} readOnly />
                </label>
                <label>
                  종목코드
                  <select value={orderForm.stock_code} onChange={(event) => setOrderForm({ ...orderForm, stock_code: event.target.value })}>
                    {(dashboard?.watch_stocks || []).map((stock) => (
                      <option key={stock.stock_code} value={stock.stock_code}>{stock.stock_code} / {stock.stock_name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  매수/매도
                  <select value={orderForm.side} onChange={(event) => setOrderForm({ ...orderForm, side: event.target.value })}>
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </label>
                <label>
                  주문유형
                  <select value={orderForm.order_type} onChange={(event) => setOrderForm({ ...orderForm, order_type: event.target.value })}>
                    <option value="LIMIT">LIMIT</option>
                    <option value="MARKET">MARKET</option>
                  </select>
                </label>
                <label>
                  수량
                  <input type="number" value={orderForm.quantity} onChange={(event) => setOrderForm({ ...orderForm, quantity: Number(event.target.value) })} />
                </label>
                <label>
                  가격
                  <input type="number" value={orderForm.price} onChange={(event) => setOrderForm({ ...orderForm, price: Number(event.target.value) })} disabled={orderForm.order_type === 'MARKET'} />
                </label>
                <label>
                  Device ID
                  <input value={orderForm.device_id} onChange={(event) => setOrderForm({ ...orderForm, device_id: event.target.value })} />
                </label>
                <label>
                  Region
                  <input value={orderForm.region} onChange={(event) => setOrderForm({ ...orderForm, region: event.target.value })} />
                </label>
                <button className="button" disabled={loading} type="submit">주문 실행</button>
              </form>
            </article>

            <article className="card form-card">
              <h3>주문 정정</h3>
              <form className="form-grid" onSubmit={amendOrder}>
                <label>
                  주문 ID
                  <input value={amendOrderId} onChange={(event) => setAmendOrderId(event.target.value)} placeholder="정정할 주문 ID" />
                </label>
                <label>
                  수량
                  <input type="number" value={amendForm.quantity} onChange={(event) => setAmendForm({ ...amendForm, quantity: Number(event.target.value) })} />
                </label>
                <label>
                  가격
                  <input type="number" value={amendForm.price} onChange={(event) => setAmendForm({ ...amendForm, price: Number(event.target.value) })} />
                </label>
                <label>
                  주문유형
                  <select value={amendForm.order_type} onChange={(event) => setAmendForm({ ...amendForm, order_type: event.target.value })}>
                    <option value="LIMIT">LIMIT</option>
                    <option value="MARKET">MARKET</option>
                  </select>
                </label>
                <button className="button button-secondary" disabled={loading} type="submit">정정 실행</button>
              </form>

              <div className="note-box">
                <strong>추가인증 코드 입력</strong>
                <p>기본 seed는 환경변수 `ADDITIONAL_AUTH_CODE` 값을 사용한다.</p>
                {(dashboard?.pending_auth || []).map((item) => (
                  <div className="inline-form" key={item.order_id}>
                    <span>주문 {item.order_id}</span>
                    <input
                      placeholder="인증코드"
                      value={authCodes[item.order_id] || ''}
                      onChange={(event) => setAuthCodes({ ...authCodes, [item.order_id]: event.target.value })}
                    />
                    <button className="button button-secondary" type="button" onClick={() => verifyAdditionalAuth(item.order_id)}>인증</button>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <article className="card">
            <h3>보유 포지션</h3>
            <table>
              <thead>
                <tr><th>종목</th><th>수량</th><th>평단</th><th>현재가</th><th>평가금액</th><th>손익</th></tr>
              </thead>
              <tbody>
                {(dashboard?.positions || []).map((row) => (
                  <tr key={row.stock_code}>
                    <td>{row.stock_code} / {row.stock_name}</td>
                    <td>{formatNumber(row.quantity)}</td>
                    <td>{formatCurrency(row.avg_price)}</td>
                    <td>{formatCurrency(row.current_price)}</td>
                    <td>{formatCurrency(row.evaluation_amount)}</td>
                    <td className={row.profit_loss >= 0 ? 'text-profit' : 'text-loss'}>{formatCurrency(row.profit_loss)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <div className="two-column-grid">
            <article className="card">
              <h3>시장 감시 종목 / 현재가</h3>
              <table>
                <thead>
                  <tr><th>종목</th><th>현재가</th><th>거래량</th><th>감시여부</th></tr>
                </thead>
                <tbody>
                  {(dashboard?.watch_stocks || []).map((stock) => (
                    <tr key={stock.stock_code}>
                      <td>{stock.stock_code} / {stock.stock_name}</td>
                      <td>{formatCurrency(stock.current_price)}</td>
                      <td>{formatNumber(stock.volume)}</td>
                      <td><span className={`badge ${stock.is_monitored ? 'warning' : 'normal'}`}>{stock.is_monitored ? 'WATCH' : 'NORMAL'}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>

            <article className="card">
              <h3>최근 주문</h3>
              <table>
                <thead>
                  <tr><th>ID</th><th>종목</th><th>유형</th><th>상태</th><th>리스크</th><th>액션</th></tr>
                </thead>
                <tbody>
                  {(dashboard?.recent_orders || []).map((order) => (
                    <tr key={order.id}>
                      <td>{order.id}</td>
                      <td>{order.stock_code}</td>
                      <td>{order.side} / {order.order_type}</td>
                      <td>{order.status} ({order.filled_quantity}/{order.quantity})</td>
                      <td><span className={`badge ${riskBadgeClass(order.risk_level)}`}>{order.risk_level}</span></td>
                      <td>
                        <div className="action-stack">
                          <button className="text-button" type="button" onClick={() => { setAmendOrderId(String(order.id)); setAmendForm({ quantity: order.quantity, price: order.price, order_type: order.order_type }); }}>정정선택</button>
                          <button className="text-button danger" type="button" onClick={() => cancelOrder(order.id)}>취소</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          </div>
        </>
      )}

      {message && <div className="toast success">{message}</div>}
      {error && <div className="toast error">{error}</div>}
      {loading && <div className="loading-state">처리 중...</div>}
    </section>
  );
}
