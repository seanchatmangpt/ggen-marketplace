# emitted_rust/

Empty by design. This directory receives the ggen-synced emission of
`templates/rust/` once the pack `ggen.toml` carries the three
`[[generation.rules]]` entries in `templates/rust/BINDING_CONTRACT.md`
(sync addendum). That edit belongs to R1/R14; this lane does not own the
manifest.

The compile smoke for the templates ran against a hand-instantiated render
in a /tmp scratch crate — see `../qualification/rust_emission_note.md` for
the real commands and exits.
