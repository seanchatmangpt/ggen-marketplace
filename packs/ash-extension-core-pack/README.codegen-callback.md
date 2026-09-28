```turtle
@prefix aex: <http://seanchatmangpt.github.io/packs/ash-extension-core#> .

<#extension> a aex:AshExtensionSpec ;
  aex:codegenTask "my_extension.codegen" ;
  aex:codegenName "my_extension" .
```

When present, the generated Spark extension implements the optional `Ash.Extension.codegen/1` callback by re-enabling and running exactly the admitted Mix task. `codegenName` is display metadata only.
