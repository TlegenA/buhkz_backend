from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.calculator import (
    calculate_salary,
    calculate_gross_from_net,
    calculate_vacation,
    calculate_sick_leave,
    calculate_ip_tax,
)

router = APIRouter(prefix="/api/calculator", tags=["calculator"])


class SalaryRequest(BaseModel):
    gross_salary: float = Field(..., gt=0)
    has_child_deduction: bool = False
    children_count: int = Field(0, ge=0, le=10)
    entity_type: str = "ТОО"
    alimony_children: int = Field(0, ge=0, le=10)


class ReverseRequest(BaseModel):
    net_salary: float = Field(..., gt=0)
    has_child_deduction: bool = False
    children_count: int = Field(0, ge=0, le=10)
    entity_type: str = "ТОО"
    alimony_children: int = Field(0, ge=0, le=10)


class VacationRequest(BaseModel):
    gross_monthly: float = Field(..., gt=0)
    vacation_days: int = Field(..., gt=0, le=365)


class SickLeaveRequest(BaseModel):
    gross_monthly: float = Field(..., gt=0)
    sick_days: int = Field(..., gt=0, le=365)
    seniority_years: float = Field(..., ge=0)


class IpRequest(BaseModel):
    income: float = Field(..., gt=0)
    mode: str = Field("simplified", description="simplified — упрощёнка (3%), patent — патент (1%)")
    months: int = Field(6, ge=1, le=12)


class IpTaxOut(BaseModel):
    mode: str
    income: int
    period_months: int
    ip_tax: int
    opv: int
    opvr: int
    osms: int
    so: int
    total: int
    income_limit: int
    income_remaining: int


class EmployerOut(BaseModel):
    opvr: int
    so: int
    osms_employer: int
    sn: int
    total_cost: int


class SalaryOut(BaseModel):
    gross: int
    opv: int
    osms_employee: int
    ipn_base: int
    ipn: int
    net_salary: int
    employer: EmployerOut
    alimony: int = 0
    alimony_rate: float = 0.0
    executor_fee: int = 0
    salary_after_alimony: int = 0


class VacationOut(BaseModel):
    gross_monthly: int
    vacation_days: int
    avg_daily: int
    vacation_pay: int


class SickLeaveOut(BaseModel):
    gross_monthly: int
    sick_days: int
    avg_daily: int
    coefficient: float
    seniority_label: str
    sick_pay: int


def _salary_to_out(result) -> SalaryOut:
    return SalaryOut(
        gross=result.gross,
        opv=result.opv,
        osms_employee=result.osms_employee,
        ipn_base=result.ipn_base,
        ipn=result.ipn,
        net_salary=result.net_salary,
        employer=EmployerOut(
            opvr=result.employer.opvr,
            so=result.employer.so,
            osms_employer=result.employer.osms_employer,
            sn=result.employer.sn,
            total_cost=result.employer.total_cost,
        ),
        alimony=result.alimony,
        alimony_rate=result.alimony_rate,
        executor_fee=result.executor_fee,
        salary_after_alimony=result.salary_after_alimony,
    )


@router.post("/salary", response_model=SalaryOut)
async def salary_calculator(body: SalaryRequest):
    return _salary_to_out(calculate_salary(
        gross=body.gross_salary,
        has_child_deduction=body.has_child_deduction,
        children_count=body.children_count,
        entity_type=body.entity_type,
        alimony_children=body.alimony_children,
    ))


@router.post("/reverse", response_model=SalaryOut)
async def reverse_calculator(body: ReverseRequest):
    return _salary_to_out(calculate_gross_from_net(
        net=body.net_salary,
        has_child_deduction=body.has_child_deduction,
        children_count=body.children_count,
        entity_type=body.entity_type,
        alimony_children=body.alimony_children,
    ))


@router.post("/vacation", response_model=VacationOut)
async def vacation_calculator(body: VacationRequest):
    r = calculate_vacation(body.gross_monthly, body.vacation_days)
    return VacationOut(
        gross_monthly=r.gross_monthly,
        vacation_days=r.vacation_days,
        avg_daily=r.avg_daily,
        vacation_pay=r.vacation_pay,
    )


@router.post("/sick-leave", response_model=SickLeaveOut)
async def sick_leave_calculator(body: SickLeaveRequest):
    r = calculate_sick_leave(body.gross_monthly, body.sick_days, body.seniority_years)
    return SickLeaveOut(
        gross_monthly=r.gross_monthly,
        sick_days=r.sick_days,
        avg_daily=r.avg_daily,
        coefficient=r.coefficient,
        seniority_label=r.seniority_label,
        sick_pay=r.sick_pay,
    )


@router.post("/ip", response_model=IpTaxOut)
async def ip_calculator(body: IpRequest):
    r = calculate_ip_tax(body.income, body.mode, body.months)
    return IpTaxOut(
        mode=r.mode,
        income=r.income,
        period_months=r.period_months,
        ip_tax=r.ip_tax,
        opv=r.opv,
        opvr=r.opvr,
        osms=r.osms,
        so=r.so,
        total=r.total,
        income_limit=r.income_limit,
        income_remaining=r.income_remaining,
    )
