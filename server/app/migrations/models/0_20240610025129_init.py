from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `channels` (
            `id` INT NOT NULL PRIMARY KEY,
            `name` VARCHAR(255) NOT NULL,
            `description` LONGTEXT NOT NULL
        ) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `threads` (
            `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            `channel_id` INT NOT NULL,
            `start_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
            `end_at` DATETIME(6),
            `duration` INT NOT NULL,
            `title` VARCHAR(255) NOT NULL,
            `description` LONGTEXT NOT NULL,
            CONSTRAINT `fk_threads_channels_eb0decce` FOREIGN KEY (`channel_id`) REFERENCES `channels` (`id`) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `comments` (
            `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            `thread_id` INT NOT NULL,
            `no` INT NOT NULL,
            `vpos` INT NOT NULL,
            `date` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            `mail` VARCHAR(255) NOT NULL  DEFAULT '',
            `user_id` VARCHAR(255) NOT NULL,
            `premium` BOOL NOT NULL  DEFAULT 0,
            `anonymity` BOOL NOT NULL  DEFAULT 0,
            `content` LONGTEXT NOT NULL,
            CONSTRAINT `fk_comments_threads_eb0decce` FOREIGN KEY (`thread_id`) REFERENCES `threads` (`id`) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `aerich` (
            `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            `version` VARCHAR(255) NOT NULL,
            `app` VARCHAR(100) NOT NULL,
            `content` JSON NOT NULL
        ) CHARACTER SET utf8mb4;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "channels";
        DROP TABLE IF EXISTS "threads";
        DROP TABLE IF EXISTS "comments";
        DROP TABLE IF EXISTS "aerich";
    """
