
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from helpers import get_noise_model

def run_e91_simulation(num_trials, noise_level, has_eve):
    """
    Runs E91 simulation serially
    """
    
    noise_model = get_noise_model(noise_level)
    backend = AerSimulator(noise_model=noise_model)
    
    # --- CORRECTED ANGLES FOR S = 2.82 ---
    # Alice: 0 (Z-basis), pi/2 (X-basis)
    # Bob:   pi/4 (Diagonal), 3*pi/4 (Orthogonal Diagonal)
    # maximizing the formula:
    # S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    
    combinations = [
        (0, np.pi/4),
        (0, 3*np.pi/4),
        (np.pi/2, np.pi/4),
        (np.pi/2, 3*np.pi/4)
    ]
    
    correlations = []
    
    for theta_a, theta_b in combinations:
        N_same = 0
        N_diff = 0
        
        for _ in range(num_trials):
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            
            if has_eve:
                qc.measure([0,1], [0,1])
            
            qc.ry(theta_a, 0)
            qc.ry(theta_b, 1)
            
            qc.measure([0, 1], [0, 1])
            
            job = backend.run(transpile(qc, backend), shots=1, memory=True)
            result = job.result().get_memory()[0]
            
            if result[0] == result[1]:
                N_same += 1
            else:
                N_diff += 1
                
        # Calculate Correlation E
        # E = (Same - Diff) / Total
        total = N_same + N_diff
        E = (N_same - N_diff) / total if total > 0 else 0
        correlations.append(E)

    # --- STANDARD CHSH FORMULA ---
    S = correlations[0] - correlations[1] + correlations[2] + correlations[3]
    
    return {
        "s_value": abs(S),
        "is_secure": abs(S) > 2.0,
        "correlations": correlations,
        "total_pairs": num_trials * 4
    }