#!/usr/bin/env bash
# xaas-ash-build-extend.sh -- Part 3: upgrade every resource from --extend ets
# (Part 1's structural proof) to real postgres+json_api+graphql extensions,
# using the confirmed `mix ash.extend` command (not the deprecated
# `ash.patch.extend`) and its real short-code table, verified from Ash's own
# source this session (deps/ash/lib/mix/tasks/ash.extend.ex). Run AFTER
# xaas-ash-build-ecosystem.sh (Part 2) has installed ash_postgres/
# ash_json_api/ash_graphql -- these short codes fail Code.ensure_loaded?/1
# and error out listing available extensions if those packages are absent,
# confirmed by this session's own earlier --extend postgres failure.

set -euo pipefail

echo "=== XaaS resource extension upgrade: $(date) ==="

mix ash.extend Xaas.Billing.ApprovalInvoiceReconciliationApprove postgres,json_api,graphql --yes
mix ash.extend Xaas.Billing.ApprovalPatchSlaCreditApply postgres,json_api,graphql --yes
mix ash.extend Xaas.Billing.ApprovalPricingOverride postgres,json_api,graphql --yes
mix ash.extend Xaas.Billing.ApprovalQuotaOverride postgres,json_api,graphql --yes
mix ash.extend Xaas.Billing.ApprovalSlaCreditApply postgres,json_api,graphql --yes
mix ash.extend Xaas.Billing.ApprovalTierDowngrade postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalBackupRetentionChange postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalBreakGlassJustificationReview postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalChangeOfControlNotify postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalCmekKeyBinding postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalComplianceRotationBlock postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalDeniedPartyOverride postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalDeploymentQuarantine postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalDrFailover postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalDsarErasure postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalEnvironmentPromote postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalExportSubscriptionUpdate postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalFreezeOverride postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalGeofenceExceptionGrant postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalInsurancePolicyUpdate postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalLegalHoldRelease postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalLeRequestRespond postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalOrgDelete postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalPentestFindingResolve postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalPersonnelAttestationRecord postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalSourceEscrowSnapshot postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalSsoRoleMappingUpdate postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalSubprocessorRegistryUpdate postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.ApprovalVendorOffboardingAttestationIssue postgres,json_api,graphql --yes
mix ash.extend Xaas.Governance.DataDestructionCertificateIssue postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.ApprovalCastleVerbSchedule postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.ApprovalK8sFaultRemediateSuggest postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.CastleVerbFortune5Requirements postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.CastleVerbInventoryComponents postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.CastleVerbInventoryGoals postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.RouteCastleDeploy postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.RouteCastleRun postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.RouteCastleSchedule postgres,json_api,graphql --yes
mix ash.extend Xaas.Operations.RouteCastleSunset postgres,json_api,graphql --yes
mix ash.extend Xaas.Platform.RouteFeatureFlags postgres,json_api,graphql --yes
mix ash.extend Xaas.Platform.RouteOrgsCustomDomain postgres,json_api,graphql --yes
mix ash.extend Xaas.Platform.RouteProjects postgres,json_api,graphql --yes
mix ash.extend Xaas.Platform.RouteProjectsBackups postgres,json_api,graphql --yes
mix ash.extend Xaas.Platform.RouteSecrets postgres,json_api,graphql --yes

# Domain-level API wiring (json_api/graphql routes/queries/mutations --
# real short codes, domain-scope from the same ash.extend short-code table)
mix ash.extend Xaas.Operations json_api,graphql --yes
mix ash.extend Xaas.Governance json_api,graphql --yes
mix ash.extend Xaas.Billing json_api,graphql --yes
mix ash.extend Xaas.Platform json_api,graphql --yes

mix compile

echo "=== Extension upgrade complete: $(date) ==="
echo "Each of the 44 resources' HAND-EDIT actions/policies (from Part 1) must"
echo "still be added by hand -- ash.extend only adds data-layer/API' extensions,"
echo "it does not touch actions/policies blocks."
