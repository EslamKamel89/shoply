import asyncio
import csv
from decimal import Decimal
from pathlib import Path

from src.app.apps.products.repository import ProductRepository


async def demo_background_service(message: str) -> None:
    await asyncio.sleep(5)
    print(f"[SERVICE] {message}")


async def import_products_from_csv(file_path: Path) -> None:
    from src.app.db.session import Database
    from src.app.settings import settings

    db = Database(settings.ASYNC_DATABASE_URL)
    try:
        async for session in db.get_session():
            repo = ProductRepository(session)
            async with session.begin():
                with open(file_path, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row["name"].strip()
                        price = Decimal(row["price"])
                        await repo.create(name=name, price=price)
    finally:
        await db.dispose()
