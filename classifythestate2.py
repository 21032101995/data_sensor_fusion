import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score

# 1. Carregar os dados
df = pd.read_csv('dataset.csv')

# Separar features (X) e target (y)
X = df.drop(columns=['State'])
y = df['State']

# 2. Normalizar as features (crucial para o bom funcionamento de redes neuronais)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. Dividir em conjuntos de treino e teste
# Nota: Como o dataset é muito pequeno (18 linhas), a divisão é apenas ilustrativa
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.5, random_state=42
)

# 4. Criar e treinar a Rede Neuronal (MLP)
# Arquitetura: 2 camadas ocultas com 16 e 8 neurónios respetivamente
mlp = MLPClassifier(
    hidden_layer_sizes=(16, 8),
    activation='relu',
    solver='adam',
    max_iter=1000,
    random_state=42
)

mlp.fit(X_train, y_train)

# 5. Avaliar o modelo
y_pred = mlp.predict(X_test)
print(f"Precisão (Accuracy): {accuracy_score(y_test, y_pred):.2f}\n")
print("Relatório de Classificação:")
print(classification_report(y_test, y_pred, zero_division=0))