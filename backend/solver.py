import numpy as np
from ortools.linear_solver import pywraplp
from typing import Dict, Any, List, Optional
from models import ConfigModel, ComputeResult
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


def solve_nddf_dual(
    current_dmu: Dict[str, Any],
    global_data: Dict[str, np.ndarray],
    config: ConfigModel
) -> Optional[ComputeResult]:
    is_vrs = config.isVRS
    
    input_names = [col.name for col in config.inputCols]
    output_names = [col.name for col in config.outputCols]
    undesired_names = [col.name for col in config.undesiredCols]
    
    x0 = np.array([current_dmu[col] for col in input_names])
    y0 = np.array([current_dmu[col] for col in output_names])
    b0 = np.array([current_dmu[col] for col in undesired_names])
    
    dx = np.array([col.direction for col in config.inputCols])
    dy = np.array([col.direction for col in config.outputCols])
    db = np.array([col.direction for col in config.undesiredCols])
    
    wx = np.array([col.weight for col in config.inputCols])
    wy = np.array([col.weight for col in config.outputCols])
    wb = np.array([col.weight for col in config.undesiredCols])
    
    gx, gy, gb = dx * x0, dy * y0, db * b0
    
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return None
    
    u = [
        solver.NumVar(
            wx[i] / gx[i] if gx[i] > 1e-6 else 0,
            solver.infinity(),
            f'u_{i}'
        )
        for i in range(len(gx))
    ]
    v = [
        solver.NumVar(
            wy[m] / gy[m] if gy[m] > 1e-6 else 0,
            solver.infinity(),
            f'v_{m}'
        )
        for m in range(len(gy))
    ]
    z = [
        solver.NumVar(
            wb[q] / gb[q] if gb[q] > 1e-6 else 0,
            solver.infinity(),
            f'z_{q}'
        )
        for q in range(len(gb))
    ]
    
    zeta = solver.NumVar(-solver.infinity(), solver.infinity(), 'zeta') if is_vrs else None
    
    xn_all, yn_all, bn_all = global_data['x'], global_data['y'], global_data['b']
    for n in range(len(xn_all)):
        ct = solver.Constraint(0, solver.infinity())
        if is_vrs and zeta is not None:
            ct.SetCoefficient(zeta, 1.0)
        for i in range(len(u)):
            ct.SetCoefficient(u[i], float(xn_all[n][i]))
        for m in range(len(v)):
            ct.SetCoefficient(v[m], float(-yn_all[n][m]))
        for q in range(len(z)):
            ct.SetCoefficient(z[q], float(bn_all[n][q]))
    
    obj = solver.Objective()
    if is_vrs and zeta is not None:
        obj.SetCoefficient(zeta, 1.0)
    for i in range(len(u)):
        obj.SetCoefficient(u[i], float(x0[i]))
    for m in range(len(v)):
        obj.SetCoefficient(v[m], float(-y0[m]))
    for q in range(len(z)):
        obj.SetCoefficient(z[q], float(b0[q]))
    obj.SetMinimization()
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        prices = {}
        for i, col in enumerate(input_names):
            prices[col] = u[i].solution_value()
        for m, col in enumerate(output_names):
            prices[col] = v[m].solution_value()
        for q, col in enumerate(undesired_names):
            prices[col] = z[q].solution_value()
        
        mac = {}
        main_y_price = v[0].solution_value() if v else 1.0
        for q, col in enumerate(undesired_names):
            mac[col] = z[q].solution_value() / (main_y_price + 1e-12)
        
        return ComputeResult(
            id=current_dmu.get(config.idCol),
            year=current_dmu.get(config.yearCol),
            Efficiency_NDDF=obj.Value(),
            Zeta=zeta.solution_value() if is_vrs and zeta else 0,
            prices=prices,
            mac=mac
        )
    return None


def _solve_single_task(args):
    row, global_data, config = args
    return solve_nddf_dual(row, global_data, config)


def compute_all(
    data: List[Dict[str, Any]],
    config: ConfigModel,
    progress_callback=None
) -> List[ComputeResult]:
    input_names = [col.name for col in config.inputCols]
    output_names = [col.name for col in config.outputCols]
    undesired_names = [col.name for col in config.undesiredCols]
    
    global_data = {
        'x': np.array([[row[col] for col in input_names] for row in data]),
        'y': np.array([[row[col] for col in output_names] for row in data]),
        'b': np.array([[row[col] for col in undesired_names] for row in data])
    }
    
    tasks = [(row, global_data, config) for row in data]
    total = len(tasks)
    num_workers = min(cpu_count(), 8)
    
    results = []
    
    with Pool(processes=num_workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(_solve_single_task, tasks)):
            if res:
                results.append(res)
            
            if progress_callback and (idx + 1) % max(1, total // 20) == 0:
                progress_callback(idx + 1, total)
    
    if progress_callback:
        progress_callback(total, total)
    
    return results
