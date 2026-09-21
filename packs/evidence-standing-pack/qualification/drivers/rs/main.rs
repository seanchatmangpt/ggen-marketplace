// Golden-vector driver (rust). Usage: cargo run --offline -- <golden.vec>; includes generated src/es/chain.rs.
#[path = "es/chain.rs"]
mod chain;
use std::fs;

fn main() {
    let path = std::env::args().nth(1).expect("vec path");
    let text = fs::read_to_string(path).expect("read vec");
    let mut c: Vec<chain::Entry> = Vec::new();
    for raw in text.split('\n') {
        if raw.is_empty() || raw.starts_with('#') { continue; }
        let p: Vec<&str> = raw.split('|').collect();
        if let Some(name) = raw.strip_prefix("case ") { c = Vec::new(); println!("case {name}"); }
        else if p[0] == "append" || p[0] == "seal" {
            let r = if p[0] == "append" { chain::append(&mut c, p[1], p[2], p[3], p[4], p[5]) } else { chain::seal(&mut c, p[1], p[2], p[3]) };
            match r { Ok(()) => println!("ok {}", c.last().unwrap().hash), Err(_) => println!("err") }
        } else if p[0] == "verify" { println!("verify {}", chain::verify(&c)); }
        else if p[0] == "tamper" { c[0].subject = "tampered".into(); println!("tampered"); }
    }
}
