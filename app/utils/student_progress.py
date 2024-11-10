from app.models.enum import LatestGrade
def calculate_grade(overall_percentage: float) -> LatestGrade:
    if overall_percentage >= 90:
        return LatestGrade.A_PLUS
    elif overall_percentage >= 85:
        return LatestGrade.A
    elif overall_percentage >= 80:
        return LatestGrade.A_MINUS
    elif overall_percentage >= 75:
        return LatestGrade.B_PLUS
    elif overall_percentage >= 70:
        return LatestGrade.B
    elif overall_percentage >= 65:
        return LatestGrade.B_MINUS
    elif overall_percentage >= 60:
        return LatestGrade.C_PLUS
    elif overall_percentage >= 55:
        return LatestGrade.C
    elif overall_percentage >= 50:
        return LatestGrade.C_MINUS
    elif overall_percentage >= 45:
        return LatestGrade.D_PLUS
    elif overall_percentage >= 40:
        return LatestGrade.D
    elif overall_percentage >= 35:
        return LatestGrade.D_MINUS
    else:
        return LatestGrade.F
