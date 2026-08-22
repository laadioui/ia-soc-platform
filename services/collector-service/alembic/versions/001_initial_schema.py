"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-08-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("resource", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("level", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), primary_key=True),
        sa.Column("permission_id", UUID(as_uuid=True), sa.ForeignKey("permissions.id"), primary_key=True),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("username", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("full_name", sa.String(200)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("mfa_enabled", sa.Boolean, default=False),
        sa.Column("mfa_secret", sa.String(255)),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column("login_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), primary_key=True),
    )

    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("user_name", sa.String(255)),
        sa.Column("source_ip", sa.String(45)),
        sa.Column("destination_ip", sa.String(45)),
        sa.Column("destination_port", sa.Integer),
        sa.Column("hostname", sa.String(255)),
        sa.Column("application", sa.String(255)),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("raw_event", JSON),
        sa.Column("normalized_event", JSON),
        sa.Column("tags", JSON),
        sa.Column("risk_score", sa.Float),
        sa.Column("is_alert", sa.Boolean, default=False),
        sa.Column("processed", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_events_timestamp", "events", ["timestamp"])
    op.create_index("idx_events_source", "events", ["source"])
    op.create_index("idx_events_category", "events", ["category"])
    op.create_index("idx_events_severity", "events", ["severity"])

    op.create_table(
        "alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("alert_id", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="new"),
        sa.Column("risk_score", sa.Float),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("rule_id", sa.String(100)),
        sa.Column("rule_name", sa.String(255)),
        sa.Column("event_count", sa.Integer, default=1),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("metadata_json", JSON),
        sa.Column("related_events", JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "incidents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("risk_score", sa.Float, default=0.0),
        sa.Column("status", sa.String(30), default="new"),
        sa.Column("source", sa.String(255)),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("contained_at", sa.DateTime(timezone=True)),
        sa.Column("ai_summary", sa.Text),
        sa.Column("ai_confidence", sa.Float),
        sa.Column("tags", JSON),
        sa.Column("metadata_json", JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "incident_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("event_id", UUID(as_uuid=True), nullable=False),
        sa.Column("event_id_str", sa.String(255), nullable=False),
        sa.Column("added_by", sa.String(100), default="system"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "incident_iocs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("ioc_type", sa.String(50), nullable=False),
        sa.Column("ioc_value", sa.String(500), nullable=False),
        sa.Column("confidence", sa.Float),
        sa.Column("source", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "iocs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ioc_type", sa.String(50), nullable=False),
        sa.Column("ioc_value", sa.String(500), nullable=False),
        sa.Column("severity", sa.String(20), default="medium"),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("description", sa.Text),
        sa.Column("source", sa.String(255)),
        sa.Column("tags", JSON),
        sa.Column("first_seen", sa.String(50)),
        sa.Column("last_seen", sa.String(50)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("threat_type", sa.String(100)),
        sa.Column("related_campaign", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("hostname", sa.String(255)),
        sa.Column("operating_system", sa.String(100)),
        sa.Column("owner", sa.String(255)),
        sa.Column("environment", sa.String(50)),
        sa.Column("criticality", sa.String(20), default="medium"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("metadata_json", JSON),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "mitre_techniques",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("technique_id", sa.String(20), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tactic", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("detection", sa.Text),
        sa.Column("platforms", JSON),
        sa.Column("data_sources", JSON),
        sa.Column("sub_techniques", JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "incident_mitre_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("technique_id", sa.String(20), sa.ForeignKey("mitre_techniques.technique_id"), nullable=False),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("context", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "threat_intelligence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("indicator_type", sa.String(50), nullable=False),
        sa.Column("indicator_value", sa.String(500), nullable=False),
        sa.Column("threat_type", sa.String(100)),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("severity", sa.String(20), default="medium"),
        sa.Column("description", sa.Text),
        sa.Column("source", sa.String(255)),
        sa.Column("source_url", sa.String(1000)),
        sa.Column("tags", JSON),
        sa.Column("related_campaign", sa.String(255)),
        sa.Column("related_mitre", JSON),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("tlp", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "detection_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("rule_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("condition", JSON, nullable=False),
        sa.Column("mitre_technique", sa.String(20)),
        sa.Column("mitre_tactic", sa.String(100)),
        sa.Column("false_positive_check", sa.Text),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("author", sa.String(255)),
        sa.Column("tags", JSON),
        sa.Column("time_window_seconds", sa.Integer),
        sa.Column("threshold", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("username", sa.String(255)),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255)),
        sa.Column("details", JSON),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "ai_analyses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id")),
        sa.Column("event_id", UUID(as_uuid=True)),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("response", sa.Text, nullable=False),
        sa.Column("model_used", sa.String(100)),
        sa.Column("confidence", sa.Float),
        sa.Column("context_used", JSON),
        sa.Column("tokens_used", sa.Integer),
        sa.Column("processing_time_ms", sa.Float),
        sa.Column("feedback", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "response_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("target", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("executed_by", sa.String(255)),
        sa.Column("executed_at", sa.DateTime(timezone=True)),
        sa.Column("result", sa.Text),
        sa.Column("is_simulated", sa.Boolean, default=True),
        sa.Column("parameters", JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("response_actions")
    op.drop_table("ai_analyses")
    op.drop_table("audit_logs")
    op.drop_table("detection_rules")
    op.drop_table("threat_intelligence")
    op.drop_table("incident_mitre_mappings")
    op.drop_table("mitre_techniques")
    op.drop_table("assets")
    op.drop_table("iocs")
    op.drop_table("incident_iocs")
    op.drop_table("incident_events")
    op.drop_table("incidents")
    op.drop_table("alerts")
    op.drop_index("idx_events_severity", "events")
    op.drop_index("idx_events_category", "events")
    op.drop_index("idx_events_source", "events")
    op.drop_index("idx_events_timestamp", "events")
    op.drop_table("events")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")
