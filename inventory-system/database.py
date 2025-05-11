from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import Column, Integer, String, and_, delete, select, text, true
from typing import Optional
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

Base = declarative_base()

# Database configuration
DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/dissertation"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = async_sessionmaker(bind=engine)

app = FastAPI()


# Dependency to get a database session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# USER TABLE
class User (BaseModel):
    username: str
    health: int
    armour: int
    mana: int
    weight: int

class userRespond(User):
    userID:int

# USER INVENTORY TABLE
class UserInventory (BaseModel):
    userID: int
    itemID: int
    quantity: int

# ITEMS

# Parent Class - ItemID, ItemType
class ItemType(BaseModel):
    itemID: Optional[int] = None

# Weapon Item Type
class weaponCrate (ItemType):
    name: str
    damage: int
    ranged: bool
    weight: int
    note: str

# Armour Item Type
class armourCreate (ItemType):
    name: str
    armourValue: int
    weight: int
    note: str

# Quest Item Type
class questItemCreate (ItemType):
    name: str
    weight: int
    note: str

# Spell Item Type
class spellCreate (ItemType):
    name: str
    damage: int
    manaCost: int
    weight: int
    note: str

# Health Consumable Type
class healthConsumCreate (ItemType):
    name: str
    healthRestore: int
    weight: int
    note: str

# Mana Consumable Type
class manaConsumCreate (ItemType):
    name: str
    manaRegen: int
    weight: int
    note: str

# Choose between the Item Type tables
class ItemOption (str, Enum):
    WEP = "WEP"
    ARM = "ARM"
    QUE = "QUE"
    SPL = "SPL"
    HLT = "HLT"
    MAN = "MAN"

# Link the table options to the database options
ITEM_MODELS = {
    "WEP": weaponCrate,
    "ARM": armourCreate,
    "QUE": questItemCreate,
    "SPL": spellCreate,
    "HLT": healthConsumCreate,
    "MAN": manaConsumCreate
}

TABLE_MODELS = {
    "WEP": {"table": "Weapon"},
    "ARM": {"table": "Armour"},
    "QUE": {"table": "QuestItem"},
    "SPL": {"table": "Spell"},
    "HLT": {"table": "HConsumable"},
    "MAN": {"table": "MConsumable"}
}



# Create the item type table that links every item
class ItemTypePost(BaseModel):
    itemType: ItemOption



# MODELLING
# ITEMS
class Weapon(Base):
    __tablename__ = 'Weapon'

    itemID = Column(Integer, primary_key=true)
    name = Column(String(30), nullable=False)
    damage = Column(Integer, nullable=False)
    ranged = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

class Armour(Base):
    __tablename__ = 'Armour'

    itemID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    armourValue = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

class QuestItem(Base):
    __tablename__ = 'QuestItem'

    itemID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

class Spell(Base):
    __tablename__ = 'Spell'

    itemID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    damage = Column(Integer, nullable=False)
    manaCost = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

class HealthConsumable(Base):
    __tablename__ = 'HConsumable'

    itemID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    healthRestore = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

class ManaConsumable(Base):
    __tablename__ = 'MConsumable'

    itemID = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    manaRegen = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    note = Column(String(150), nullable=True)

CLASS_MODELS = {
        "WEP": Weapon,
        "ARM": Armour,
        "QUE": QuestItem,
        "SPL": Spell,
        "HLT": HealthConsumable,
        "MAN": ManaConsumable,
}

# USERS
class UserModel(Base):
    __tablename__ = 'User'

    userID = Column(Integer, primary_key=True)
    username = Column(String(20), nullable = False)
    health = Column(Integer, nullable=False)
    armour = Column(Integer, nullable=False)
    mana = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)

# INVENTORY
class UserInventoryModel(Base):
    __tablename__ = 'UserInventory'

    userID = Column(Integer, primary_key=True)
    itemID = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)

# FASTAPI USAGE
# ITEMS

