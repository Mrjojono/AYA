"""Database models for AYA."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from aya_api.db import Base


class Drug(Base):
    """Canonical drug entity."""

    __tablename__: str = "drug"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Interaction(Base):
    """Drug-drug interaction record."""

    __tablename__: str = "interaction"
    __table_args__: tuple[object, ...] = (
        UniqueConstraint("drug_a_id", "drug_b_id", "source", name="uq_interaction"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_a_id: Mapped[int] = mapped_column(index=True)
    drug_b_id: Mapped[int] = mapped_column(index=True)
    severity: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    source_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RawDdinter(Base):
    """Raw DDInter import rows."""

    __tablename__: str = "raw_ddinter"

    id: Mapped[int] = mapped_column(primary_key=True)
    ddinter_id_a: Mapped[str] = mapped_column(String(64), index=True)
    drug_a: Mapped[str] = mapped_column(String(255))
    ddinter_id_b: Mapped[str] = mapped_column(String(64), index=True)
    drug_b: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(64))
    source_version: Mapped[str] = mapped_column(String(64))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Food(Base):
    """Food composition entry (WAFCT 2019)."""

    __tablename__: str = "food"

    id: Mapped[int] = mapped_column(primary_key=True)
    food_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    nutrients: Mapped[dict[str, object]] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(String(64), index=True)
    source_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OmsThreshold(Base):
    """Versioned WHO/FAO nutrient threshold."""

    __tablename__: str = "oms_threshold"

    id: Mapped[int] = mapped_column(primary_key=True)
    nutrient: Mapped[str] = mapped_column(String(64), index=True)
    unit: Mapped[str] = mapped_column(String(32))
    population_group: Mapped[str] = mapped_column(String(64), index=True)
    rni_low: Mapped[float | None] = mapped_column(nullable=True)
    rni_high: Mapped[float | None] = mapped_column(nullable=True)
    value_type: Mapped[str] = mapped_column(String(64))
    bioavailability: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_version: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Medication(Base):
    """Medication entry (Togo short list)."""

    __tablename__: str = "medication"

    id: Mapped[int] = mapped_column(primary_key=True)
    commercial_name: Mapped[str] = mapped_column(String(255), index=True)
    dci: Mapped[str] = mapped_column(String(255), index=True)
    active_substances: Mapped[str] = mapped_column(String(255))
    form: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    atc_code: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    therapeutic_class: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class MedicationSynonym(Base):
    """Synonym mapping to canonical DCI."""

    __tablename__: str = "medication_synonym"

    id: Mapped[int] = mapped_column(primary_key=True)
    input_form: Mapped[str] = mapped_column(String(255), index=True)
    canonical_dci: Mapped[str] = mapped_column(String(255), index=True)
    lang: Mapped[str | None] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
class Profile(Base):
    """User health profile (age required)."""

    __tablename__: str = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    age: Mapped[int] = mapped_column()
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    diet: Mapped[str | None] = mapped_column(String(128), nullable=True)
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Consent(Base):
    """Per-purpose consent record."""

    __tablename__: str = "consent"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    purpose: Mapped[str] = mapped_column(String(64), index=True)
    granted: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ImportReport(Base):
    """Quality report for an import run."""

    __tablename__: str = "import_report"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(64))
    source_version: Mapped[str] = mapped_column(String(64))
    row_count: Mapped[int] = mapped_column()
    distinct_drugs: Mapped[int] = mapped_column()
    severity_counts: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
