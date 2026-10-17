# Cascade sweep plan — GENERATED from smalt-substrate-pack ontology via
# ggen_igniter.sync (engine sparql). DO NOT EDIT — regenerate with the
# mix ggen_igniter.sync invocation in the pack README.
#
# Source of truth: packs/smalt-substrate-pack/ontology.ttl
#   smalt:contains walk + smalt:dataPlaneTable / smalt:keyStyle /
#   smalt:dataPlaneKeyPrefix annotations (queries/cascade_sweep_rows.rq).
# PROTOTYPE artifact (cascade-projection lane, 2026-10-16): NOT wired into
# smalt lib/. A later lane replaces the hand-written per-service drop_*
# dispatch (router.ex cascade_sweep/2 + BlobStorage.drop_account_data/1 +
# Cosmos/SB/EH/Ledger sweeps) with this graph walk.
defmodule Smalt.CascadeSweep do
  @moduledoc """
  Graph-walk cascade teardown plan projected from the ontology.
  """

  rows = [
    %{
      root: "Microsoft.App/containerApps",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Attestation/attestationProviders",
      table: :smalt_attestation_baseline,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Authorization/roleAssignments",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Compute/diskEncryptionSets",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Compute/disks",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Compute/virtualMachines",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.ConfidentialLedger/ledgers",
      table: :smalt_ledger_meta,
      style: :ledger_tx,
      prefix: "<ledger>/"
    },
    %{
      root: "Microsoft.ConfidentialLedger/ledgers",
      table: :smalt_ledger_transactions,
      style: :ledger_tx,
      prefix: "<ledger>/"
    },
    %{
      root: "Microsoft.ConfidentialLedger/managedCCFs",
      table: :smalt_ledger_meta,
      style: :ledger_tx,
      prefix: nil
    },
    %{
      root: "Microsoft.ConfidentialLedger/managedCCFs",
      table: :smalt_ledger_transactions,
      style: :ledger_tx,
      prefix: nil
    },
    %{
      root: "Microsoft.ContainerService/managedClusters",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.DevTestLab/schedules",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlContainers",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlContainers",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlContainers",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlContainers",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.EventGrid/topics",
      table: :smalt_event_messages,
      style: :topic_stream,
      prefix: nil
    },
    %{
      root: "Microsoft.EventHub/namespaces",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: nil
    },
    %{
      root: "Microsoft.EventHub/namespaces",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces",
      table: :smalt_eh_partitions,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces",
      table: :smalt_event_messages,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces/eventhubs",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: nil
    },
    %{
      root: "Microsoft.EventHub/namespaces/eventhubs",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces/eventhubs",
      table: :smalt_eh_partitions,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces/eventhubs",
      table: :smalt_event_messages,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.EventHub/namespaces/eventhubs/consumergroups",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: nil
    },
    %{
      root: "Microsoft.Insights/diagnosticSettings",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/managedHSMs",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults",
      table: :smalt_vault_deleted_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults",
      table: :smalt_vault_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults",
      table: :smalt_vault_secrets,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults/keys",
      table: :smalt_vault_deleted_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults/keys",
      table: :smalt_vault_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults/secrets",
      table: :smalt_vault_deleted_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.KeyVault/vaults/secrets",
      table: :smalt_vault_secrets,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/networkInterfaces",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/networkSecurityGroups",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/privateDnsZones",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/privateEndpoints",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/subnets",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Network/virtualNetworks",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.OperationalInsights/workspaces",
      table: :smalt_sentinel_rows,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.OperationalInsights/workspaces",
      table: :smalt_sentinel_streams,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Purview/accounts",
      table: :smalt_purview_edges,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Purview/accounts",
      table: :smalt_purview_entities,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_attestation_baseline,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_docs,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_lsn,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_pk_meta,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_cosmos_ru,
      style: :db_coll_doc,
      prefix: "<db>/<coll>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_eh_checkpoints,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_eh_partitions,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_event_messages,
      style: :topic_stream,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_event_messages,
      style: :ns_hub,
      prefix: "<ns>/<hub>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_ledger_meta,
      style: :ledger_tx,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_ledger_meta,
      style: :ledger_tx,
      prefix: "<ledger>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_ledger_transactions,
      style: :ledger_tx,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_ledger_transactions,
      style: :ledger_tx,
      prefix: "<ledger>/"
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_purview_edges,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_purview_entities,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_resource_groups,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sb_locks,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sb_messages,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sb_queues,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sb_sessions,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sb_tokens,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sentinel_rows,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_sentinel_streams,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_vault_deleted_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_vault_keys,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Resources/resourceGroups",
      table: :smalt_vault_secrets,
      style: :vault_name_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.SecurityInsights/onboardingStates",
      table: :smalt_sentinel_rows,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.SecurityInsights/onboardingStates",
      table: :smalt_sentinel_streams,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces",
      table: :smalt_sb_locks,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces",
      table: :smalt_sb_messages,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces",
      table: :smalt_sb_queues,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces",
      table: :smalt_sb_sessions,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces",
      table: :smalt_sb_tokens,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/queues",
      table: :smalt_sb_locks,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/queues",
      table: :smalt_sb_messages,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/queues",
      table: :smalt_sb_queues,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/queues",
      table: :smalt_sb_sessions,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/queues",
      table: :smalt_sb_tokens,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics",
      table: :smalt_sb_locks,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics",
      table: :smalt_sb_messages,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics",
      table: :smalt_sb_queues,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics",
      table: :smalt_sb_sessions,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics",
      table: :smalt_sb_tokens,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics/subscriptions",
      table: :smalt_sb_locks,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics/subscriptions",
      table: :smalt_sb_messages,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics/subscriptions",
      table: :smalt_sb_queues,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics/subscriptions",
      table: :smalt_sb_sessions,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.ServiceBus/namespaces/topics/subscriptions",
      table: :smalt_sb_tokens,
      style: :sb_queue_tuple,
      prefix: nil
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts",
      table: :smalt_resources,
      style: :arm_id_prefix,
      prefix: nil
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers",
      table: :smalt_blob_blocks,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers",
      table: :smalt_blob_containers,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers",
      table: :smalt_blob_snapshots,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers",
      table: :smalt_blobs,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    },
    %{
      root: "Microsoft.Storage/storageAccounts/blobServices/containers/immutabilityPolicies",
      table: :smalt_blob_policy,
      style: :acct_container,
      prefix: "<acct>/<container>/"
    }
  ]

  @rows rows

  @doc "Sweep entries for a root ARM type (nil if not cascade-covered)."
  def plan(root_type) do
    case Enum.filter(@rows, &(&1.root == root_type)) do
      [] ->
        nil

      entries ->
        entries
        |> Enum.map(&Map.delete(&1, :root))
        |> Enum.uniq()
    end
  end

  @doc "Types with a cascade plan (walk roots), sorted."
  def covered_types do
    @rows |> Enum.map(& &1.root) |> Enum.uniq() |> Enum.sort()
  end

  # Key-style dispatch. Binary-prefix styles sweep via Store.prefix_keys/2.
  # Tuple styles need :ets.select patterns over the entity name — generated
  # here as a SELECT-the-owner stub; the concrete match specs remain the
  # hand-written residue (see prototype verdict).
  @binary_styles [
    :arm_id_prefix,
    :acct_container,
    :db_coll_doc,
    :ns_hub,
    :ledger_tx,
    :topic_stream
  ]
  @tuple_styles [:sb_queue_tuple, :vault_name_tuple]

  def sweep(root_type, ids) when is_map(ids) do
    for %{table: t, style: s, prefix: p} <- plan(root_type) || [] do
      cond do
        s in @binary_styles and is_binary(p) ->
          base =
            p
            |> String.replace("<acct>", ids.account)
            |> String.replace("<container>", ids.container)
            |> String.replace("<db>", ids.db)
            |> String.replace("<coll>", ids.coll)
            |> String.replace("<ns>", ids.ns)
            |> String.replace("<hub>", ids.hub)
            |> String.replace("<ledger>", ids.ledger)
            |> String.downcase()

          {:prefix_sweep, t, base}

        s in @tuple_styles ->
          {:select_owner, t, s, Map.get(ids, :entity)}

        true ->
          {:singleton_delete, t}
      end
    end
  end
end
