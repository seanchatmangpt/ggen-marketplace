import Config

config :ash, default_string_length_count: :codepoints

config :ash, :validate_domain_resource_inclusion?, false
config :ash, :validate_domain_config_inclusion?, false
config :pipeline_probe, ash_domains: [PipelineProbe.Domain]
