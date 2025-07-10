def get_quality_text(tds: float) -> str:
    """
        Classifies monitoring quality based on TDS (Total Dissolved Solids).
        :param tds: TDS value in ppm
        :return: Text describing the quality
    """
    if tds <= 300:
        return "Excellent"
    elif tds <= 600:
        return "Good"
    elif tds <= 900:
        return "Acceptable"
    elif tds <= 1200:
        return "Bad"
    elif tds <= 2000:
        return "Non-potable"
    else:
        return "Contaminated"