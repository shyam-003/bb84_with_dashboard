# bb84.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from helpers import *
from constants import *

def run_bb84_simulation(num_qubits, noise_level, has_eve):
    """
    Runs BB84 simulation serially (bit by bit)
    """
    
    # 1. Setup Data
    alice_bits = get_quantum_random_numbers(num_qubits)
    alice_bases = get_random_bases(num_qubits)
    bob_bases = get_random_bases(num_qubits)
    
    alice_sifted = []
    bob_sifted = []
    
    # 2. Setup Backend
    noise_model = get_noise_model(noise_level)
    backend = AerSimulator(noise_model=noise_model)
    
    # 3. Serial Transmission Loop
    for i in range(num_qubits):
        qc = QuantumCircuit(1, 1)
        
        # ------ ALICE PREPARES ------
        if alice_bases[i] == BASIS_Z:
            if alice_bits[i] == BIT_1:
                qc.x(0)
        else:
            if alice_bits[i] == BIT_0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        
        # ------ EVE ATTACKS ------
        if has_eve:
            eve_basis = BASIS_X if np.random.rand() > 0.5 else BASIS_Z
            
            if eve_basis == BASIS_X:
                qc.h(0)
            
            qc.measure(0, 0)

            if eve_basis == BASIS_X:
                qc.h(0)
        
        # ------ BOB MEASURES ------
        if bob_bases[i] == BASIS_X:
            qc.h(0)
        qc.measure(0, 0)
        
        # ------ EXECUTE ------
        job = backend.run(transpile(qc, backend), shots=1, memory=True)
        measured_bit = job.result().get_memory()[0]
        
        # ------ SIFTING ------
        if alice_bases[i] == bob_bases[i]:
            alice_sifted.append(alice_bits[i])
            bob_sifted.append(measured_bit)
            
    # 4. Calculate QBER
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