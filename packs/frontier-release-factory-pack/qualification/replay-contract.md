# Replay contract

For a fixed tuple `(source graph digest, pack commit, ggen runtime identity, query bindings)`, the working-backwards, acceptance, and earned-release projections must be deterministic. Replay may verify prior manufacture but must not create external repositories, publish releases, or otherwise re-actuate DO side effects.
