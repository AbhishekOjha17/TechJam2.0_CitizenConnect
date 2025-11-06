from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://dhiraj:dhiraj123@pippo.rjbrs.mongodb.net/?retryWrites=true&w=majority",
    tls=True,
    tlsAllowInvalidCertificates=True
)

try:
    client.admin.command('ping')
    print("✅ MongoDB connected successfully (insecure mode)")
except Exception as e:
    print("❌ Connection failed:", e)
