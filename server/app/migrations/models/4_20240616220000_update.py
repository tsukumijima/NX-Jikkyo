from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `comments` DROP FOREIGN KEY `fk_comments_threads_eb0decce`;
        ALTER TABLE `comments` MODIFY COLUMN `date` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `comments` MODIFY COLUMN `thread_id` INT NOT NULL;
        DROP TABLE IF EXISTS `comment_counters`;
        CREATE TABLE IF NOT EXISTS `comment_counters` (
            `thread_id` INT NOT NULL PRIMARY KEY,
            `max_no` INT NOT NULL DEFAULT 0
        ) CHARACTER SET utf8mb4;
        ALTER TABLE `threads` MODIFY COLUMN `start_at` DATETIME(6) NOT NULL;
        ALTER TABLE `threads` MODIFY COLUMN `end_at` DATETIME(6) NOT NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `threads` MODIFY COLUMN `start_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `threads` MODIFY COLUMN `end_at` DATETIME(6);
        ALTER TABLE `comments` MODIFY COLUMN `date` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `comments` MODIFY COLUMN `thread_id` INT NOT NULL;
        DROP TABLE IF EXISTS `comment_counters`;
        ALTER TABLE `comments` ADD CONSTRAINT `fk_comments_threads_eb0decce` FOREIGN KEY (`thread_id`) REFERENCES `threads` (`id`) ON DELETE CASCADE;
    """


MODELS_STATE = (
    "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"
    "pfJ9or0A=="
)
