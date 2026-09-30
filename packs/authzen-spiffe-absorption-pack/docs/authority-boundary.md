# Authority boundary gate

A generated AuthZEN/SPIFFE adapter is admissible only when:

1. external policy decisions remain evidence;
2. attested workload identity remains authentication evidence;
3. PreparedEffect principal and digest are preserved exactly;
4. certificate issuance stays in the configured local C2 authority domain;
5. protected DO still requires actuator-local certificate verification and claim;
6. generated code contains no signing private key or protected effector credential.
