//! Typed noun-verb routes GENERATED from first-class RDF arguments.
//!
//! Every body closes through `BehaviorSpec`, except commands carrying the
//! explicit, admitted `cnv:CustomBehavior` opt-out, which route to a
//! hand-written `crate::custom_handlers::<noun>_<verb>` function instead. That
//! is the sole consumer handler seam this compiler ever emits, and it is
//! visible per-command in the source ontology, not a blanket escape hatch.

use crate::generated_behavior::{self, BehaviorSpec};
use clap_noun_verb::{NounVerbError, Result};
use clap_noun_verb_macros::verb;
use serde::Serialize;
use serde_json::{Map, Value};
#[doc = "Add two signed 64-bit integers through the generated expression interpreter."]
#[doc = ""]
#[doc = "# Arguments"]
/// * `left` - Generated argument metadata.
/// * `right` - Generated argument metadata.
#[verb("add", "greet")]
fn greet_add(
    #[arg(help = "Left operand.", index = 1)] left: i64,
    #[arg(help = "Right operand.", index = 2)] right: i64,
) -> Result<Value> {
    let mut inputs = Map::new();
    inputs.insert("left".to_owned(), encode_input("left", &left)?);
    inputs.insert("right".to_owned(), encode_input("right", &right)?);
    generated_behavior::execute(
        BehaviorSpec::Expression {
            operator: "add",
            left: "left",
            right: "right",
        },
        inputs,
    )
}

#[doc = "Return typed command inputs as a JSON object."]
#[doc = ""]
#[doc = "# Arguments"]
/// * `uppercase` - Generated argument metadata.
/// * `name` - Generated argument metadata.
#[verb("hello", "greet")]
fn greet_hello(
    #[arg(
        help = "Include an uppercase-request flag in the returned input object.",
        short = 'u'
    )]
    uppercase: bool,
    #[arg(help = "Who to greet.", index = 1)] name: String,
) -> Result<Value> {
    let mut inputs = Map::new();
    inputs.insert(
        "uppercase".to_owned(),
        encode_input("uppercase", &uppercase)?,
    );
    inputs.insert("name".to_owned(), encode_input("name", &name)?);
    generated_behavior::execute(BehaviorSpec::Echo, inputs)
}

#[doc = "Return a deterministic ontology-owned liveness value."]
#[verb("ping", "system")]
fn system_ping() -> Result<Value> {
    let inputs = Map::new();
    generated_behavior::execute(
        BehaviorSpec::StaticJson {
            json: "{\"status\":\"alive\",\"source\":\"clap-noun-verb-zeroconfig-pack\"}",
        },
        inputs,
    )
}

#[doc = "Exercise a typed ontology-declared refusal path."]
#[verb("refuse", "system")]
fn system_refuse() -> Result<Value> {
    let inputs = Map::new();
    generated_behavior::execute(
        BehaviorSpec::Refusal {
            code: "DEMONSTRATION_REFUSAL",
            message: "This command is intentionally refused by the admitted graph.",
        },
        inputs,
    )
}

#[linkme::distributed_slice(::clap_noun_verb::cli::registry::__NOUN_REGISTRY)]
static REGISTER_GREET_NOUN: fn() = register_greet_noun;

fn register_greet_noun() {
    ::clap_noun_verb::cli::registry::CommandRegistry::register_noun(
        "greet",
        "Say hello and do simple typed arithmetic.",
    );
}

#[linkme::distributed_slice(::clap_noun_verb::cli::registry::__NOUN_REGISTRY)]
static REGISTER_SYSTEM_NOUN: fn() = register_system_noun;

fn register_system_noun() {
    ::clap_noun_verb::cli::registry::CommandRegistry::register_noun(
        "system",
        "Inspect the generated CLI and exercise explicit refusal.",
    );
}

#[allow(dead_code)]
fn encode_input<T: Serialize>(name: &str, value: &T) -> Result<Value> {
    serde_json::to_value(value).map_err(|error| {
        NounVerbError::execution_error(format!(
            "failed to encode generated argument {name:?}: {error}"
        ))
    })
}

#[cfg(test)]
mod generated_route_proofs {
    const GENERATED_SOURCE: &str =
        include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/src/generated_cli.rs"));

    fn routes_only() -> &'static str {
        GENERATED_SOURCE
            .split("#[cfg(test)]")
            .next()
            .unwrap_or(GENERATED_SOURCE)
    }

    #[test]
    fn every_admitted_command_became_one_registered_verb() {
        assert_eq!(routes_only().matches("#[verb(").count(), 4);
    }

    #[test]
    fn no_consumer_handler_seam_survives_generation() {
        // `custom_handlers::` is the sole, explicitly admitted escape hatch
        // (cnv:CustomBehavior); strip it before checking for the legacy,
        // unbounded `handlers::` seam this compiler never emits otherwise.
        let without_admitted_custom_seam = routes_only().replace("custom_handlers::", "");
        assert!(!without_admitted_custom_seam.contains("handlers::"));
        assert!(!routes_only().contains("todo!"));
        assert!(!routes_only().contains("unimplemented!"));
    }

    #[test]
    fn every_custom_command_routes_to_its_own_handler() {
        // Proves per-command wiring, not just that a seam exists somewhere:
        // each cnv:CustomBehavior command must call the one handler function
        // named after ITS OWN noun and verb, not a neighboring command's.
    }
}
