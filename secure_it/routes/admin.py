from secure_it import admin_required, make_layout


@admin_required
def admin_page():
    return make_layout(
        "admin",
        "Security Analyst Dashboard",
        "SOC Operator: Admin User",
        "admin_dashboard.html",
        alerts=[
            {"label": "Notifications", "value": 3},
            {"label": "Critical", "value": 1},
        ],
        summary={
            "attack": "Web Discovery Attack",
            "source_ip": "32.122.195.63",
            "first_detected": "2 minutes ago",
            "event_id": "SEC-000001",
            "duration": "16 minutes 32 seconds",
            "urls_attempted": 31,
            "blocked_requests": 10,
        },
    )
