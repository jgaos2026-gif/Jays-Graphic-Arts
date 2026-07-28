"""
tests/unit/test_word.py — Braid Algebra Engine Unit Tests

Covers every public surface of braid_simulator.word:
  • Generator arithmetic (negation, cancellation)
  • BraidWord construction, validation, and concatenation
  • sigma() / sigma_inv() constructors
  • reduce_to_normal_form() — far commutativity, braid relation, free cancellation
  • is_equivalent() and check_topological_equivalence()
"""
from __future__ import annotations

import pytest

from braid_simulator import (
    BraidWord,
    Generator,
    NormalForm,
    TopologicalMismatchFault,
    check_topological_equivalence,
    is_equivalent,
    reduce_to_normal_form,
    sigma,
    sigma_inv,
)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class TestGenerator:
    def test_negation_flips_inverse_flag(self) -> None:
        g = Generator(1, False)
        assert (-g) == Generator(1, True)
        assert (-(-g)) == g

    def test_cancels_detects_inverse_pair(self) -> None:
        g = Generator(2, False)
        g_inv = Generator(2, True)
        assert g.cancels(g_inv)
        assert g_inv.cancels(g)

    def test_does_not_cancel_same_sign(self) -> None:
        g = Generator(1, False)
        assert not g.cancels(Generator(1, False))

    def test_does_not_cancel_different_index(self) -> None:
        assert not Generator(1, False).cancels(Generator(2, True))

    def test_repr_positive(self) -> None:
        assert "σ_1" in repr(Generator(1, False))
        assert "⁻¹" not in repr(Generator(1, False))

    def test_repr_inverse(self) -> None:
        assert "⁻¹" in repr(Generator(1, True))


# ---------------------------------------------------------------------------
# BraidWord construction
# ---------------------------------------------------------------------------

class TestBraidWord:
    def test_construction_valid(self) -> None:
        w = BraidWord(3, [Generator(1), Generator(2)])
        assert w.n == 3
        assert len(w.generators) == 2

    def test_construction_requires_n_at_least_2(self) -> None:
        with pytest.raises(ValueError):
            BraidWord(1, [])

    def test_generator_index_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            BraidWord(3, [Generator(3)])  # valid for B_3 are 1, 2 only

    def test_empty_word_is_identity(self) -> None:
        w = BraidWord(4, [])
        assert w.generators == ()

    def test_concatenation(self) -> None:
        w1 = sigma(1, 3)
        w2 = sigma(2, 3)
        w = w1 * w2
        assert w.generators == (Generator(1), Generator(2))

    def test_concatenation_different_groups_raises(self) -> None:
        with pytest.raises(ValueError):
            sigma(1, 3) * sigma(1, 4)

    def test_equality_same_word(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(1, 3) * sigma(2, 3)
        assert w1 == w2

    def test_inequality_different_words(self) -> None:
        assert sigma(1, 3) != sigma(2, 3)

    def test_hash_consistent(self) -> None:
        w = sigma(1, 3)
        assert hash(w) == hash(w)

    def test_repr_empty(self) -> None:
        w = BraidWord(3, [])
        assert "ε" in repr(w)

    def test_repr_nonempty(self) -> None:
        w = sigma(1, 3)
        assert "σ_1" in repr(w)


# ---------------------------------------------------------------------------
# Constructors: sigma / sigma_inv
# ---------------------------------------------------------------------------

class TestConstructors:
    def test_sigma_creates_positive_generator(self) -> None:
        w = sigma(1, 3)
        assert w.generators == (Generator(1, False),)

    def test_sigma_inv_creates_negative_generator(self) -> None:
        w = sigma_inv(2, 4)
        assert w.generators == (Generator(2, True),)

    def test_sigma_index_zero_raises(self) -> None:
        with pytest.raises(ValueError):
            sigma(0, 3)

    def test_sigma_index_equals_n_raises(self) -> None:
        with pytest.raises(ValueError):
            sigma(3, 3)  # valid for B_3 are 1, 2

    def test_sigma_inv_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            sigma_inv(5, 3)


# ---------------------------------------------------------------------------
# reduce_to_normal_form
# ---------------------------------------------------------------------------

class TestReduceToNormalForm:
    def test_empty_word_normal_form(self) -> None:
        w = BraidWord(3, [])
        nf = reduce_to_normal_form(w)
        assert isinstance(nf, NormalForm)
        assert nf.n == 3
        assert nf.canonical == ()

    def test_free_cancellation_sigma_sigma_inv(self) -> None:
        # σ_1 σ_1^{-1} = ε
        w = sigma(1, 3) * sigma_inv(1, 3)
        nf = reduce_to_normal_form(w)
        assert nf.canonical == (), f"σ_1 σ_1^{{-1}} should reduce to ε, got {nf.canonical}"

    def test_free_cancellation_sigma_inv_sigma(self) -> None:
        # σ_1^{-1} σ_1 = ε
        w = sigma_inv(1, 3) * sigma(1, 3)
        nf = reduce_to_normal_form(w)
        assert nf.canonical == ()

    def test_far_commutativity_b4(self) -> None:
        # σ_1 σ_3 = σ_3 σ_1 in B_4
        w1 = sigma(1, 4) * sigma(3, 4)
        w2 = sigma(3, 4) * sigma(1, 4)
        assert reduce_to_normal_form(w1) == reduce_to_normal_form(w2)

    def test_far_commutativity_b5(self) -> None:
        # σ_1 σ_4 = σ_4 σ_1 in B_5 (|1-4| = 3 ≥ 2)
        w1 = sigma(1, 5) * sigma(4, 5)
        w2 = sigma(4, 5) * sigma(1, 5)
        assert reduce_to_normal_form(w1) == reduce_to_normal_form(w2)

    def test_braid_relation_b3(self) -> None:
        # σ_1 σ_2 σ_1 = σ_2 σ_1 σ_2 in B_3 (Garside Δ_3)
        w1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        w2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)
        assert reduce_to_normal_form(w1) == reduce_to_normal_form(w2)

    def test_adjacent_non_commutativity_b3(self) -> None:
        # σ_1 σ_2 ≠ σ_2 σ_1 in B_3
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(2, 3) * sigma(1, 3)
        assert reduce_to_normal_form(w1) != reduce_to_normal_form(w2)

    def test_double_cancellation(self) -> None:
        # σ_1 σ_2 σ_2^{-1} σ_1^{-1} = ε
        w = sigma(1, 3) * sigma(2, 3) * sigma_inv(2, 3) * sigma_inv(1, 3)
        nf = reduce_to_normal_form(w)
        assert nf.canonical == ()

    def test_single_generator_is_its_own_normal_form(self) -> None:
        w = sigma(2, 4)
        nf = reduce_to_normal_form(w)
        assert nf.canonical == (Generator(2, False),)

    def test_identity_in_different_groups_not_equal(self) -> None:
        nf3 = reduce_to_normal_form(BraidWord(3, []))
        nf4 = reduce_to_normal_form(BraidWord(4, []))
        assert nf3 != nf4  # different n

    def test_normal_form_has_correct_n(self) -> None:
        w = sigma(1, 5) * sigma(2, 5)
        nf = reduce_to_normal_form(w)
        assert nf.n == 5

    def test_repr_empty_normal_form(self) -> None:
        w = BraidWord(3, [])
        nf = reduce_to_normal_form(w)
        assert "ε" in repr(nf)

    def test_repr_nonempty_normal_form(self) -> None:
        w = sigma(1, 3)
        nf = reduce_to_normal_form(w)
        assert "σ_1" in repr(nf)


