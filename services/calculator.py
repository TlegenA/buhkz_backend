from dataclasses import dataclass


# Актуальные показатели 2025
MZP = 85000   # Минимальная зарплата
MRP = 3932    # Месячный расчётный показатель

OPV_RATE = 0.10          # ОПВ 10%, потолок 50 МЗП
OSMS_EMPLOYEE_RATE = 0.02  # ОСМС работник 2%
IPN_RATE = 0.10          # ИПН 10%
SO_RATE = 0.035          # СО 3.5%, потолок 7 МЗП
OSMS_EMPLOYER_RATE = 0.03  # ОСМС работодатель 3%
SN_RATE = 0.095          # СН 9.5% (до вычета ОПВ и СО)

# Ставки алиментов от чистой зарплаты (ст.139 Кодекса РК о браке и семье)
ALIMONY_RATES = {1: 0.25, 2: 0.33}
ALIMONY_RATE_3_PLUS = 0.50


@dataclass
class EmployerCosts:
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
    salary_after_alimony: int = 0


def calculate_salary(
    gross: float,
    has_child_deduction: bool = False,
    children_count: int = 0,
    entity_type: str = "ТОО",
    alimony_children: int = 0,
) -> SalaryResult:
    gross = int(gross)

    # 1. ОПВ — 10% от дохода, потолок 50 МЗП
    opv_base = min(gross, MZP * 50)
    opv = round(opv_base * OPV_RATE)

    # 2. ОСМС работника — 2% от дохода
    osms_employee = round(gross * OSMS_EMPLOYEE_RATE)

    # 3. База ИПН с вычетами
    ipn_deduction = MZP  # стандартный вычет 1 МЗП
    if has_child_deduction and children_count > 0:
        # вычет на детей: 882 МРП на каждого ребёнка в год = 73.5 МРП в месяц
        ipn_deduction += round(MRP * 882 / 12 * children_count)

    ipn_base = gross - opv - osms_employee - ipn_deduction
    ipn = max(0, round(ipn_base * IPN_RATE))

    # 4. Чистая зарплата
    net_salary = gross - opv - osms_employee - ipn

    # 5. Расходы работодателя
    # СО: 3.5% от (доход − МЗП), потолок база 7 МЗП
    so_base = min(gross, MZP * 7)
    so = max(0, round((so_base - MZP) * SO_RATE))

    # ОСМС работодателя: 3%
    osms_employer = round(gross * OSMS_EMPLOYER_RATE)

    # СН: 9.5% от дохода − ОПВ − СО (не менее 0)
    sn = max(0, round(gross * SN_RATE - opv - so))

    total_cost = gross + so + osms_employer + sn

    # 6. Алименты — удерживаются с чистой зарплаты
    alimony = 0
    alimony_rate = 0.0
    if alimony_children > 0:
        alimony_rate = ALIMONY_RATES.get(alimony_children, ALIMONY_RATE_3_PLUS)
        alimony = round(net_salary * alimony_rate)
    salary_after_alimony = net_salary - alimony

    return SalaryResult(
        gross=gross,
        opv=opv,
        osms_employee=osms_employee,
        ipn_base=max(0, ipn_base),
        ipn=ipn,
        net_salary=net_salary,
        employer=EmployerCosts(
            so=so,
            osms_employer=osms_employer,
            sn=sn,
            total_cost=total_cost,
        ),
        alimony=alimony,
        alimony_rate=alimony_rate,
        salary_after_alimony=salary_after_alimony,
    )
