from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection String
MONGO_URI = "mongodb://localhost:27017"  # Move this to a config

client = AsyncIOMotorClient(MONGO_URI)
db = client["cat_platforms"]
collection = db["supaclear"]


async def fetch_n_rows(collection, n=1, filter_query=None, sort=None):
    """Fetch a specified number of rows from a MongoDB collection using Motor.

    Args:
        collection (_type_): Motor collection object
        n (int, optional): Number of rows to fetch (default 1)
        filter_query (_type_, optional): Optional dictionary for filtering documents
        sort (_type_, optional): Optional list of tuples for sorting (e.g., [('timestamp', -1)])

    Returns:
        _type_: List of documents
    """
    try:
        query = filter_query or {}
        sorting = sort or [('_id', 1)]
        cursor = collection.find(query).sort(sorting).limit(n)
        documents = await cursor.to_list(length=n)
        return documents
    
    except Exception as e:
        raise Exception("Error fetching documents")