# Create a new item
@app.post("/items/{itemType}")
async def itemCreate(
    item_type: str,  # This should match the keys in ITEM_MODELS
    db: AsyncSession = Depends(get_db),
    body: dict = Body(...)
):
    """Create a new item"""
    try:
        # First, add into the ItemType table
        await db.execute(
            text("INSERT INTO ItemType (itemType) VALUES (:itemType)"),
            {"itemType": item_type}
        )

        result = await db.execute(text("SELECT LAST_INSERT_ID()"))
        itemID = result.scalar_one()

        if itemID is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve last inserted ID.")

        # Get the corresponding model class based on item_type
        model_class = ITEM_MODELS.get(item_type)
        if not model_class:
            raise HTTPException(status_code=400, detail="Invalid item type.")

        # Create an instance of the model using the body data
        item_data = model_class(**body)  # This should now work as expected
        item_fields = item_data.dict()

        # Add the server-generated itemID to the fields
        item_fields["itemID"] = itemID

        # Define item_table based on item_type
        item_table = TABLE_MODELS[item_type]["table"]

        # Insert into the respective child table
        await db.execute(
            text(f"""
                INSERT INTO {item_table} ({', '.join(item_fields.keys())})
                VALUES ({', '.join(':' + k for k in item_fields.keys())})
            """),
            item_fields
        )

        # Commit the changes
        await db.commit()

        return {"itemID": itemID, "message": f"{item_table} item created."}

    # Error Handling
    except Exception as e:
        await db.rollback()
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Gather every item
@app.get("/items")
async def get_all_items(
    db: AsyncSession = Depends(get_db)
    ):
    """Get all items"""
    try:
        # Query all items from each table
        weapon_query = select(Weapon)
        armour_query = select(Armour)
        quest_item_query = select(QuestItem)
        spell_query = select(Spell)
        health_consumable_query = select(HealthConsumable)
        mana_consumable_query = select(ManaConsumable)

        # Execute all queries
        weapons = await db.execute(weapon_query)
        armours = await db.execute(armour_query)
        quest_items = await db.execute(quest_item_query)
        spells = await db.execute(spell_query)
        health_consumables = await db.execute(health_consumable_query)
        mana_consumables = await db.execute(mana_consumable_query)

        # Fetch all items as lists
        weapon_list = weapons.scalars().all()
        armour_list = armours.scalars().all()
        quest_item_list = quest_items.scalars().all()
        spell_list = spells.scalars().all()
        health_consumable_list = health_consumables.scalars().all()
        mana_consumable_list = mana_consumables.scalars().all()

        # Combine all lists into a single response
        all_items = {
            "weapons": weapon_list,
            "armours": armour_list,
            "quest_items": quest_item_list,
            "spells": spell_list,
            "health_consumables": health_consumable_list,
            "mana_consumables": mana_consumable_list
        }

        return all_items

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{itemType}/{itemID}")
async def get_one_item(
    item_type: str,
    item_id: int,
    db:AsyncSession = Depends(get_db)
):
    """Get a specific item's record."""
    # First filter to the right item type
    model_class = CLASS_MODELS.get(item_type)

    if not model_class:
        raise HTTPException(status_code=404, detail="Invalid item type.")

    # Then find the item within its dedicated table
    query = select(model_class).where(model_class.itemID == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    return item


@app.put("/items/{itemType}/{itemID}")
async def update_item(
    item_type: str,
    item_id: int,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db)
    ):
    """Update a specific item"""
    # Determine the model class based on item_type
    model_class = CLASS_MODELS.get(item_type)

    if not model_class:
        raise HTTPException(status_code=404, detail="Invalid item type.")

    # Query the database for the item with the specified itemID
    query = select(model_class).where(model_class.itemID == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()  # Get a single item or None

    # Error Handling - If there is no item with a specific ID
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found.")

    # Update fields based on the request body
    for field, value in body.items():
        if hasattr(item, field):
            setattr(item, field, value)

    # Commit the changes to the database
    await db.commit()

    return {"message": f"{item_type} item updated successfully", "itemID": item_id}

@app.delete("/items/{itemType}/{itemID}")
async def delete_item(
    item_type: str,
    item_id: int,
    db: AsyncSession = Depends(get_db)
    ):
    """Delete an item"""
    # Dynamically get the correct model class
    model_class = CLASS_MODELS.get(item_type)

    # Error Handling - If user inputs wrong item type.
    if not model_class:
        raise HTTPException(status_code=404, detail="Invalid item type.")

    # Check if the item exists first
    result = await db.execute(select(model_class).where(model_class.itemID == item_id))
    item = result.scalar_one_or_none()

    # Error Handling - If there is no item with a specific ID
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    # Proceed with deletion
    await db.execute(delete(model_class).where(model_class.itemID == item_id))
    await db.commit()

    return {"message": f"{item_type} item with ID {item_id} deleted successfully."}


# USERS
@app.post("/users/", response_model=userRespond)
async def insert_user(
    user: User,
    db: AsyncSession = Depends(get_db)
):
    """Add a new user"""
    try:
        await db.execute(
            text("""
                INSERT INTO User (username, health, armour, mana, weight)
                VALUES (:username, :health, :armour, :mana, :weight)
                """),
                {"username": user.username, "health": user.health, "armour":user.armour, "mana":user.mana, "weight": user.weight}
        )
        await db.commit()

        result  = await db.execute(text("SELECT LAST_INSERT_ID()"))
        new_id = result.scalar()

        return {"userID": new_id, **user.dict()}

    # Error Handling - Make sure database works
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Database error: {str(e)}")

@app.get("/users/", response_model=list[User])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """Return every user's data."""
    result = await db.execute(select(UserModel))
    user_list = result.scalars().all()
    return user_list


@app.get("/users/{userID}")
async def get_one_user(
    userID: int,
    db: AsyncSession = Depends(get_db)
):
    """Return a singule user's data."""
    result = await db.execute(select(UserModel).where(UserModel.userID == userID))
    user = result.scalar_one_or_none()

    # Error Handling
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "userID": user.userID,
        "username": user.username,
        "health": user.health,
        "armour": user.armour,
        "mana": user.mana,
        "weight": user.weight
    }

