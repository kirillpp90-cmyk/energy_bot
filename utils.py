def calculate_energy(power: float, hours: float, days: float, tariff: float):
    """Функция расчёта энергопотребления"""
    power_kw = power / 1000.0
    total_kwh = power_kw * hours * days
    cost = total_kwh * tariff
    return total_kwh, cost