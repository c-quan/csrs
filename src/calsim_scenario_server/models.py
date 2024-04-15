import enum

from sqlalchemy import Boolean
from sqlalchemy import Enum as sqlalchemyEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint


# Create a base class for our ORM models
class Base(DeclarativeBase):
    pass


# Define the assumption types as a Python enumeration
class AssumptionEnumeration(enum.StrEnum):
    hydrology = "hydrology"
    sea_level_rise = "sea_level_rise"
    land_use = "land_use"
    tucp = "tucp"
    dcp = "dcp"
    va = "va"
    south_of_delta = "south_of_delta"


# Define ORM models for each table
class RunModel(Base):
    __tablename__ = "runs"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String, index=True)
    scenario_id = mapped_column(ForeignKey("scenarios.id"))
    version = mapped_column(String, nullable=False)

    scenario: Mapped["ScenarioModel"] = relationship(back_populates="runs")

    __table_args__ = (UniqueConstraint("name", "version", name="unique_purpose"),)


class RunMetadataModel(Base):
    __tablename__ = "run_metadata"

    run_id = mapped_column(
        ForeignKey("runs.id"),
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    predecessor_run_id = mapped_column(ForeignKey("runs.id"), nullable=True)
    contact = mapped_column(String, nullable=False)
    confidential = mapped_column(Boolean, nullable=False)
    published = mapped_column(Boolean, nullable=False)
    code_version = mapped_column(String, nullable=False)
    detail = mapped_column(String, nullable=False)


class ScenarioModel(Base):
    __tablename__ = "scenarios"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String, nullable=False, unique=True)

    runs: Mapped[list[RunModel]] = relationship(back_populates="scenario")
    assumptions: Mapped[list["ScenarioAssumptionsModel"]] = relationship(
        back_populates="scenario"
    )


class ScenarioAssumptionsModel(Base):
    __tablename__ = "scenario_assumptions"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    assumption_kind = mapped_column(
        sqlalchemyEnum(AssumptionEnumeration),
        nullable=False,
    )
    assumption_id = mapped_column(ForeignKey("assumptions.id"), nullable=False)

    scenario: Mapped[ScenarioModel] = relationship(back_populates="assumptions")
    assumption: Mapped["AssumptionModel"] = relationship(back_populates="scenarios")


class NamedPathModel(Base):
    __tablename__ = "paths"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String)
    path = mapped_column(String)
    category = mapped_column(String)
    units = mapped_column(ForeignKey("units.name"))
    detail = mapped_column(String, nullable=False)

    __table_args__ = (UniqueConstraint("path", "category", name="unique_purpose"),)


class UnitModel(Base):
    __tablename__ = "units"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String, unique=True)


class MetricModel(Base):
    __tablename__ = "metrics"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    index_detail = mapped_column(String, nullable=False)
    units = mapped_column(ForeignKey("units.name"))
    detail = mapped_column(String, nullable=False)


class TimeseriesValueModel(Base):
    __tablename__ = "time_series_values"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id = mapped_column(ForeignKey("runs.id"))
    path_id = mapped_column(ForeignKey("paths.id"))
    timestep_id = mapped_column(ForeignKey("timesteps.id"))
    value = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "path_id", "timestep_id", name="unique_in_run"),
    )


class MetricValueModel(Base):
    __tablename__ = "metric_values"
    path_id = mapped_column(ForeignKey("paths.id"), primary_key=True)
    run_id = mapped_column(ForeignKey("runs.id"), primary_key=True)
    metric_id = mapped_column(ForeignKey("metrics.id"), primary_key=True)
    index = mapped_column(Integer, nullable=False)
    value = mapped_column(Float, nullable=False)


class TimestepModel(Base):
    __tablename__ = "timesteps"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    datetime_str = mapped_column(String, nullable=False, unique=True)


class AssumptionModel(Base):
    __tablename__ = "assumptions"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    kind = mapped_column(
        sqlalchemyEnum(AssumptionEnumeration),
        nullable=False,
    )
    detail = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("name", "kind", name="unique_name"),
        UniqueConstraint("detail", "kind", name="unique_detail"),
    )
    scenarios: Mapped[list[ScenarioAssumptionsModel]] = relationship(
        back_populates="assumption"
    )
