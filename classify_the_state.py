import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# 1. Carregar o dataset
df = pd.read_csv('dataset.csv')

# Substituir 'estado' pelo nome real da coluna alvo no seu ficheiro
X = df.drop(columns=['State']).values
y = df['State'].values

# Codificar a variável alvo se for texto
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
num_classes = len(np.unique(y_encoded))

# 2. Dividir em treino e teste e normalizar
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Construir a rede neuronal
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')
])

loss_fn = 'sparse_categorical_crossentropy' if num_classes > 2 else 'binary_crossentropy'
model.compile(optimizer='adam', loss=loss_fn, metrics=['accuracy'])

# 4. Treinar o modelo
model.fit(X_train_scaled, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# 5. Avaliar o modelo
loss, accuracy = model.evaluate(X_test_scaled, y_test)
print(f"Precisão no teste: {accuracy:.4f}")