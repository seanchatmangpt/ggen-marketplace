use std::{env, error::Error, fs, path::PathBuf, process};

use serde::{Deserialize, Serialize};
use star_toml::{
    loader::{ConfigLifecycle, TrustedLoader},
    Validate, Validator,
};

const STAR_TOML_SHA: &str = "8395515cf8e68bfdc9edff49fb358c4f1da7c795";

#[derive(Debug, Deserialize, Serialize)]
struct MarketplaceConfig {
    schema_version: String,
    marketplace: MarketplaceMeta,
    qualification: QualificationConfig,
    ggen: GgenConfig,
}

/// This repository's own release identity -- an org-owned version for a
/// whole registry snapshot, independent of individual packs' SemVer and
/// of `ggen.version` (the pinned upstream binary this repo qualifies
/// against).
#[derive(Debug, Deserialize, Serialize)]
struct MarketplaceMeta {
    version: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct QualificationConfig {
    workers: u64,
    timeout_seconds: u64,
}

#[derive(Debug, Deserialize, Serialize)]
struct GgenConfig {
    repository: String,
    version: String,
    assets: AssetMatrix,
}

#[derive(Debug, Deserialize, Serialize)]
struct AssetMatrix {
    linux_x86_64: AssetConfig,
    linux_aarch64: AssetConfig,
    darwin_aarch64: AssetConfig,
    darwin_x86_64: AssetConfig,
}

#[derive(Debug, Deserialize, Serialize)]
struct AssetConfig {
    archive: String,
    sha256: String,
}

impl Validate for MarketplaceConfig {
    fn validate(&self, v: &mut Validator) {
        v.check_non_empty("schema_version", &self.schema_version);
        v.field("marketplace", |v| {
            v.check_non_empty("version", &self.marketplace.version);
        });
        v.field("qualification", |v| {
            v.check_range("workers", self.qualification.workers, 1..=16);
            v.check_range("timeout_seconds", self.qualification.timeout_seconds, 1..=5);
        });
        v.field("ggen", |v| {
            v.check_non_empty("repository", &self.ggen.repository);
            v.check_non_empty("version", &self.ggen.version);
            v.field("assets", |v| {
                validate_asset(v, "linux_x86_64", &self.ggen.assets.linux_x86_64);
                validate_asset(v, "linux_aarch64", &self.ggen.assets.linux_aarch64);
                validate_asset(v, "darwin_aarch64", &self.ggen.assets.darwin_aarch64);
                validate_asset(v, "darwin_x86_64", &self.ggen.assets.darwin_x86_64);
            });
        });
    }
}

impl ConfigLifecycle for MarketplaceConfig {}

fn validate_asset(v: &mut Validator, name: &str, asset: &AssetConfig) {
    v.field(name, |v| {
        v.check_non_empty("archive", &asset.archive);
        v.check_non_empty("sha256", &asset.sha256);
    });
}

#[derive(Serialize)]
struct AdmissionReceipt<'a> {
    schema: &'static str,
    q_config: u8,
    standing: &'static str,
    star_toml_sha: &'static str,
    witness_blake3: &'a str,
    source_count: usize,
    layer_count: usize,
    env_override_count: usize,
    config: &'a MarketplaceConfig,
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = env::args().skip(1);
    let config_path = PathBuf::from(args.next().unwrap_or_else(|| "marketplace.toml".to_owned()));
    let output_path = args.next().map(PathBuf::from);
    if args.next().is_some() {
        return Err("usage: ggen-marketplace-config [marketplace.toml] [output.json]".into());
    }

    let admitted = TrustedLoader::new()
        .layer_file(&config_path)
        .load_admitted::<MarketplaceConfig>()?;

    let receipt = AdmissionReceipt {
        schema: "https://ggen.dev/marketplace/config-admission/v1",
        q_config: 1,
        standing: "ADMITTED",
        star_toml_sha: STAR_TOML_SHA,
        witness_blake3: admitted.witness().hash(),
        source_count: admitted.source_report().entries.len(),
        layer_count: admitted.layer_report().entries.len(),
        env_override_count: admitted.env_report().entries.len(),
        config: admitted.value(),
    };
    let encoded = serde_json::to_string_pretty(&receipt)? + "\n";

    if let Some(path) = output_path {
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                fs::create_dir_all(parent)?;
            }
        }
        fs::write(path, encoded)?;
    } else {
        print!("{encoded}");
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("REFUSED:MARKETPLACE_CONFIG_NOT_ADMITTED:{error}");
        process::exit(2);
    }
}