# ---------------------------------------------------------------------------
# is_equivalent
# ---------------------------------------------------------------------------

class TestIsEquivalent:
    def test_same_word_is_equivalent(self) -> None:
        w = sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(w, w)

    def test_far_commutative_words_are_equivalent(self) -> None:
        w1 = sigma(1, 4) * sigma(3, 4)
        w2 = sigma(3, 4) * sigma(1, 4)
        assert is_equivalent(w1, w2)

    def test_braid_relation_words_are_equivalent(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        w2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)
        assert is_equivalent(w1, w2)

    def test_non_equivalent_words(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(2, 3) * sigma(1, 3)
        assert not is_equivalent(w1, w2)

    def test_different_groups_not_equivalent(self) -> None:
        w1 = sigma(1, 3)
        w2 = sigma(1, 4)
        assert not is_equivalent(w1, w2)

    def test_word_and_identity_not_equivalent(self) -> None:
        w = sigma(1, 3)
        identity = BraidWord(3, [])
        assert not is_equivalent(w, identity)

    def test_cancellation_equivalent_to_identity(self) -> None:
        w = sigma(1, 3) * sigma_inv(1, 3)
        identity = BraidWord(3, [])
        assert is_equivalent(w, identity)


# ---------------------------------------------------------------------------
# check_topological_equivalence
# ---------------------------------------------------------------------------

class TestCheckTopologicalEquivalence:
    def test_equivalent_words_do_not_raise(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3) * sigma(1, 3)
        w2 = sigma(2, 3) * sigma(1, 3) * sigma(2, 3)
        check_topological_equivalence(w1, w2)  # no exception

    def test_non_equivalent_words_raise_fault(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(2, 3) * sigma(1, 3)
        with pytest.raises(TopologicalMismatchFault):
            check_topological_equivalence(w1, w2)

    def test_different_groups_raise_fault(self) -> None:
        w1 = sigma(1, 3)
        w2 = sigma(1, 4)
        with pytest.raises(TopologicalMismatchFault):
            check_topological_equivalence(w1, w2)

    def test_fault_message_contains_normal_forms(self) -> None:
        w1 = sigma(1, 3) * sigma(2, 3)
        w2 = sigma(2, 3) * sigma(1, 3)
        with pytest.raises(TopologicalMismatchFault) as exc_info:
            check_topological_equivalence(w1, w2)
        assert "NF" in str(exc_info.value) or "mismatch" in str(exc_info.value).lower()
