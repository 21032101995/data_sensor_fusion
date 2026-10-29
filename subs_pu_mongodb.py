import pymongo

myclient = pymongo.MongoClient(
    "mongodb://192.168.68.113:27017/",
    serverSelectionTimeoutMS=5000
)

# Testar a ligação ao servidor
print(myclient.admin.command("ping"))

# Selecionar a base de dados
mydb = myclient["data_sensors"]

# Selecionar a coleção
mycol = mydb["customers"]

# Inserir um documento para criar a base de dados e a coleção
document = {
    "sensor_id": "sensor_01",
    "temperature": 24.5,
    "humidity": 60
}

result = mycol.insert_one(document)

print("Documento inserido com o ID:", result.inserted_id)
print("Base de dados:", mydb.name)
print("Coleção:", mycol.name)