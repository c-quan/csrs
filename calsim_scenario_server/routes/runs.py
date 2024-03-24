from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..logger import logger
from ..models.backend import Run, RunMetadata, Scenario
from ..models.frontend import RunModel

router = APIRouter(prefix="/runs")


def assert_scenario_exists(s_id: int | None, db: Session):
    if s_id is not None:
        s_count = db.query(Scenario).filter(Scenario.id == s_id).count()
        if s_count != 1:
            logger.error(f"scenario_id was not found, {s_id=}")
            raise HTTPException(
                status_code=400,
                detail=f"scenario_id={s_id} not found, you need to add it first",
            )


@router.get("/", response_model=list[RunModel])
async def get_all_runs(metadata: bool = False, db: Session = Depends(get_db)):
    logger.info(f"{metadata=}")
    if metadata is True:
        runs = db.query(Run).join(RunMetadata, Run.id == RunMetadata.run_id).all()
    else:
        runs = db.query(Run).all()

    if runs is None:
        raise HTTPException(status_code=404, detail="Runs not found")
    logger.info(f"{runs=}")
    return runs


@router.post("/", response_model=RunModel)
async def post_run(run_data: RunModel, db: Session = Depends(get_db)):
    logger.info(run_data)
    try:
        assert_scenario_exists(run_data.scenario_id, db)
        assert_scenario_exists(run_data.predecessor_run_id, db)
        metadata = {
            "contact",
            "confidential",
            "published",
            "code_version",
            "detail",
            "predecessor_run_id",
        }
        # Create a new Path object
        new_run = Run(**run_data.model_dump(exclude=metadata))
        new_run_metadata = RunMetadata(**run_data.model_dump(include=metadata))

        # Add the new path to the database session
        db.add(new_run)
        db.add(new_run_metadata)
        db.commit()
        db.refresh(new_run)
        db.refresh(new_run_metadata)

        return run_data
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        logger.error(f"{type(e)} encountered: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
