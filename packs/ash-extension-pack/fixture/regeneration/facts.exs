# Regeneration specimen facts -- the ontology in miniature.
#
# These are THE semantic facts for the specimen extension. They mirror,
# key-for-key, the aex:AshExtensionSpec vocabulary of
# packs/ash-extension-pack/ontology.ttl (packageName, moduleName, sections,
# entities, schema fields, verifiers, InfoGetters, ReactorSteps, installer
# target, singleExtensionKind) so the courts exercise the same sync law the
# real pack enforces: facts -> generated extension, facts authoritative,
# generated files never authoritative.
#
# Everything downstream (generated extension source, committed specimen,
# regeneration/drift digests) is a pure function of this file.

%{
  package_name: "regeneration_specimen",
  module_name: "RegenerationSpecimen.Resource",
  extension_target: "resource",
  task_module_name: "RegenerationSpecimen",
  single_extension_kind: "regeneration_specimen",
  installer_target: "RegenerationSpecimen.Resource",
  installer_idempotent: true,
  # aex:afterTransformer rows -- the Persist-transformer ordering facts.
  persist_after: [
    "Ash.Resource.Transformers.CachePrimaryKey",
    "Ash.Resource.Transformers.SetRelationshipInformation"
  ],
  verifiers: [
    %{
      name: "unique_event_name",
      doc: "Every :audit event name must be unique within the resource."
    },
    %{
      name: "valid_projection",
      doc: "Every :audit projection attribute must reference an attribute that actually exists on the resource."
    }
  ],
  info_getters: [
    %{name: "audit_index", source_section: "audit"}
  ],
  sections: [
    %{
      name: "audit",
      order: 1,
      describe: "Audit event and projection declarations.",
      singleton_entity_keys: [],
      section_fields: [],
      entities: [
        %{
          name: "event",
          order: 1,
          struct: "RegenerationSpecimen.Dsl.Event",
          identifier: nil,
          args: [],
          fields: [
            %{
              name: "name",
              type: "atom",
              required: true,
              default: nil,
              doc: "The audited event's slug."
            },
            %{
              name: "description",
              type: "string",
              required: false,
              default: nil,
              doc: "Human-readable description of what triggers this event."
            }
          ]
        },
        %{
          name: "projection",
          order: 2,
          struct: "RegenerationSpecimen.Dsl.Projection",
          identifier: "attribute",
          args: ["attribute"],
          fields: [
            %{
              name: "attribute",
              type: "atom",
              required: true,
              default: nil,
              doc: "Resource attribute this projection reads."
            },
            %{
              name: "strategy",
              type: "one_of",
              one_of: ["eager", "lazy"],
              required: false,
              default: ":eager",
              doc: "Projection evaluation strategy."
            }
          ]
        }
      ]
    }
  ],
  steps: [
    %{
      name: "admit",
      order: 1,
      module: "Admit",
      wait_for: [],
      max_retries: 0,
      has_compensate: false,
      is_return: false,
      scope: "regeneration_specimen"
    },
    %{
      name: "deliver",
      order: 2,
      module: "Deliver",
      wait_for: ["admit"],
      max_retries: 3,
      has_compensate: true,
      is_return: false,
      scope: "regeneration_specimen"
    },
    %{
      name: "seal_receipt",
      order: 3,
      module: "SealReceipt",
      wait_for: ["deliver"],
      max_retries: 0,
      has_compensate: false,
      is_return: true,
      scope: "regeneration_specimen"
    }
  ]
}
