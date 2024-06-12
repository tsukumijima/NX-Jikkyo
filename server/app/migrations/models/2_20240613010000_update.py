from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS before_comment_insert;

        ALTER TABLE `comments`
        DROP INDEX `idx_thread_id`,
        DROP INDEX `idx_id`,
        ADD INDEX `idx_thread_id_id` (`thread_id`, `id`);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `comments`
        DROP INDEX `idx_thread_id_id`,
        ADD INDEX `idx_thread_id` (`thread_id`),
        ADD INDEX `idx_id` (`id`);

        CREATE TRIGGER before_comment_insert
        BEFORE INSERT ON comments
        FOR EACH ROW
        BEGIN
            DECLARE max_no INT;
            -- 同じスレッド内の最大のコメ番を取得
            SELECT COALESCE(MAX(no), 0) INTO max_no
            FROM comments
            WHERE thread_id = NEW.thread_id;
            -- 新しいコメ番を設定
            SET NEW.no = max_no + 1;
        END;
    """
