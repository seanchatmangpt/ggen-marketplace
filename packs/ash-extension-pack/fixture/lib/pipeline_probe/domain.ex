defmodule PipelineProbe.Domain do
  @moduledoc "Consumer-owned Ash domain for the receipted-action fixture."
  use Ash.Domain, validate_config_inclusion?: false

  resources do
    resource PipelineProbe.Notice
  end
end
