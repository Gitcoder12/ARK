"""Small, deterministic demonstration of explicit identity-state drift."""

from ark.identity import AIEntity, ComponentReplacer, IdentityEvaluator


def run_simulation() -> None:
    """Mutate a synthetic entity and measure its signature drift."""
    original = AIEntity(
        name="Original You",
        memory_core=[
            "Childhood home",
            "First love",
            "Favourite food",
            "Fear of failure",
        ],
        logic_core={"rationality": 0.8, "empathy": 0.7},
        personality_vector=0.5,
    )
    baseline = original.behavioral_signature()
    evaluator = IdentityEvaluator(original)
    replacer = ComponentReplacer(original)

    print("--- Starting State ---")
    print(f"Drift from Original: {evaluator.identity_drift(baseline):.2f}")

    print("\n--- Replacing Memories ---")
    replacer.mutate_memory(
        add=["A memory of Mars", "A memory of Neuralink"],
        remove=["Childhood home", "First love"],
        step=1,
    )

    drift = evaluator.identity_drift(baseline)
    print(f"Drift from Original: {drift:.2f}")
    print(f"Behavioral Test: {original.respond_to_stimulus('Childhood home')}")
    original.record_signature(step=1)


if __name__ == "__main__":
    run_simulation()
