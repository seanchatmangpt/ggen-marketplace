defmodule Cs2SemanticWorkFixture.GeneratedTest do
  use ExUnit.Case, async: true

  alias Cs2SemanticWork.Consumer
  alias Cs2SemanticWork.ConsumerAdapter
  alias Cs2SemanticWork.ConsumerWork

  @root System.fetch_env!("CS2_PACK_GENERATED")

  defp generated_json(rel), do: @root |> Path.join(rel) |> File.read!() |> Jason.decode!()

  defp batch, do: generated_json("work-projection-batch.json")

  describe "ConsumerAdapter.admit/1 over the generated batch projection" do
    test "admits the generated batch with authority :none and every work item" do
      generated = batch()
      assert {:ok, admitted} = ConsumerAdapter.admit(generated)
      assert admitted.authority == :none
      assert admitted.subject == generated["subject"]
      assert admitted.batch_id == generated["batchId"]

      assert Enum.map(admitted.work, & &1.work_key) ==
               Enum.map(generated["work"], & &1["workKey"])

      assert length(admitted.work) >= 2
    end

    test "refuses a duplicate work key" do
      b = batch()
      [first | _] = b["work"]
      assert {:error, :duplicate_work_key} = ConsumerAdapter.admit(%{b | "work" => b["work"] ++ [first]})
    end

    test "refuses an unknown dependency and a self dependency" do
      b = batch()
      [first | rest] = b["work"]
      unknown = Map.put(first, "dependencies", ["CS2-WRK-NOT-IN-BATCH"])
      assert {:error, :open_dependency} = ConsumerAdapter.admit(%{b | "work" => [unknown | rest]})

      self_dep = Map.put(first, "dependencies", [first["workKey"]])
      assert {:error, :open_dependency} = ConsumerAdapter.admit(%{b | "work" => [self_dep | rest]})
    end

    test "refuses a foreign subject, a DO authority, a short SHA, and an empty batch" do
      b = batch()
      assert {:error, :refused_cs2_batch} = ConsumerAdapter.admit(%{b | "subject" => "https://example.org/other"})
      assert {:error, :refused_cs2_batch} = ConsumerAdapter.admit(%{b | "authority" => "DO"})

      short = put_in(b, ["source", "sha"], String.slice(b["source"]["sha"], 0, 7))
      assert {:error, :invalid_source} = ConsumerAdapter.admit(short)

      assert {:error, :refused_cs2_batch} = ConsumerAdapter.admit(%{b | "work" => []})
    end
  end

  describe "Consumer.admit/1 over the generated per-item projections" do
    test "admits every generated work/*.json projection and refuses mutations" do
      files = Path.wildcard(Path.join([@root, "work", "*.json"]))
      assert files != []

      for file <- files do
        projection = file |> File.read!() |> Jason.decode!()
        assert {:ok, admitted} = Consumer.admit(projection)
        assert admitted.authority == :none
        assert admitted.work_key == Path.basename(file, ".json")
        assert admitted.origin.sha == projection["source"]["sha"]

        assert {:error, :refused_cs2_projection} = Consumer.admit(%{projection | "authority" => "DO"})
        assert {:error, :refused_cs2_projection} = Consumer.admit(Map.delete(projection, "falsifier"))
      end

      assert {:error, :refused_cs2_projection} = Consumer.admit("not a map")
    end
  end

  describe "typed ConsumerWork modules over the generated consumer JSON" do
    defp rows(kind) do
      doc = generated_json("consumer/consumer-#{kind}.json")
      assert doc["kind"] == kind
      assert doc["authority"] == "NONE"
      Enum.map(doc["payload"], fn row -> Map.new(row, fn {k, v} -> {snake(k), v} end) end)
    end

    defp snake(key), do: key |> Macro.underscore() |> String.to_atom()

    test "work rows build structs, sources validate, and authority is NONE-only" do
      for row <- rows("work") do
        work = struct!(ConsumerWork.Work, row)
        assert work.authority == "NONE"
      end

      assert Enum.all?(rows("source"), &ConsumerWork.Source.valid?/1)
      refute ConsumerWork.Source.valid?(%{source_repo: "r", source_sha: "abc1234"})

      assert {:ok, _} = ConsumerWork.Admission.admit(%{"authority" => "NONE"})
      assert {:error, :authority_refused} = ConsumerWork.Admission.admit(%{"authority" => "DO"})
      assert ConsumerWork.Batch.authority() == "NONE"
    end

    test "dependency, projection, and roots rows agree with the generated batch" do
      deps = rows("dependency")
      assert deps != []
      assert Enum.all?(deps, &ConsumerWork.Dependency.valid?/1)
      refute ConsumerWork.Dependency.valid?(%{work_key: "K", depends_on_work_key: "K"})

      assert Enum.all?(rows("projection"), &ConsumerWork.Projection.requested?/1)

      expected_roots =
        for item <- batch()["work"], item["dependencies"] == [], do: item["workKey"]

      assert Enum.map(rows("roots"), & &1.work_key) == expected_roots
      assert Enum.map(ConsumerWork.Batch.roots(deps ++ rows("roots")), & &1.work_key) == expected_roots
    end
  end
end
