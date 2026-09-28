defmodule CS2.Consumer.Work do
  defstruct [:work_key,:subject,:source_repo,:source_sha,:objective,:acceptance,:falsifier,:next_edge,:path_scope,:projection_type,dependencies: [],authority: "NONE"]
end
