# semantic-life-loop-pack

Reusable GGen bridge for:

`LifeGym observation + BibleGym formation packet -> authority-free observation delta -> Semantic Jira admission`.

It does **not** create WorkOrder authority. The generated artifact is a
candidate-only JSON projection intended for
`GgenIgniter.SemanticJira.observation_delta_work_orders/2`.

The pack reuses the existing LifeGym and BibleGym anchor IRIs and fixes all
authority fields in the template so ontology data cannot smuggle a DO path.

Expected composition:

```text
lifegym-world-pack
      +
biblegym-pack
      +
semantic-life-loop-pack
      |
      v
ggen sync run
      |
      v
semantic-life-loop.observation-delta.json
      |
      v
ggen_igniter Semantic Jira admission
```

A consumer replaces the worked-example ABox with its own bounded episode facts
while preserving the pack vocabulary and gates.
