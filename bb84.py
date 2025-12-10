# bb84.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from helpers import *
from constants import *

def run_bb84_simulation(num_qubits, noise_level, has_eve):
    """
    Runs a full BB84 simulation cycle.
    
    Args:
        num_qubits (int): Length of the key (e.g., 50 bits)
        noise_level (float): 0.0 to 0.5 (noise probability)
        has_eve (bool): True if Eve is intercepting
        
    Returns:
        dict: Contains QBER, Alice's Key, Bob's Key, and Status
    """
    
    # 1. Alice generates bits and bases (True Quantum Randomness)
    alice_bits = get_quantum_random_numbers(num_qubits)
    alice_bases = get_random_bases(num_qubits)
    
    # 2. Create the Quantum Circuit
    circuit = QuantumCircuit(num_qubits, num_qubits)
    
    # 3. Alice prepares her states
    prepare_alice_states(circuit, alice_bits, alice_bases)
    
    # 4. Transmission (Channel)
    if has_eve:
        simulate_eve(circuit, num_qubits)
        
    # 5. Bob generates bases and measures
    bob_bases = get_random_bases(num_qubits)
    measure_bob(circuit, bob_bases)
    
    # 6. Execute Simulation (with Noise)
    noise_model = get_noise_model(noise_level)
    backend = AerSimulator(noise_model=noise_model)
    job = backend.run(transpile(circuit, backend), shots=1)
    result = job.result().get_counts()
    
    
    raw_bob_key_string = list(result.keys())[0]
    bob_bits = [bit for bit in raw_bob_key_string]
    bob_bits.reverse()
    
    # 7. Sifting (The Classic BB84 Step)
    alice_sifted = []
    bob_sifted = []
    
    for i in range(num_qubits):
        if alice_bases[i] == bob_bases[i]:
            alice_sifted.append(alice_bits[i])
            bob_sifted.append(bob_bits[i])
            
    # 8. Calculate QBER (Quantum Bit Error Rate)
    if len(alice_sifted) == 0:
        qber = 0
    else:
        errors = sum(1 for a, b in zip(alice_sifted, bob_sifted) if a != b)
        qber = errors / len(alice_sifted)

    return {
        "alice_key": "".join(alice_sifted),
        "bob_key": "".join(bob_sifted),
        "qber": qber,
        "total_bits": num_qubits,
        "sifted_size": len(alice_sifted)
    }

# Quick test if you run this file directly
if __name__ == "__main__":
    print("Running Standard Test...")
    res = run_bb84_simulation(num_qubits=20, noise_level=0.0, has_eve=False)
    print(f"Clean QBER: {res['qber']}")
    
    print("Running Eve Test...")
    res_eve = run_bb84_simulation(num_qubits=20, noise_level=0.0, has_eve=True)
    print(f"Eve QBER: {res_eve['qber']} (Should be ~25%)")