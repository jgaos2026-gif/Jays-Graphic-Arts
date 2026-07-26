# Limitations

**Author:** John E. Arenz — JGA Enterprises, Mendota, Illinois

---

## Current Limitations (v0.1.0-alpha)

### Not Validated
No empirical benchmark results exist for Hypotheses H1–H6. All claimed advantages are architectural hypotheses, not measured results.

### Not Formally Proved
The formal semantics of the execution model have not been written. The governing laws have not been formally proved as theorems of the model. Open Problems OP-1 and OP-2 are prerequisites for formal validation.

### Simulator Limitations
- Verification functions limited to HMAC and equality checks
- No distributed execution support
- No persistence backend (in-memory only)
- No Atomic Proof Core
- Braid-relation edge case (OP-9 / PO-1) not yet handled in tamper detector
- Fixed braid width (no dynamic strand creation during execution)

### Not Peer Reviewed
This research has not been submitted to or reviewed by peer-reviewed venues.

### Not Independently Reproduced
No external party has independently reproduced any result.

### Scope Limitations
BCT addresses computation where history preservation is mandatory. For general-purpose computation where history is not required, BCT adds overhead with no benefit. BCT is not proposed as a replacement for conventional architectures.
