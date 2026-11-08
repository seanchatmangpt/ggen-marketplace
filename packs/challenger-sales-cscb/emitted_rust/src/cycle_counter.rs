// cycle_counter.rs.tmpl — CSCB runner cycle counter (RFC-2026-0042 §4.1)
// Binding contract: see templates/rust/BINDING_CONTRACT.md
//
// Architecture-cfg-gated cycle reads, safe wrappers returning u64 cycles.
//   x86_64: RDTSC/RDTSCP via core::arch::x86_64
//   aarch64: CNTVCT_EL0 via inline asm
//   other targets: compile error (fail-closed, never a silent fake counter)
//
//! SAFETY note: `_rdtscp` serializes the read (ordered with respect to prior
//! instructions), making it the correct fence for measurement windows.

//! Cycle counter: cfg-gated per target arch, safe wrappers returning u64.

#![allow(unused)]

/// Read the arch cycle counter. Serializing on x86_64 (RDTSCP).
#[inline]
pub fn read_cycles() -> u64 {
    #[cfg(target_arch = "x86_64")]
    {
        unsafe { core::arch::x86_64::_rdtscp() }.0
    }

    #[cfg(target_arch = "aarch64")]
    {
        let v: u64;
        unsafe {
            core::arch::asm!(
                "mrs {v}, CNTVCT_EL0",
                v = out(reg) v,
                options(nomem, nostack, preserves_flags),
            );
        }
        v
    }

    #[cfg(not(any(target_arch = "x86_64", target_arch = "aarch64")))]
    {
        // Fail-closed: no silent fake counter on unsupported arches.
        compile_error!("cscb-runner cycle counter unsupported on this target arch");
        0
    }
}

/// Serializing read suitable for bracketing a measurement window:
/// read_before(); work(); read_after(); cycles = after - before.
#[inline]
pub fn read_cycles_serializing() -> u64 {
    #[cfg(target_arch = "x86_64")]
    {
        unsafe { core::arch::x86_64::_rdtscp() }.0
    }
    #[cfg(target_arch = "aarch64")]
    {
        read_cycles()
    }
    #[cfg(not(any(target_arch = "x86_64", target_arch = "aarch64")))]
    {
        read_cycles()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counter_is_monotonic_within_window() {
        let a = read_cycles_serializing();
        let b = read_cycles_serializing();
        assert!(b >= a, "cycle counter regressed: {a} -> {b}");
    }
}
