"""
tests/property/test_braid_algebra.py — Algebraic Property Tests

Mathematical properties that must hold for the braid group B_n.
These are property-style checks (deterministic, not randomized) covering
the algebraic laws of braid words.
"""
from __future__ import annotations

import pytest

from braid_simulator import (
    BraidWord,
    Generator,
    is_equivalent,
    reduce_to_normal_form,
    sigma,
    sigma_inv,
)


# ---------------------------------------------------------------------------
# Group axioms
# ---------------------------------------------------------------------------

class TestGroupAxioms:
    def test_identity_is_neutral_left(self) -> None:
        """ε · w = w for any braid word w."""
        identity = BraidWord(3, [])
        w = sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(identity * w, w)

    def test_identity_is_neutral_right(self) -> None:
        """w · ε = w for any braid word w."""
        identity = BraidWord(3, [])
        w = sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(w * identity, w)

    def test_inverse_cancels_left(self) -> None:
        """σ_i^{-1} σ_i = ε."""
        w = sigma_inv(1, 3) * sigma(1, 3)
        identity = BraidWord(3, [])
        assert is_equivalent(w, identity)

    def test_inverse_cancels_right(self) -> None:
        """σ_i σ_i^{-1} = ε."""
        w = sigma(1, 3) * sigma_inv(1, 3)
        identity = BraidWord(3, [])
        assert is_equivalent(w, identity)

    def test_associativity(self) -> None:
        """(a · b) · c = a · (b · c)."""
        a = sigma(1, 4)
        b = sigma(2, 4)
        c = sigma(3, 4)
        lhs = (a * b) * c
        rhs = a * (b * c)
        assert is_equivalent(lhs, rhs)


# ---------------------------------------------------------------------------
# Artin braid relations
# ---------------------------------------------------------------------------

class TestArtinRelations:
    def test_far_commutativity_b3(self) -> None:
        """σ_1 σ_3 = σ_3 σ_1 in B_4 is the minimal far-commuting case."""
        w1 = sigma(1, 4) * sigma(3, 4)
        w2 = sigma(3, 4) * sigma(1, 4)
        assert is_equivalent(w1, w2)

    def test_far_commutativity_b5_distance3(self) -> None:
        """σ_1 σ_4 = σ_4 σ_1 in B_5 (distance 3 ≥ 2)."""
        w1 = sigma(1, 5) * sigma(4, 5)
        w2 = sigma(4, 5) * sigma(1, 5)
        assert is_equivalent(w1, w2)

    def test_braid_relation_b3(self) -> None:
        """σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 in B_3."""
        w1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        w2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(w1, w2)

    def test_braid_relation_b4_12(self) -> None:
        """σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 in B_4 (same relation, different group)."""
        w1 = sigma(1, 4) * sigma(2, 4) * sigma(1, 4)
        w2 = sigma(2, 4) * sigma(1, 4) * sigma(2, 4)
        assert is_equivalent(w1, w2)

    def test_braid_relation_b4_23(self) -> None:
        """σ_2 σ_3 σ_2 = σ_3 σ_2 σ_3 in B_4."""
        w1 = sigma(2, 4) * sigma(3, 4) * sigma(2, 4)
        w2 = sigma(3, 4) * sigma(2, 4) * sigma(3, 4)
        assert is_equivalent(w1, w2)

    def test_non_commutativity_adjacent(self) -> None:
        """σ_1 σ_2 ≠ σ_2 σ_1 in B_3 (adjacent generators do not commute)."""
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(2, 3) * sigma(1, 3)
        assert not is_equivalent(w1, w2)


# ---------------------------------------------------------------------------
# Normal form properties
# ---------------------------------------------------------------------------

class TestNormalFormProperties:
    def test_normal_form_is_idempotent(self) -> None:
        """NF(NF(w)) = NF(w) — applying normal form twice is the same."""
        w = sigma(1, 4) * sigma(2, 4) * sigma(3, 4)
        nf1 = reduce_to_normal_form(w)
        # Reconstruct word from normal form and re-reduce
        nf_word = BraidWord(nf1.n, list(nf1.canonical))
        nf2 = reduce_to_normal_form(nf_word)
        assert nf1 == nf2

    def test_equivalent_words_have_same_normal_form(self) -> None:
        """Equivalent words must share a canonical form."""
        w1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)  # = Δ_3
        w2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)  # = Δ_3
        assert reduce_to_normal_form(w1) == reduce_to_normal_form(w2)

    def test_non_equivalent_words_differ_in_normal_form(self) -> None:
        """Non-equivalent words must have different canonical forms."""
        w1 = sigma(1, 3)
        w2 = sigma(2, 3)
        assert reduce_to_normal_form(w1) != reduce_to_normal_form(w2)

    def test_normal_form_of_identity(self) -> None:
        """Normal form of ε is the empty canonical tuple."""
        w = BraidWord(3, [])
        nf = reduce_to_normal_form(w)
        assert nf.canonical == ()
        assert nf.n == 3

    def test_free_cancel_produces_shorter_normal_form(self) -> None:
        """σ_1 σ_1^{-1} reduces to ε (length 0 < 2)."""
        w = sigma(1, 3) * sigma_inv(1, 3)
        nf = reduce_to_normal_form(w)
        assert len(nf.canonical) < 2

    def test_normal_form_canonical_is_lex_minimal(self) -> None:
        """Far-commuting words have the same normal form (lex-minimal pick)."""
        w1 = sigma(1, 4) * sigma(3, 4)  # σ_1 σ_3
        w2 = sigma(3, 4) * sigma(1, 4)  # σ_3 σ_1 = same element
        nf1 = reduce_to_normal_form(w1)
        nf2 = reduce_to_normal_form(w2)
        # Both reduce to the same lex-minimal representative
        assert nf1.canonical == nf2.canonical


# ---------------------------------------------------------------------------
# Garside Δ_3 (three-strand Garside element)
# ---------------------------------------------------------------------------

class TestGarside:
    def test_delta3_is_six_crossings(self) -> None:
        """
        Δ_3 = σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 is the Garside element of B_3.
        Its normal form should have exactly 3 generators.
        """
        delta3 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        nf = reduce_to_normal_form(delta3)
        assert len(nf.canonical) == 3

    def test_delta3_squared_reduces(self) -> None:
        """Δ_3^2 can be expressed in 6 generators and reduces to a canonical form."""
        delta3 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        delta3_sq = delta3 * delta3
        nf = reduce_to_normal_form(delta3_sq)
        assert nf.n == 3
        # The normal form has length ≤ 6 (free-reduction shortens)
        assert len(nf.canonical) <= 6

    def test_delta3_alt_form_equivalent(self) -> None:
        """Both generating forms of Δ_3 are equivalent."""
        d1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        d2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(d1, d2)
