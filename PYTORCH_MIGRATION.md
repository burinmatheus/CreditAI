# 🔄 Migração TensorFlow → PyTorch

## Resumo

O CreditAI foi migrado de **TensorFlow/Keras** para **PyTorch** na implementação da Rede Neural (Etapa 4).

---

## 🎯 Motivação

PyTorch é preferido em pesquisa acadêmica por:
- **Interface Pythonic**: Mais natural para desenvolvedores Python
- **Dynamic Computation Graphs**: Facilita debugging e experimentação
- **Maior adoção em pesquisa**: NeurIPS, ICML, ICLR
- **Flexibilidade**: Controle total do loop de treinamento
- **Debugging**: Mensagens de erro mais claras

---

## 📝 Mudanças Realizadas

### 1. Dependências (`requirements.txt`)

**Antes:**
```
tensorflow==2.15.0
```

**Depois:**
```
torch==2.1.2
torchvision==0.16.2
```

### 2. Arquitetura da Rede Neural

**TensorFlow/Keras:**
```python
model = keras.Sequential([
    layers.Input(shape=(10,)),
    layers.Dense(16, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(8, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(3, activation='softmax')
])
```

**PyTorch:**
```python
class CreditApprovalNN(nn.Module):
    def __init__(self, input_dim=10):
        super().__init__()
        self.hidden1 = nn.Linear(input_dim, 16)
        self.dropout1 = nn.Dropout(0.3)
        self.hidden2 = nn.Linear(16, 8)
        self.dropout2 = nn.Dropout(0.2)
        self.output = nn.Linear(8, 3)
        
    def forward(self, x):
        x = self.relu(self.hidden1(x))
        x = self.dropout1(x)
        x = self.relu(self.hidden2(x))
        x = self.dropout2(x)
        return self.output(x)
```

### 3. Treinamento

**TensorFlow:**
```python
model.compile(optimizer='adam', loss='categorical_crossentropy')
model.fit(X_train, y_train, epochs=50, batch_size=32)
```

**PyTorch:**
```python
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(epochs):
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
```

### 4. Predição

**TensorFlow:**
```python
probabilities = model.predict(X)
predictions = np.argmax(probabilities, axis=1)
```

**PyTorch:**
```python
model.eval()
with torch.no_grad():
    outputs = model(X_tensor)
    probabilities = softmax(outputs)
    predictions = torch.argmax(probabilities, dim=1)
```

### 5. Salvar/Carregar Modelo

**TensorFlow:**
```python
model.save('model.h5')
model = keras.models.load_model('model.h5')
```

**PyTorch:**
```python
torch.save(model.state_dict(), 'model.pt')
model.load_state_dict(torch.load('model.pt'))
```

---

## 📂 Arquivos Modificados

1. ✅ `requirements.txt` - Substituído tensorflow por torch/torchvision
2. ✅ `src/domain/services/approval_neural_network.py` - Reescrito com PyTorch
3. ✅ `AI_LIBRARIES.md` - Atualizada documentação para PyTorch
4. ✅ `test_ai_libs.sh` - Atualizado script de teste

---

## 🔧 Como Testar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Ou individualmente:
```bash
pip install torch torchvision scikit-fuzzy scikit-learn
```

### 2. Testar Bibliotecas

```bash
./test_ai_libs.sh
```

### 3. Testar Importação

```python
from src.domain.services.approval_neural_network import (
    CreditApprovalNN, 
    ApprovalNeuralNetwork
)

# Criar modelo
nn = ApprovalNeuralNetwork()
print("✅ PyTorch funcionando!")
```

### 4. Verificar Device

```python
import torch
print(f"Device: {torch.cuda.is_available() and 'cuda' or 'cpu'}")
```

---

## 🚀 Próximos Passos

1. **Rebuild Container**: 
   ```bash
   # No VS Code: "Dev Containers: Rebuild Container"
   ```

2. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Testar Serviço**:
   ```bash
   PYTHONPATH=/workspaces/CreditAI python3 src/main.py
   ```

4. **Testar Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/credit/analyze \
     -H "Content-Type: application/json" \
     -d @sample_request.json
   ```

---

## ⚠️ Notas Importantes

1. **Compatibilidade**: A arquitetura da rede neural permanece idêntica (MLP 10→16→8→3)
2. **Performance**: PyTorch pode ser ligeiramente mais rápido em CPU
3. **GPU**: PyTorch detecta CUDA automaticamente
4. **Modelos Antigos**: Modelos `.h5` (TensorFlow) NÃO são compatíveis com `.pt` (PyTorch)
5. **Retrainamento**: Será necessário retreinar o modelo na primeira execução

---

## 📚 Referências

- **PyTorch Docs**: https://pytorch.org/docs/
- **PyTorch Tutorials**: https://pytorch.org/tutorials/
- **Paper Original**: Paszke et al. "PyTorch: An Imperative Style, High-Performance Deep Learning Library" (NeurIPS 2019)

---

## ✅ Checklist de Validação

- [x] requirements.txt atualizado
- [x] approval_neural_network.py reescrito
- [x] AI_LIBRARIES.md atualizado
- [x] test_ai_libs.sh atualizado
- [ ] Container rebuilt
- [ ] Dependências instaladas
- [ ] Serviço testado
- [ ] Endpoint validado

---

**Migração completa! 🎉**
