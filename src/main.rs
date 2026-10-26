//! Local deterministic restaking loss-threshold policy only.
//! No validator telemetry, oracle, RPC, on-chain settlement, or security certification.
use std::env;
use std::process::ExitCode;

const MAX_BPS: u32 = 10_000;

#[derive(Debug, PartialEq, Eq)]
struct PolicyInput {
    exposure_bps: u32,
    slash_bps: u32,
    max_loss_bps: u32,
}

fn parse_bps(value: &str) -> Result<u32, String> {
    if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
        return Err("expected unsigned decimal basis points".to_string());
    }
    let parsed = value.parse::<u32>().map_err(|_| "basis points overflow".to_string())?;
    if parsed > MAX_BPS {
        return Err("basis points must be between 0 and 10000".to_string());
    }
    Ok(parsed)
}

fn parse_args<I: Iterator<Item = String>>(mut args: I) -> Result<PolicyInput, String> {
    let mut exposure_bps = None;
    let mut slash_bps = None;
    let mut max_loss_bps = None;
    while let Some(flag) = args.next() {
        let slot = match flag.as_str() {
            "--exposure-bps" => &mut exposure_bps,
            "--slash-bps" => &mut slash_bps,
            "--max-loss-bps" => &mut max_loss_bps,
            _ => return Err(format!("unknown flag: {flag}")),
        };
        if slot.is_some() {
            return Err(format!("duplicate flag: {flag}"));
        }
        let value = args.next().ok_or_else(|| format!("missing value for {flag}"))?;
        *slot = Some(parse_bps(&value)?);
    }
    Ok(PolicyInput {
        exposure_bps: exposure_bps.ok_or("missing --exposure-bps")?,
        slash_bps: slash_bps.ok_or("missing --slash-bps")?,
        max_loss_bps: max_loss_bps.ok_or("missing --max-loss-bps")?,
    })
}

/// Conservative integer ceiling: exposure * slash / 10,000, in bps of principal.
fn loss_bps(exposure_bps: u32, slash_bps: u32) -> u32 {
    ((u64::from(exposure_bps) * u64::from(slash_bps) + 9_999) / 10_000) as u32
}

fn main() -> ExitCode {
    let input = match parse_args(env::args().skip(1)) {
        Ok(input) => input,
        Err(error) => {
            eprintln!("INPUT_REJECTED: {error}");
            return ExitCode::from(2);
        }
    };
    let loss = loss_bps(input.exposure_bps, input.slash_bps);
    let decision = if loss <= input.max_loss_bps { "ALLOW" } else { "BLOCK" };
    println!("MODEL_SCOPE=LOCAL_DETERMINISTIC_POLICY_ONLY");
    println!("LOSS_BPS={loss}");
    println!("POLICY_DECISION={decision}");
    println!("IMPLEMENTATION_STATUS=PARTIAL_LOCAL_POLICY");
    println!("SECURITY_APPROVED=NO");
    println!("DEPLOYMENT_READY=NO");
    println!("NETWORK_STATUS=NOT_CONNECTED");
    ExitCode::SUCCESS
}

#[cfg(test)]
mod tests {
    use super::*;
    fn parse(values: &[&str]) -> Result<PolicyInput, String> {
        parse_args(values.iter().map(|value| (*value).to_string()))
    }
    #[test]
    fn conservative_rounding() {
        assert_eq!(loss_bps(7_500, 1_000), 750);
        assert_eq!(loss_bps(1, 1), 1);
        assert_eq!(loss_bps(0, 10_000), 0);
        assert_eq!(loss_bps(10_000, 10_000), 10_000);
    }
    #[test]
    fn complete_policy_parses() {
        assert_eq!(parse(&["--exposure-bps", "7500", "--slash-bps", "1000",
            "--max-loss-bps", "800"]).unwrap(),
            PolicyInput { exposure_bps: 7_500, slash_bps: 1_000, max_loss_bps: 800 });
    }
    #[test]
    fn invalid_values_rejected() {
        for invalid in ["-1", "10001", "1.0", "abc", "", "4294967296", "1;echo"] {
            assert!(parse_bps(invalid).is_err(), "{invalid}");
        }
    }
    #[test]
    fn missing_unknown_and_duplicate_flags_rejected() {
        assert!(parse(&[]).is_err());
        assert!(parse(&["--unknown", "1"]).is_err());
        assert!(parse(&["--exposure-bps", "1", "--exposure-bps", "2"]).is_err());
        assert!(parse(&["--exposure-bps"]).is_err());
    }
}
