from dataclasses import dataclass

# Базовые показатели 2026
MZP = 85_000    # МЗП
MRP = 4_325     # МРП

# ОПВ (работник) — 10%, потолок 50 МЗП
OPV_RATE = 0.10
OPV_CAP = MZP * 50              # 4 250 000

# ВОСМС (работник) — 2%, потолок 20 МЗП
OSMS_EMPLOYEE_RATE = 0.02
OSMS_EMPLOYEE_CAP = MZP * 20    # 1 700 000

# ИПН — базовый вычет 30 МРП; прогрессивная шкала
# Порог 15% = 8 500 МРП в год (ст.363 НК РК 2026), месячный эквивалент:
BASE_DEDUCTION = MRP * 30                       # 129 750
IPN_THRESHOLD = MRP * 8_500 // 12              # ~3 063 541 тг/мес
IPN_RATE_LOW = 0.10
IPN_RATE_HIGH = 0.15

# ОПВР (работодатель) — 3.5%, потолок 50 МЗП  (НОВЫЙ с 2026)
OPVR_RATE = 0.035
OPVR_CAP = MZP * 50

# СО (работодатель) — 5% от (gross − ОПВ), база min 1МЗП max 7МЗП
SO_RATE = 0.05
SO_BASE_MIN = MZP
SO_BASE_MAX = MZP * 7           # 595 000

# ООСМС (работодатель) — 3%, потолок 40 МЗП
OSMS_EMPLOYER_RATE = 0.03
OSMS_EMPLOYER_CAP = MZP * 40    # 3 400 000

# СН (работодатель) — 6% от (gross − ОПВ − ВОСМС), мин. база 14 МРП
SN_RATE = 0.06
SN_BASE_MIN = MRP * 14          # 60 550

# Ставки алиментов от чистой зарплаты (ст.139 Кодекса РК о браке и семье)
ALIMONY_RATES = {1: 0.25, 2: 0.33}
ALIMONY_RATE_3_PLUS = 0.50


@dataclass
class EmployerCosts:
    opvr: int
    so: int
    osms_employer: int
    sn: int
    total_cost: int


@dataclass
class SalaryResult:
    gross: int
    opv: int
    osms_employee: int
    ipn_base: int
    ipn: int
    net_salary: int
    employer: EmployerCosts
    alimony: int = 0
    alimony_rate: float = 0.0
    executor_fee: int = 0
    salary_after_alimony: int = 0


def _calc_ipn(ipn_base: int) -> int:
    if ipn_base <= 0:
        return 0
    if ipn_base <= IPN_THRESHOLD:
        return round(ipn_base * IPN_RATE_LOW)
    return round(IPN_THRESHOLD * IPN_RATE_LOW + (ipn_base - IPN_THRESHOLD) * IPN_RATE_HIGH)


def calculate_salary(
    gross: float,
    has_child_deduction: bool = False,
    children_count: int = 0,
    entity_type: str = "ТОО",
    alimony_children: int = 0,
) -> SalaryResult:
    gross = int(gross)

    # 1. ОПВ — 10%, потолок 50 МЗП
    opv = round(min(gross, OPV_CAP) * OPV_RATE)

    # 2. ВОСМС работника — 2%, потолок 20 МЗП
    osms_employee = round(min(gross, OSMS_EMPLOYEE_CAP) * OSMS_EMPLOYEE_RATE)

    # 3. База ИПН = gross − ОПВ − ВОСМС − базовый вычет (30 МРП)
    extra_deduction = 0
    if has_child_deduction and children_count > 0:
        # Социальный вычет на детей-инвалидов: 882 МРП в год на ребёнка
        extra_deduction = round(MRP * 882 / 12 * children_count)

    ipn_base = gross - opv - osms_employee - BASE_DEDUCTION - extra_deduction
    ipn = _calc_ipn(ipn_base)

    # 4. Чистая зарплата
    net_salary = gross - opv - osms_employee - ipn

    # 5. Расходы работодателя
    # ОПВР — 3.5%, потолок 50 МЗП (новый с 2026)
    opvr = round(min(gross, OPVR_CAP) * OPVR_RATE)

    # СО — 5% от (gross − ОПВ), база min 1МЗП, max 7МЗП
    so_base = min(max(gross - opv, SO_BASE_MIN), SO_BASE_MAX)
    so = round(so_base * SO_RATE)

    # ООСМС — 3%, потолок 40 МЗП
    osms_employer = round(min(gross, OSMS_EMPLOYER_CAP) * OSMS_EMPLOYER_RATE)

    # СН — 6% от (gross − ОПВ − ВОСМС), мин. база 14 МРП
    sn_base = max(gross - opv - osms_employee, SN_BASE_MIN)
    sn = round(sn_base * SN_RATE)

    total_cost = gross + opvr + so + osms_employer + sn

    # 6. Алименты + вознаграждение судебного исполнителя (1 МРП, ст. 117 Закона об исполнит. производстве)
    alimony = 0
    alimony_rate = 0.0
    executor_fee = 0
    if alimony_children > 0:
        alimony_rate = ALIMONY_RATES.get(alimony_children, ALIMONY_RATE_3_PLUS)
        alimony = round(net_salary * alimony_rate)
        executor_fee = MRP
    salary_after_alimony = net_salary - alimony - executor_fee

    return SalaryResult(
        gross=gross,
        opv=opv,
        osms_employee=osms_employee,
        ipn_base=max(0, ipn_base),
        ipn=ipn,
        net_salary=net_salary,
        employer=EmployerCosts(
            opvr=opvr,
            so=so,
            osms_employer=osms_employer,
            sn=sn,
            total_cost=total_cost,
        ),
        alimony=alimony,
        alimony_rate=alimony_rate,
        executor_fee=executor_fee,
        salary_after_alimony=salary_after_alimony,
    )
