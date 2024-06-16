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
