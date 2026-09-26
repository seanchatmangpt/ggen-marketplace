# ERRC ownership manifest

This pack closes the declaration half of repository-fact semantic compression.

```
RDF ownership facts
      |
      +-- fail closed:
      |   exact Git subject
      |   generated => generator + digest
      |   reused => source owner + digest
      |   materialized => source + receipt
      |   unique path/subject
      v
ggen deterministic projection
      |
      v
generated/ownership-manifest.json
      |
      v
@unrdf/manufacturing collectGitRepositoryFacts()
      |
      v
accountRepositoryFacts()
      |
      v
exact-subject ERRC receipt
```

The split is deliberate. The marketplace owns semantic declarations and
generation; UNRDF owns repository observation and accounting. The manifest
never supplies LOC, blob identity, file bytes, or Git state. Those are observed
from the repository itself, so an ontology claim cannot fabricate repository
facts.

Unknown ownership is not emitted as a special trusted value. Missing evidence
falls through to UNRDF's conservative rule: charge the path as handwritten.
No artifact in this pack grants DO authority.
