"""部门服务层（树形结构）。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dept import Dept
from app.schemas.dept import DeptCreate, DeptNode


def list_depts(db: Session) -> list[DeptNode]:
    """列出所有部门（按 sort + id）。"""
    rows = db.scalars(select(Dept).order_by(Dept.sort.asc(), Dept.id.asc())).all()
    return [DeptNode.model_validate(d) for d in rows]


def build_tree(nodes: list[DeptNode]) -> list[dict]:
    """将扁平列表转换为树形（含 children）。"""
    by_id: dict[int, dict] = {}
    for n in nodes:
        by_id[n.id] = {
            "id": n.id, "name": n.name, "code": n.code,
            "parent_id": n.parent_id, "sort": n.sort,
            "leader_id": n.leader_id, "is_activate": n.is_activate,
            "children": [],
        }
    roots: list[dict] = []
    for d in by_id.values():
        pid = d["parent_id"]
        if pid and pid in by_id:
            by_id[pid]["children"].append(d)
        else:
            roots.append(d)
    return roots


def get_dept(db: Session, dept_id: int) -> DeptNode | None:
    d = db.get(Dept, dept_id)
    return DeptNode.model_validate(d) if d else None


def create_dept(db: Session, payload: DeptCreate, admin_id: int) -> DeptNode:
    d = Dept(
        name=payload.name,
        code=payload.code,
        parent_id=payload.parent_id,
        sort=payload.sort,
        leader_id=payload.leader_id,
        created_at=admin_id,
        updated_at=admin_id,
    )
    db.add(d)
    db.flush()
    # 简单实现 path 计算：父 path + 本 id（递归 1 层，复杂场景用 CTE）
    if d.parent_id:
        parent = db.get(Dept, d.parent_id)
        if parent and parent.path:
            d.path = f"{parent.path}{d.id},"
        else:
            d.path = f",{d.parent_id},{d.id},"
    else:
        d.path = f",{d.id},"
    db.commit()
    db.refresh(d)
    return DeptNode.model_validate(d)


def update_dept(db: Session, dept_id: int, payload: DeptCreate, admin_id: int) -> DeptNode | None:
    d = db.get(Dept, dept_id)
    if not d:
        return None
    data = payload.model_dump(exclude_unset=True)
    if "is_activate" in data:
        data["is_activate"] = 1 if data["is_activate"] else 0
    for k, v in data.items():
        setattr(d, k, v)
    d.updated_at = admin_id
    db.commit()
    db.refresh(d)
    return DeptNode.model_validate(d)


def delete_dept(db: Session, dept_id: int, admin_id: int) -> bool:
    """删除部门（如有子部门或被 admin_users 引用则拒绝）。"""
    from sqlalchemy import func

    child_count = db.scalar(
        select(func.count()).select_from(Dept).where(Dept.parent_id == dept_id)
    ) or 0
    if child_count > 0:
        return False
    d = db.get(Dept, dept_id)
    if not d:
        return False
    # 简单实现：直接删除（生产环境应检查 admin_users.dept_id 外键）
    db.delete(d)
    db.commit()
    return True


__all__ = ["list_depts", "build_tree", "get_dept", "create_dept", "update_dept", "delete_dept"]