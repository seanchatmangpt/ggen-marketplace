# Explanation: security and authority

A pack is data plus executable projection logic, so convenience must not erase authority boundaries. Marketplace CI therefore validates source with a read-only token and never commits formatting or generated corrections to a PR branch.

Symlinks are refused to keep reviewed pack paths self-contained. Optional SPARQL gates are treated as admission controls: they can prevent a bad manufacture request, but their existence alone does not prove that a downstream system is safe or authorized.

Most importantly, pack generation and external actuation are different operations. A pack can manufacture Terraform, GitHub workflow, MCP, API, or other artifacts without receiving authority to execute those artifacts. Any real DO boundary must be granted and receipted by the consumer system responsible for that authority.
