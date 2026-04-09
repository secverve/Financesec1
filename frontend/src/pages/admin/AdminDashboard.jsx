import { useEffect, useState } from 'react';

import api, { setAuthToken } from '../../api/client';
import { formatNumber, riskBadgeClass } from '../../utils';

const DEFAULT_LOGIN = {
  email: 'demo-admin@example.com',
  password: 'Admin1234!',
  ip_address: '10.10.10.10',
  region: 'KR-SEOUL',
};

export default function AdminDashboard() {
  const [token, setToken] = useState(localStorage.getItem('admin_token') || '');
  const [loginForm, setLoginForm] = useState(DEFAULT_LOGIN);
  const [profile, setProfile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);
  const [riskLevelFilter, setRiskLevelFilter] = useState('');
  const [lockUserId, setLockUserId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    setAuthToken(token);
    loadAdminConsole(token, riskLevelFilter);
  }, []);

  async function login(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data } = await api.post('/auth/login', loginForm);
      localStorage.setItem('admin_token', data.access_token);
      setToken(data.access_token);
      setAuthToken(data.access_token);
      await loadAdminConsole(data.access_token, riskLevelFilter);
      setMessage('관리자 세션 로그인 완료');
    } catch (err) {
      setError(err.response?.data?.error?.message || '로그인 실패');
    } finally {
      setLoading(false);
    }
  }

  async function loadAdminConsole(currentToken = token, currentFilter = riskLevelFilter) {
    if (!currentToken) return;
    setLoading(true);
    setError('');
    try {
      setAuthToken(currentToken);
      const [meResponse, summaryResponse, eventsResponse] = await Promise.all([
        api.get('/auth/me'),
        api.get('/dashboard/admin-summary'),
        api.get('/admin/risk-events', { params: currentFilter ? { risk_level: currentFilter } : {} }),
      ]);
      setProfile(meResponse.data);
      setSummary(summaryResponse.data);
      setEvents(eventsResponse.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || '관리자 콘솔 조회 실패');
    } finally {
      setLoading(false);
    }
  }

  async function takeAction(riskEventId, actionType) {
    setLoading(true);
    setError('');
    try {
      await api.post(`/admin/risk-events/${riskEventId}/actions`, { action_type: actionType });
      setMessage(`위험 이벤트 ${riskEventId} ${actionType} 처리 완료`);
      await loadAdminConsole();
    } catch (err) {
      setError(err.response?.data?.error?.message || '관리자 조치 실패');
    } finally {
      setLoading(false);
    }
  }

  async function lockUser(isLocked) {
    if (!lockUserId) {
      setError('사용자 ID를 입력해');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await api.post(`/admin/users/${lockUserId}/${isLocked ? 'lock' : 'unlock'}`);
      setMessage(`사용자 ${lockUserId} ${isLocked ? '잠금' : '잠금해제'} 완료`);
      await loadAdminConsole();
    } catch (err) {
      setError(err.response?.data?.error?.message || '계정 상태 변경 실패');
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem('admin_token');
    setToken('');
    setProfile(null);
    setSummary(null);
    setEvents([]);
    setAuthToken(null);
    setMessage('관리자 세션 로그아웃 완료');
  }

  return (
    <section>
      <header className="page-header page-header-column">
        <div>
          <p className="eyebrow">ADMIN CONSOLE</p>
          <h2>이상거래탐지 운영 콘솔</h2>
          <p>위험 이벤트 집계, 리스크 필터링, 승인/차단/추가인증 요구, 계정 잠금까지 한 화면에서 시연 가능하다.</p>
        </div>
        {profile && (
          <div className="header-actions">
            <div className="pill">{profile.full_name} / {profile.role}</div>
            <button className="button button-secondary" onClick={() => loadAdminConsole()}>새로고침</button>
            <button className="button button-secondary" onClick={logout}>로그아웃</button>
          </div>
        )}
      </header>

      {!profile ? (
        <article className="card form-card">
          <h3>관리자 로그인</h3>
          <form className="form-grid" onSubmit={login}>
            <label>
              Email
              <input value={loginForm.email} onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })} placeholder="환경변수에 설정한 관리자 계정" />
            </label>
            <label>
              Password
              <input type="password" value={loginForm.password} onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })} placeholder="환경변수에 설정한 관리자 비밀번호" />
            </label>
            <label>
              IP
              <input value={loginForm.ip_address} onChange={(event) => setLoginForm({ ...loginForm, ip_address: event.target.value })} />
            </label>
            <label>
              Region
              <input value={loginForm.region} onChange={(event) => setLoginForm({ ...loginForm, region: event.target.value })} />
            </label>
            <button className="button" disabled={loading} type="submit">관리자 로그인</button>
          </form>
        </article>
      ) : (
        <>
          <div className="card-grid">
            <article className="card stat-card"><h3>총 위험 이벤트</h3><strong>{formatNumber(summary?.total_events)}</strong></article>
            <article className="card stat-card"><h3>미해결 이벤트</h3><strong>{formatNumber(summary?.open_events)}</strong></article>
            <article className="card stat-card"><h3>CRITICAL</h3><strong>{formatNumber(summary?.critical_events)}</strong></article>
            <article className="card stat-card"><h3>SUSPICIOUS</h3><strong>{formatNumber(summary?.suspicious_events)}</strong></article>
            <article className="card stat-card"><h3>보류 주문</h3><strong>{formatNumber(summary?.held_orders)}</strong></article>
            <article className="card stat-card"><h3>동일 IP 다계정</h3><strong>{formatNumber(summary?.same_ip_multi_account_events)}</strong></article>
          </div>

          <div className="two-column-grid">
            <article className="card form-card">
              <h3>이벤트 필터 / 계정 제어</h3>
              <div className="form-grid compact-grid">
                <label>
                  위험도 필터
                  <select value={riskLevelFilter} onChange={(event) => setRiskLevelFilter(event.target.value)}>
                    <option value="">ALL</option>
                    <option value="NORMAL">NORMAL</option>
                    <option value="CAUTION">CAUTION</option>
                    <option value="SUSPICIOUS">SUSPICIOUS</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </label>
                <button className="button button-secondary" type="button" onClick={() => loadAdminConsole(token, riskLevelFilter)}>필터 적용</button>
                <label>
                  사용자 ID
                  <input value={lockUserId} onChange={(event) => setLockUserId(event.target.value)} placeholder="잠글 사용자 ID" />
                </label>
                <div className="button-row">
                  <button className="button button-danger" type="button" onClick={() => lockUser(true)}>잠금</button>
                  <button className="button button-secondary" type="button" onClick={() => lockUser(false)}>잠금해제</button>
                </div>
              </div>
            </article>

            <article className="card">
              <h3>상위 위험 사용자</h3>
              <table>
                <thead>
                  <tr><th>Email</th><th>이벤트 건수</th></tr>
                </thead>
                <tbody>
                  {(summary?.top_risk_users || []).map((item) => (
                    <tr key={item.email}>
                      <td>{item.email}</td>
                      <td>{formatNumber(item.event_count)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          </div>

          <article className="card">
            <h3>위험 이벤트</h3>
            <table>
              <thead>
                <tr><th>ID</th><th>위험도</th><th>주문결정</th><th>종목</th><th>탐지 사유</th><th>상태</th><th>조치</th></tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id}>
                    <td>{event.id}</td>
                    <td><span className={`badge ${riskBadgeClass(event.risk_level)}`}>{event.risk_level}</span></td>
                    <td>{event.decision}</td>
                    <td>{event.stock_code} / {event.stock_name}</td>
                    <td>{event.reason_summary}</td>
                    <td>{event.status}</td>
                    <td>
                      <div className="action-stack">
                        <button className="text-button" type="button" onClick={() => takeAction(event.id, 'APPROVE')}>승인</button>
                        <button className="text-button" type="button" onClick={() => takeAction(event.id, 'REQUIRE_AUTH')}>추가인증</button>
                        <button className="text-button danger" type="button" onClick={() => takeAction(event.id, 'BLOCK')}>차단</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        </>
      )}

      {message && <div className="toast success">{message}</div>}
      {error && <div className="toast error">{error}</div>}
      {loading && <div className="loading-state">처리 중...</div>}
    </section>
  );
}
