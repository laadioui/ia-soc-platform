{{/*
Expand the name of the chart.
*/}}
{{- define "ai-soc.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ai-soc.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ai-soc.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ai-soc.labels" -}}
helm.sh/chart: {{ include "ai-soc.chart" . }}
{{ include "ai-soc.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: ai-soc-platform
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ai-soc.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-soc.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Namespace
*/}}
{{- define "ai-soc.namespace" -}}
{{- default .Values.global.namespace .Release.Namespace }}
{{- end }}

{{/*
Postgres fullname
*/}}
{{- define "ai-soc.postgres.fullname" -}}
{{- printf "%s-postgres" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis fullname
*/}}
{{- define "ai-soc.redis.fullname" -}}
{{- printf "%s-redis" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
OpenSearch fullname
*/}}
{{- define "ai-soc.opensearch.fullname" -}}
{{- printf "%s-opensearch" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Kafka fullname
*/}}
{{- define "ai-soc.kafka.fullname" -}}
{{- printf "%s-kafka" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Zookeeper fullname
*/}}
{{- define "ai-soc.zookeeper.fullname" -}}
{{- printf "%s-zookeeper" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Keycloak fullname
*/}}
{{- define "ai-soc.keycloak.fullname" -}}
{{- printf "%s-keycloak" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Backend fullname
*/}}
{{- define "ai-soc.backend.fullname" -}}
{{- printf "%s-backend" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Detection fullname
*/}}
{{- define "ai-soc.detection.fullname" -}}
{{- printf "%s-detection" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Correlation fullname
*/}}
{{- define "ai-soc.correlation.fullname" -}}
{{- printf "%s-correlation" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
AI Engine fullname
*/}}
{{- define "ai-soc.aiengine.fullname" -}}
{{- printf "%s-ai-engine" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Frontend fullname
*/}}
{{- define "ai-soc.frontend.fullname" -}}
{{- printf "%s-frontend" (include "ai-soc.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
