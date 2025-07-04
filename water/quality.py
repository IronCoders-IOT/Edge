def get_quality_text(tds: float) -> str:
    """
        Classifies water quality based on TDS (Total Dissolved Solids).
        :param tds: TDS value in ppm
        :return: Text describing the quality
    """
    if tds <= 100:
        return "Excellent"
    elif tds <= 300:
        return "Good"
    elif tds <= 600:
        return "Acceptable"
    elif tds <= 900:
        return "Bad"
    elif tds <= 1200:
        return "Non-potable"
    else:
        return "Contaminated water" 