@app.put("/users/{userID}")
async def update_user (
    userID: int,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Update a specific user."""
    # Query the database for the item with the specified itemID
    query = select(UserModel).where(UserModel.userID == userID)
    result = await db.execute(query)
    user = result.scalar_one_or_none()  # Get a single item or None

    # Error Handling
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    # Update fields based on the request body
    for field, value in body.items():
        if hasattr(user, field):
            setattr(user, field, value)

    # Commit the changes to the database
    await db.commit()

    return {"message": f"User has been updated successfully", "User ID": userID}

@app.delete("/users/{userID}")
async def delete_user (
    userID: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific user"""
    result = await db.execute(select(UserModel).where(UserModel.userID == userID))
    user = result.scalar_one_or_none()

    # Error Handling - If there is no item with a specific ID
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Proceed with deletion
    await db.execute(delete(UserModel).where(UserModel.userID == userID))
    await db.commit()

    return {"message": f"User with ID {userID} deleted successfully."}


# USER INVENTORY

@app.get("/userinventory", response_model=list[UserInventory])
async def get_every_inventory_record(db: AsyncSession = Depends(get_db)):
    """Get every inventory record"""
    result = await db.execute(select(UserInventoryModel))
    inventory_list = result.scalars().all()
    return inventory_list

@app.get("/userinventory/{itemID}")
async def get_one_items_records(
    itemID: int,
    db: AsyncSession = Depends(get_db)
):
    """Get every user with a specific item"""
    result = await db.execute(select(UserInventoryModel).where(UserInventoryModel.itemID == itemID))
    userInventory = result.scalar_one_or_none()

    # Error Handling
    if not userInventory:
        raise HTTPException(status_code=404, detail="Item not found.")

    return {
        "userID": userInventory.userID,
        "itemID": userInventory.itemID,
        "quantity": userInventory.quantity,
    }

@app.get("/userinventory/{userID}")
async def get_one_users_inventory(
    userID: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user's inventory"""
    result = await db.execute(select(UserInventoryModel).where(UserInventoryModel.userID == userID))
    userInventory = result.scalar_one_or_none()

    # Error Handling
    if not userInventory:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "userID": userInventory.userID,
        "itemID": userInventory.itemID,
        "quantity": userInventory.quantity,
    }

@app.get("/userinventory/{userID}/{itemID}")
async def get_specific_inventory_record(
    userID: int,
    itemID: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific item from a specific user's inventory"""
    result = await db.execute(select(UserInventoryModel).where(
        and_(
            UserInventoryModel.userID == userID,
            UserInventoryModel.itemID == itemID
        )
    ))
    inventoryRecord = result.scalar_one_or_none()

    # Error Handling
    if not inventoryRecord:
        raise HTTPException(status_code=404, detail="Inventory Record not found.")

    return {
        "userID": inventoryRecord.userID,
        "itemID": inventoryRecord.itemID,
        "quantity": inventoryRecord.quantity
    }


@app.put("/userinventory/{userID}/{itemID}")
async def update_inventory(
    userID: int,
    itemID: int,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    query = select(UserInventoryModel).where(
        and_(UserInventoryModel.userID == userID,
             UserInventoryModel.itemID == itemID
             )
    )
    result = await db.execute(query)
    userInventory = result.scalar_one_or_none()  # Get a single item or None

    # Error Handling
    if userInventory is None:
        try:
            # Record isn't auto created, first tries to create if possible
            await db.execute(
                text("INSERT INTO UserInventory (userID, itemID) VALUES (:userID, :itemID)"),
                {"userID": userID, "itemID": itemID}
            )
            await db.commit()
        except Exception as e:
            # If record creation is not possible due to either itemID or userID missing, raises error
            raise HTTPException(status_code=404, detail="Inventory record not found.")

    # Update fields based on the request body
    for field, value in body.items():
        if hasattr(userInventory, field):
            setattr(userInventory, field, value)

    # Commit the changes to the database
    await db.commit()

    return {"message": f"Inventory item has been updated successfully"}


# Allow it to run and see docs
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)