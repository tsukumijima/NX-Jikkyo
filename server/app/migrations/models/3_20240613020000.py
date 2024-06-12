from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE comment_counters (
            thread_id INT PRIMARY KEY,
            max_no INT DEFAULT 0
        );
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS comment_counters;
    """
