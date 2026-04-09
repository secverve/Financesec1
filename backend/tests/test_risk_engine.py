from app.fds.engine import RiskEngine


def test_risk_engine_detects_critical_case():
    engine = RiskEngine()
    result = engine.evaluate(
        {
            'is_new_device': True,
            'order_amount': 10000000,
            'avg_order_amount': 1000000,
            'recent_login_region': 'OVERSEAS-US',
            'login_failures': 4,
            'preferred_stocks': ['000660'],
            'stock_code': '005930',
            'same_stock_order_count': 4,
            'same_ip_order_users': 3,
        }
    )
    assert result['risk_level'] == 'CRITICAL'
    assert result['decision'] == 'BLOCK'
    assert len(result['hits']) >= 4
