from sqlalchemy.orm import Session

from .. import models, schemas
from ..errors import DuplicateAssumptionError
from ..logger import logger
from ._common import common_update, rollback_on_exception


@rollback_on_exception
def create(
    name: str,
    kind: str,
    detail: str,
    db: Session,
) -> schemas.Assumption:
    logger.info(f"adding assumption, {name=}, {kind=}")
    # check if it exists already
    dup_name = (
        db.query(models.Assumption).filter_by(name=name, kind=kind).first() is not None
    )
    dup_detail = (
        db.query(models.Assumption).filter_by(detail=detail, kind=kind).first()
        is not None
    )
    if dup_name or dup_detail:
        if dup_name:
            dup_name = name
        if dup_detail:
            dup_detail = detail
        logger.error(f"error adding assumption, {dup_name=}, {dup_detail=}")
        raise DuplicateAssumptionError(dup_name, dup_detail)
    model = models.Assumption(name=name, kind=kind, detail=detail)
    db.add(model)
    db.commit()
    db.refresh(model)
    return schemas.Assumption.model_validate(model, from_attributes=True)


@rollback_on_exception
def read(
    db: Session,
    kind: str = None,
    name: str = None,
    id: int = None,
) -> list[schemas.Assumption]:
    logger.info(f"reading assumptions where {kind=}, {name=}, {id=}")
    filters = list()
    if name:
        filters.append(models.Assumption.name == name)
    if id:
        filters.append(models.Assumption.id == id)
    if kind:
        filters.append(models.Assumption.kind == kind)
    results = db.query(models.Assumption).filter(*filters).all()
    return [schemas.Assumption.model_validate(m, from_attributes=True) for m in results]


@rollback_on_exception
def read_kinds(db: Session) -> tuple[str, ...]:
    logger.info("reading assumption kinds present in the database")
    return tuple(
        str(r._asdict()["kind"]) for r in db.query(models.Assumption.kind).distinct()
    )


def update(
    db: Session,
    id: int,
    **kwargs,
) -> schemas.Assumption:
    obj = db.query(models.Assumption).filter(models.Assumption.id == id).first()
    if not obj:
        raise ValueError(f"Cannot find Assumption with {id=}")
    updated = common_update(db, obj, **kwargs)
    return updated


def delete(
    db: Session,
    id: int,
) -> None:
    obj = db.query(models.Assumption).filter(models.Assumption.id == id).first()
    if not obj:
        raise ValueError(f"Cannot find Assumption with {id=}")
    db.query(models.Assumption).filter(models.Assumption.id == id).delete()
    db.commit()
