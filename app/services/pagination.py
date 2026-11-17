from math import ceil
from typing import Any, Mapping, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate_query(
    db: Session,
    model: Any,
    base_query: Optional[Select] = None,
    page: int = 1,
    per_page: int = 10,
    order_by: Optional[str] = None,
    direction: str = "asc",
    allowed_order: Optional[Mapping[str, Any]] = None,
) -> dict:
    """Pagina cualquier consulta de SQLAlchemy.

    - `base_query`: la consulta ya filtrada (si no viene, se usa `select(model)`).
    - `allowed_order`: diccionario {"nombre": columna} con los campos por los
      que se permite ordenar. Si `order_by` no está ahí, se ordena por id.

    Devuelve {"total", "items", "pages"}. El total se cuenta sobre la consulta
    filtrada (no sobre la tabla entera), así la paginación es coherente con
    la búsqueda.
    """
    query = base_query if base_query is not None else select(model)

    total = db.scalar(
        select(func.count()).select_from(query.order_by(None).subquery())
    ) or 0
    pages = ceil(total / per_page) if total > 0 else 0

    if total == 0:
        return {"total": 0, "items": [], "pages": 0}

    current_page = min(max(1, page), pages)

    allowed = allowed_order or {}
    column = allowed.get(order_by) if order_by else None
    if column is None:
        column = model.id

    query = query.order_by(column.desc() if direction == "desc" else column.asc())
    # Desempate estable para que dos registros con el mismo valor no salten
    # de página entre consultas.
    if column is not model.id:
        query = query.order_by(model.id.asc())

    items = db.execute(
        query.limit(per_page).offset((current_page - 1) * per_page)
    ).scalars().unique().all()

    return {"total": total, "items": list(items), "pages": pages}
