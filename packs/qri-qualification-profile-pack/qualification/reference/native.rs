//! Native realization of the same domain: hex request per stdin line -> response per stdout line.
use std::io::BufRead;

fn unhex(s: &str) -> Vec<u8> {
    (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap_or(0)).collect()
}

fn main() {
    for line in std::io::stdin().lock().lines() {
        let line = line.unwrap_or_default();
        let out = qri_gl_adapter::domain::call(&unhex(line.trim()));
        println!("{}", String::from_utf8_lossy(&out));
    }
}
