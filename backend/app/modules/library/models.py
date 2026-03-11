# =============================================================================
# VELO Backend -- Library Models (Phase 9.2 -- stub/розетка)
# =============================================================================
#
# Future home of the practice recording library.
# Out of MVP scope (Section 1.3: "Library (записи практик)").
#
# TODO (Library v1 -- post-MVP):
#   Prerequisites before implementation:
#     1. S3-compatible storage (AWS S3 / Hetzner Object Storage).
#        Config keys: storage_bucket, storage_endpoint, storage_access_key,
#        storage_secret_key.
#     2. Upload endpoint: POST /api/v1/practices/{id}/recording
#        - Accepts multipart/form-data (video file).
#        - Uploads to S3, stores Recording row.
#        - Access control: master-only upload.
#     3. Stream/download endpoint: GET /api/v1/library/{id}/stream
#        - Returns pre-signed S3 URL (expires in 1h).
#        - Access control: user must have a completed booking for the practice.
#     4. Alembic migration: create_recordings_table.
#     5. Thumbnail generation (optional): background task via ffmpeg.
#
# DESIGN NOTES:
#   - Each Practice can have 0 or 1 Recording (OneToOne via practice_id UNIQUE).
#   - Recording is linked to the practice, not the master, to survive
#     master account changes.
#   - file_url stores the S3 key (not the full URL); pre-signed URLs are
#     generated at request time.
#   - duration_seconds is extracted from the video file at upload time.
#   - is_published controls visibility in the library catalog.
#     Default False -- master reviews before publishing.
#
# =============================================================================

# from datetime import datetime
# from uuid import UUID
#
# from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
# from sqlalchemy.orm import Mapped, mapped_column
#
# from app.core.database import Base
# from app.core.mixins import TimestampMixin, UUIDMixin
#
#
# class Recording(UUIDMixin, TimestampMixin, Base):
#     """A video recording of a completed practice.
#
#     Stored in S3. Linked 1:1 to Practice.
#     Access controlled: upload by master, view by past participants.
#     """
#
#     __tablename__ = "recordings"
#
#     __table_args__ = (
#         UniqueConstraint("practice_id", name="uq_recordings_practice_id"),
#     )
#
#     # -- Parent practice --
#     practice_id: Mapped[UUID] = mapped_column(
#         ForeignKey("practices.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )
#
#     # -- Storage --
#     # S3 object key (e.g. "recordings/uuid/master.mp4"), not a full URL.
#     # Pre-signed download URLs are generated per-request with TTL.
#     file_url: Mapped[str] = mapped_column(String(512), nullable=False)
#
#     # Optional thumbnail S3 key for library catalog display.
#     thumbnail_url: Mapped[str | None] = mapped_column(
#         String(512), default=None, nullable=True,
#     )
#
#     # -- Metadata --
#     duration_seconds: Mapped[int | None] = mapped_column(
#         Integer, default=None, nullable=True,
#     )
#     title: Mapped[str | None] = mapped_column(
#         String(200), default=None, nullable=True,
#     )
#     description: Mapped[str | None] = mapped_column(
#         Text, default=None, nullable=True,
#     )
#
#     # -- Visibility --
#     # False until master explicitly publishes.
#     is_published: Mapped[bool] = mapped_column(
#         Boolean, default=False, server_default="false",
#     )
#     published_at: Mapped[datetime | None] = mapped_column(
#         default=None, nullable=True,
#     )
