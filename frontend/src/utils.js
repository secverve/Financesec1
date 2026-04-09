export function formatCurrency(value) {
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW', maximumFractionDigits: 0 }).format(value || 0);
}

export function formatNumber(value) {
  return new Intl.NumberFormat('ko-KR').format(value || 0);
}

export function riskBadgeClass(riskLevel) {
  if (!riskLevel) return 'normal';
  return riskLevel.toLowerCase();
}
