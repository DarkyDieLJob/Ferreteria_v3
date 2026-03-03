def _to_float(value):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def _nearest(x: float, base: int) -> int:
    try:
        return int(round(x / base) * base)
    except Exception:
        return 0


def round_price(value, is_cartel: bool) -> int:
    """
    Regla unificada de redondeo de precios.

    - Precio <= 0 -> 0
    - 0 < precio < 50 -> 50
    - 50 <= precio < 75 -> 50
    - 75 <= precio < 100 -> 100
    - Sin cartel: >=100 -> múltiplo de 100 más cercano
    - Con cartel:
      * Si precio > 1000 -> múltiplo de 500 más cercano; si <=1000 usa regla sin cartel
      * Luego, si resultado >= 10000 y es múltiplo de 1000 -> restar 100
    """
    v = _to_float(value)

    if v <= 0:
        return 0

    # Tramo sub-100
    if v < 50:
        return 50
    if v < 75:
        return 50
    if v < 100:
        return 100

    # Redondeo principal
    if is_cartel and v > 1000:
        r = _nearest(v, 500)
    else:
        r = _nearest(v, 100)

    # Ajuste especial sólo para cartel y montos grandes
    if is_cartel and r >= 10000 and r % 1000 == 0:
        r -= 100

    return max(r, 50)
