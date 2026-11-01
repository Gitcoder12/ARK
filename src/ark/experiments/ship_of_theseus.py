from ark.identity.entity import AIEntity
from ark.identity.replacer import ComponentReplacer
from ark.identity.evaluator import IdentityEvaluator

def run_simulation():
    # 1. Create the original "You"
    original = AIEntity(
        name="Original You",
        memory_core=["Childhood home", "First love", "Favourite food", "Fear of failure"],
        logic_core={"rationality": 0.8, "empathy": 0.7},
        personality_vector=0.5
    )
    
    evaluator = IdentityEvaluator(baseline_entity=original)
    stimuli = ["Childhood home", "First love", "Favourite food"]
    
    print(f"--- Starting State ---")
    print(f"Drift from Original: {evaluator.measure_identity_drift(original, stimuli):.2f}")
    
    # 2. The Ship of Theseus (Replacing the brain bit by bit)
    replacer = ComponentReplacer(original)
    
    print(f"\n--- Swapping Neurons (Memories) ---")
    replacer.replace_memory("A memory of Mars")
    replacer.replace_memory("A memory of Neuralink")
    
    drift = evaluator.measure_identity_drift(replacer.entity, stimuli)
    print(f"Drift from Original: {drift:.2f} (The entity has forgotten its past)")
    print(f"Behavioral Test: {replacer.entity.respond_to_stimulus('Childhood home')}")
    
    # 3. The Final Swap (Is it still You?)
    print(f"\n--- Final Replaced State ---")
    print(f"Is this still the original 'You'? Check the drift score: {drift:.2f}")

if __name__ == "__main__":
    run_simulation()
