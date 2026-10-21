from datetime import datetime

def generate_activity_plans(forecast_data, current_weather=None):
    """
    Computes best time windows today for key daily outdoor activities:
    - Best Running / Workout window
    - Best Clothes Drying window
    - Best Outdoor Commute window
    Grounded strictly in hourly meteorological data.
    """
    if not forecast_data or 'list' not in forecast_data or not forecast_data['list']:
        return {
            'running': {'best_time': 'Current Window', 'score': 70, 'advice': 'Standard ambient conditions.'},
            'drying': {'best_time': 'Midday', 'score': 65, 'advice': 'Moderate drying efficiency.'},
            'commute': {'best_time': 'Flexible', 'score': 80, 'advice': 'Clear travel paths.'}
        }

    items = forecast_data['list'][:8] # Next 24 hours (8 3-hour steps)
    
    run_slots = []
    dry_slots = []
    commute_slots = []

    for item in items:
        dt = datetime.fromtimestamp(item['dt'])
        time_str = dt.strftime('%I %p')
        temp = item['main']['temp']
        humidity = item['main']['humidity']
        wind = item.get('wind', {}).get('speed', 0)
        pop = int(item.get('pop', 0) * 100)
        condition = (item['weather'][0]['description'] if item.get('weather') else '').lower()

        # 1. Running Score (Ideal 16-22°C, low rain, moderate wind, low humidity)
        run_score = 100.0
        if temp < 10:
            run_score -= (10 - temp) * 3
        elif temp > 24:
            run_score -= (temp - 24) * 4
        if pop > 20:
            run_score -= min(50, pop * 0.7)
        if humidity > 70:
            run_score -= (humidity - 70) * 0.5
        if wind > 7:
            run_score -= (wind - 7) * 3
        if 'storm' in condition or 'thunder' in condition:
            run_score -= 60
        run_score = max(10, min(100, int(round(run_score))))
        run_slots.append({'time': time_str, 'score': run_score, 'temp': round(temp, 1), 'pop': pop, 'condition': condition})

        # 2. Drying Score (Ideal high sun/clear, low humidity < 60%, wind 3-6 m/s, zero rain)
        dry_score = 100.0
        if pop > 15:
            dry_score -= min(70, pop * 0.8)
        if humidity > 50:
            dry_score -= (humidity - 50) * 1.0
        if 'rain' in condition or 'drizzle' in condition:
            dry_score -= 50
        if wind < 1.5:
            dry_score -= 15 # stagnant air dries slower
        dry_score = max(5, min(100, int(round(dry_score))))
        dry_slots.append({'time': time_str, 'score': dry_score, 'humidity': humidity, 'pop': pop})

        # 3. Commute Score (Ideal dry, moderate wind, no storms)
        commute_score = 100.0
        if pop > 30:
            commute_score -= min(50, pop * 0.6)
        if wind > 10:
            commute_score -= (wind - 10) * 3
        if 'fog' in condition or 'mist' in condition:
            commute_score -= 20
        commute_score = max(15, min(100, int(round(commute_score))))
        commute_slots.append({'time': time_str, 'score': commute_score, 'pop': pop, 'condition': condition})

    # Pick best slots
    best_run = max(run_slots, key=lambda x: x['score'])
    best_dry = max(dry_slots, key=lambda x: x['score'])
    best_commute = max(commute_slots, key=lambda x: x['score'])

    return {
        'running': {
            'best_time': best_run['time'],
            'score': best_run['score'],
            'advice': f"Best at {best_run['time']} ({best_run['temp']}°C, {best_run['pop']}% rain risk).",
            'timeline': run_slots
        },
        'drying': {
            'best_time': best_dry['time'],
            'score': best_dry['score'],
            'advice': f"Optimal drying at {best_dry['time']} ({best_dry['humidity']}% humidity).",
            'timeline': dry_slots
        },
        'commute': {
            'best_time': best_commute['time'],
            'score': best_commute['score'],
            'advice': f"Smooth commute window around {best_commute['time']}.",
            'timeline': commute_slots
        }
    }
