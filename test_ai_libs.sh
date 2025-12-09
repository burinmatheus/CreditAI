#!/bin/bash

echo "======================================"
echo "Testando Bibliotecas de IA do CreditAI"
echo "======================================"

echo ""
echo "1. Instalando scikit-fuzzy..."
pip install scikit-fuzzy --quiet

echo ""
echo "2. Instalando scikit-learn..."
pip install scikit-learn --quiet

echo ""
echo "3. Instalando PyTorch..."
pip install torch torchvision --quiet

echo ""
echo "======================================"
echo "Testando imports..."
echo "======================================"

python3 << 'PYCODE'
import sys

print("\n✅ Testando scikit-fuzzy...")
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    import numpy as np
    
    # Criar variável fuzzy simples
    test_var = ctrl.Antecedent(np.arange(0, 11, 1), 'test')
    test_var['low'] = fuzz.trimf(test_var.universe, [0, 0, 5])
    print(f"   ✓ scikit-fuzzy funcionando! Versão: {fuzz.__version__ if hasattr(fuzz, '__version__') else 'OK'}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n✅ Testando PyTorch...")
try:
    import torch
    import torch.nn as nn
    
    # Criar tensor simples
    x = torch.tensor([1.0, 2.0, 3.0])
    print(f"   ✓ PyTorch funcionando! Versão: {torch.__version__}")
    print(f"   ✓ CUDA disponível: {torch.cuda.is_available()}")
    print(f"   ✓ Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n✅ Testando scikit-learn...")
try:
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    
    # Normalizar dados simples
    scaler = StandardScaler()
    data = np.array([[1, 2], [3, 4]])
    scaler.fit(data)
    print(f"   ✓ scikit-learn funcionando!")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n✅ Testando NumPy...")
try:
    import numpy as np
    arr = np.array([1, 2, 3])
    print(f"   ✓ NumPy funcionando! Versão: {np.__version__}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("🎉 Todas as bibliotecas estão funcionando!")
print("="*50)
PYCODE
