//! Chicago-style verification of a real ggen-generated MCP surface.
//! No doubles: the module under test IS the real generated file, included verbatim.
//! Every assertion is on real resulting state, never on an interaction.

#[path = "GENERATED_PATH"]
mod surface;

use surface::*;

fn main() {
    let mut failures = 0usize;
    let mut check = |name: &str, ok: bool, detail: String| {
        println!("{} {} :: {}", if ok { "PASS" } else { "FAIL" }, name, detail);
        if !ok {
            failures += 1;
        }
    };

    check(
        "surface_is_non_empty",
        !MCP_TOOLS.is_empty(),
        format!("{} tools for server {}", MCP_TOOLS.len(), MCP_SERVER_NAME),
    );

    // AUTHORITY BOUNDARY: the property this pack exists to preserve.
    let leaks: Vec<&str> = MCP_TOOLS
        .iter()
        .filter(|t| t.consequence_class == "Do" && !t.requires_admission)
        .map(|t| t.name)
        .collect();
    check(
        "no_ambient_do_authority",
        leaks.is_empty(),
        format!("Do tools lacking admission: {:?}", leaks),
    );

    let bad_replay: Vec<&str> = MCP_TOOLS
        .iter()
        .filter(|t| t.consequence_class == "Do" && t.replay_safe)
        .map(|t| t.name)
        .collect();
    check(
        "no_do_tool_claims_replay_safety",
        bad_replay.is_empty(),
        format!("offenders: {:?}", bad_replay),
    );

    // Namespacing really came from the graph, not a template literal.
    let prefix = format!("{}.", MCP_TOOL_NAMESPACE);
    let unnamespaced: Vec<&str> = MCP_TOOLS
        .iter()
        .filter(|t| !t.name.starts_with(&prefix))
        .map(|t| t.name)
        .collect();
    check(
        "every_tool_is_namespaced_from_graph",
        unnamespaced.is_empty(),
        format!("namespace {:?}, offenders {:?}", MCP_TOOL_NAMESPACE, unnamespaced),
    );

    let undescribed = MCP_TOOLS.iter().filter(|t| t.description.is_empty()).count();
    check(
        "every_tool_is_described",
        undescribed == 0,
        format!("{} undescribed", undescribed),
    );

    // Lookup returns real state for both the namespaced and bare spelling.
    let first = MCP_TOOLS[0];
    let by_full = lookup_mcp_tool(first.name);
    let by_bare = lookup_mcp_tool(first.operation_id);
    check(
        "lookup_resolves_both_spellings",
        by_full == Some(&MCP_TOOLS[0]) && by_bare == Some(&MCP_TOOLS[0]),
        format!("{} / {}", first.name, first.operation_id),
    );

    check(
        "lookup_of_unknown_tool_is_none",
        lookup_mcp_tool("this.tool.does.not.exist").is_none(),
        "unknown name resolves to None".to_string(),
    );

    let observational = observational_tools().count();
    let consequential = MCP_TOOLS.iter().filter(|t| t.consequence_class == "Do").count();
    check(
        "read_do_partition_is_total",
        observational + consequential == MCP_TOOLS.len(),
        format!("{} read + {} do = {}", observational, consequential, MCP_TOOLS.len()),
    );

    let required_params: usize = MCP_TOOLS
        .iter()
        .flat_map(|t| t.parameters.iter())
        .filter(|p| p.required)
        .count();
    let total_params: usize = MCP_TOOLS.iter().map(|t| t.parameters.len()).sum();
    check(
        "parameters_survived_projection",
        total_params > 0,
        format!("{} parameters, {} required", total_params, required_params),
    );

    println!("---");
    if failures == 0 {
        println!("ALL CHECKS PASSED for {}", MCP_SERVER_NAME);
    } else {
        println!("{} CHECK(S) FAILED for {}", failures, MCP_SERVER_NAME);
        std::process::exit(1);
    }
}
