from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.calculator import calculate_salary

router = APIRouter(prefix="/api/calculator", tags=["calculator"])


class SalaryRequest(BaseModel):
    gross_salary: float = Field(..., gt=0, description="Оклад до вычетов (тенге)")
    has_child_deduction: bool = False
    children_count: int = Field(0, ge=0, le=10)
    entity_type: str = "ТОО"


class EmployerOut(BaseModel):
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


@router.post("/salary", response_model=SalaryOut)
async def salary_calculator(body: SalaryRequest):
    result = calculate_salary(
        gross=body.gross_salary,
        has_child_deduction=body.has_child_deduction,
        children_count=body.children_count,
        entity_type=body.entity_type,
    )
    return SalaryOut(
        gross=result.gross,
        opv=result.opv,
        osms_employee=result.osms_employee,
        ipn_base=result.ipn_base,
        ipn=result.ipn,
        net_salary=result.net_salary,
        employer=EmployerOut(
            so=result.employer.so,
            osms_employer=result.employer.osms_employer,
            sn=result.employer.sn,
            total_cost=result.employer.total_cost,
        ),
    )
