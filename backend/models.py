from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum


class ReturnScale(str, Enum):
    CRS = "CRS"
    VRS = "VRS"


class ColumnConfig(BaseModel):
    name: str
    direction: float
    weight: float


class ConfigModel(BaseModel):
    inputCols: List[ColumnConfig]
    outputCols: List[ColumnConfig]
    undesiredCols: List[ColumnConfig]
    idCol: str = "id"
    yearCol: str = "year"
    isVRS: bool = False


class ComputeRequest(BaseModel):
    config: ConfigModel
    data: List[Dict[str, Any]]


class ComputeResult(BaseModel):
    id: Any
    year: Any
    Efficiency_NDDF: float
    Zeta: float
    prices: Dict[str, float]
    mac: Dict[str, float]


class ComputeResponse(BaseModel):
    success: bool
    message: str
    results: Optional[List[ComputeResult]] = None
    total_count: int = 0
    computed_count: int = 0


class ExportRequest(BaseModel):
    config: ConfigModel
    results: List[ComputeResult]
