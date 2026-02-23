from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import json
import asyncio
import base64
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from models import ConfigModel, ComputeRequest, ComputeResponse, ComputeResult, ExportRequest
from solver import compute_all

file_cache: Dict[str, bytes] = {}

app = FastAPI(
    title="NDDF对偶模型计算工具",
    description="基于非径向方向距离函数(NDDF)对偶模型的影子价格和边际减排成本计算",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

progress_state = {"current": 0, "total": 0}


def run_compute(data: List[Dict[str, Any]], config: ConfigModel):
    def progress_callback(current, total):
        progress_state["current"] = current
        progress_state["total"] = total
    
    return compute_all(data, config, progress_callback)


@app.get("/")
async def root():
    return {"message": "NDDF对偶模型计算工具API", "version": "1.0.0"}


@app.get("/progress")
async def get_progress():
    return progress_state


@app.post("/api/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传Excel文件(.xlsx或.xls)")
    
    try:
        contents = await file.read()
        file_id = base64.b64encode(file.filename.encode()).decode()[:32]
        file_cache[file_id] = contents
        
        xl = pd.ExcelFile(io.BytesIO(contents))
        sheet_names = xl.sheet_names
        
        df = pd.read_excel(io.BytesIO(contents), sheet_name=sheet_names[0])
        columns = df.columns.tolist()
        preview = df.head(10).to_dict('records')
        total_rows = len(df)
        
        return {
            "success": True,
            "filename": file.filename,
            "fileId": file_id,
            "sheets": sheet_names,
            "currentSheet": sheet_names[0],
            "columns": columns,
            "preview": preview,
            "totalRows": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@app.post("/api/sheet-data", response_model=Dict[str, Any])
async def get_sheet_data(file_id: str = Form(...), sheet_name: str = Form(...)):
    if file_id not in file_cache:
        raise HTTPException(status_code=400, detail="文件已过期，请重新上传")
    
    try:
        contents = file_cache[file_id]
        df = pd.read_excel(io.BytesIO(contents), sheet_name=sheet_name)
        
        columns = df.columns.tolist()
        preview = df.head(10).to_dict('records')
        total_rows = len(df)
        
        all_data = df.to_dict('records')
        
        return {
            "success": True,
            "sheetName": sheet_name,
            "columns": columns,
            "preview": preview,
            "totalRows": total_rows,
            "data": all_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作簿解析失败: {str(e)}")


@app.post("/api/compute", response_model=ComputeResponse)
async def compute(request: ComputeRequest):
    try:
        progress_state["current"] = 0
        progress_state["total"] = len(request.data)
        
        results = compute_all(request.data, request.config)
        
        return ComputeResponse(
            success=True,
            message=f"计算完成，共处理{len(request.data)}条数据，成功{len(results)}条",
            results=results,
            total_count=len(request.data),
            computed_count=len(results)
        )
    except Exception as e:
        return ComputeResponse(
            success=False,
            message=f"计算失败: {str(e)}",
            results=None,
            total_count=len(request.data),
            computed_count=0
        )


@app.post("/api/export")
async def export_results(request: ExportRequest):
    try:
        results = request.results
        
        output_data = []
        for r in results:
            row = {
                request.config.idCol: r.id,
                request.config.yearCol: r.year,
                "Efficiency_NDDF": r.Efficiency_NDDF,
                "Zeta": r.Zeta
            }
            for col, val in r.prices.items():
                row[f"Price_{col}"] = val
            for col, val in r.mac.items():
                row[f"MAC_{col}"] = val
            output_data.append(row)
        
        df = pd.DataFrame(output_data)
        
        mode = "VRS" if request.config.isVRS else "CRS"
        filename = f"NDDF_ShadowPrices_{mode}.xlsx"
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.get("/api/columns-info")
async def get_columns_info():
    return {
        "inputTypes": ["投入要素"],
        "outputTypes": ["期望产出"],
        "undesiredTypes": ["非期望产出"],
        "defaultConfig": {
            "inputCols": [
                {"name": "L", "direction": 1, "weight": 0.167},
                {"name": "K", "direction": 1, "weight": 0.167},
                {"name": "E", "direction": 1, "weight": 0.167}
            ],
            "outputCols": [
                {"name": "Y", "direction": 1, "weight": 0.25}
            ],
            "undesiredCols": [
                {"name": "C", "direction": 1, "weight": 0.25},
                {"name": "P", "direction": 0, "weight": 0}
            ],
            "idCol": "id",
            "yearCol": "year",
            "isVRS": False
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
