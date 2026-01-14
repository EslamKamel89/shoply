from src.app.workers.celery_app import celery_app


@celery_app.task(
    name="import_product_csv_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
)
def import_products_csv_tasks(self, file_path: str):
    import asyncio
    from pathlib import Path

    from src.app.apps.products.services import import_products_from_csv

    asyncio.run(import_products_from_csv(Path(file_path)))
