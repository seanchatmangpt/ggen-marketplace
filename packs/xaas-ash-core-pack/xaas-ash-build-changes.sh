#!/usr/bin/env bash
# xaas-ash-build-changes.sh -- Part 4: real, generator-backed Change/Validation
# modules per resource. Confirmed real commands (mix ash.gen.change/.validation
# scaffold standalone modules -- this IS a real generator, unlike the inline
# actions/policies DSL in Part 1's HAND-EDIT blocks, which have no generator).
# Run after Part 1. Each generated module is then wired into the resource's
# `change`/`validate` calls by hand (still a HAND-EDIT step -- wiring a
# generated module into a DSL block has no generator either, confirmed same
# as Part 1's finding).

set -euo pipefail

echo "=== XaaS per-resource change/validation modules: $(date) ==="

mix ash.gen.change Xaas.Billing.Changes.ApprovalInvoiceReconciliationApproveApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalInvoiceReconciliationApproveRequiresApprover --yes
mix ash.gen.change Xaas.Billing.Changes.ApprovalPatchSlaCreditApplyApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalPatchSlaCreditApplyRequiresApprover --yes
mix ash.gen.change Xaas.Billing.Changes.ApprovalPricingOverrideApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalPricingOverrideRequiresApprover --yes
mix ash.gen.change Xaas.Billing.Changes.ApprovalQuotaOverrideApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalQuotaOverrideRequiresApprover --yes
mix ash.gen.change Xaas.Billing.Changes.ApprovalSlaCreditApplyApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalSlaCreditApplyRequiresApprover --yes
mix ash.gen.change Xaas.Billing.Changes.ApprovalTierDowngradeApprove --yes
mix ash.gen.validation Xaas.Billing.Validations.ApprovalTierDowngradeRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalBackupRetentionChangeApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalBackupRetentionChangeRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalBreakGlassJustificationReviewApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalBreakGlassJustificationReviewRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalChangeOfControlNotifyApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalChangeOfControlNotifyRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalCmekKeyBindingApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalCmekKeyBindingRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalComplianceRotationBlockApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalComplianceRotationBlockRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalDeniedPartyOverrideApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalDeniedPartyOverrideRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalDeploymentQuarantineApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalDeploymentQuarantineRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalDrFailoverApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalDrFailoverRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalDsarErasureApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalDsarErasureRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalEnvironmentPromoteApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalEnvironmentPromoteRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalExportSubscriptionUpdateApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalExportSubscriptionUpdateRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalFreezeOverrideApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalFreezeOverrideRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalGeofenceExceptionGrantApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalGeofenceExceptionGrantRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalInsurancePolicyUpdateApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalInsurancePolicyUpdateRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalLegalHoldReleaseApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalLegalHoldReleaseRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalLeRequestRespondApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalLeRequestRespondRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalOrgDeleteApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalOrgDeleteRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalPentestFindingResolveApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalPentestFindingResolveRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalPersonnelAttestationRecordApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalPersonnelAttestationRecordRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalSourceEscrowSnapshotApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalSourceEscrowSnapshotRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalSsoRoleMappingUpdateApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalSsoRoleMappingUpdateRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalSubprocessorRegistryUpdateApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalSubprocessorRegistryUpdateRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.ApprovalVendorOffboardingAttestationIssueApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.ApprovalVendorOffboardingAttestationIssueRequiresApprover --yes
mix ash.gen.change Xaas.Governance.Changes.DataDestructionCertificateIssueApprove --yes
mix ash.gen.validation Xaas.Governance.Validations.DataDestructionCertificateIssueRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.ApprovalCastleVerbScheduleApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.ApprovalCastleVerbScheduleRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.ApprovalK8sFaultRemediateSuggestApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.ApprovalK8sFaultRemediateSuggestRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.CastleVerbFortune5RequirementsApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.CastleVerbFortune5RequirementsRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.CastleVerbInventoryComponentsApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.CastleVerbInventoryComponentsRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.CastleVerbInventoryGoalsApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.CastleVerbInventoryGoalsRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.RouteCastleDeployApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.RouteCastleDeployRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.RouteCastleRunApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.RouteCastleRunRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.RouteCastleScheduleApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.RouteCastleScheduleRequiresApprover --yes
mix ash.gen.change Xaas.Operations.Changes.RouteCastleSunsetApprove --yes
mix ash.gen.validation Xaas.Operations.Validations.RouteCastleSunsetRequiresApprover --yes
mix ash.gen.change Xaas.Platform.Changes.RouteFeatureFlagsApprove --yes
mix ash.gen.validation Xaas.Platform.Validations.RouteFeatureFlagsRequiresApprover --yes
mix ash.gen.change Xaas.Platform.Changes.RouteOrgsCustomDomainApprove --yes
mix ash.gen.validation Xaas.Platform.Validations.RouteOrgsCustomDomainRequiresApprover --yes
mix ash.gen.change Xaas.Platform.Changes.RouteProjectsApprove --yes
mix ash.gen.validation Xaas.Platform.Validations.RouteProjectsRequiresApprover --yes
mix ash.gen.change Xaas.Platform.Changes.RouteProjectsBackupsApprove --yes
mix ash.gen.validation Xaas.Platform.Validations.RouteProjectsBackupsRequiresApprover --yes
mix ash.gen.change Xaas.Platform.Changes.RouteSecretsApprove --yes
mix ash.gen.validation Xaas.Platform.Validations.RouteSecretsRequiresApprover --yes

mix compile

echo "=== Change/validation module generation complete: $(date) ==="
echo "HAND-EDIT still required: wire each generated Changes/Validations module into"
echo "its resource's update action (change {Domain}.Changes.{X}Approve) and policy"
echo "(validate {Domain}.Validations.{X}RequiresApprover) -- no generator wires this"
echo "automatically, confirmed same as Part 1."
