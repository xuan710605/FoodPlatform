-- Repeatable teardown for FoodPlatform MySQL objects.
-- The database itself is preserved; only project views, routines and tables are removed.
SET NAMES utf8mb4;
USE food_platform;

DROP VIEW IF EXISTS v_ai_filter_history;
DROP VIEW IF EXISTS v_product_audit_status;
DROP VIEW IF EXISTS v_user_order_summary;
DROP VIEW IF EXISTS v_product_average_rating;
DROP VIEW IF EXISTS v_product_inventory;
DROP VIEW IF EXISTS v_product_detail;

DROP PROCEDURE IF EXISTS sp_create_order;
DROP PROCEDURE IF EXISTS sp_deduct_inventory;
DROP PROCEDURE IF EXISTS sp_cancel_order_restore_inventory;
DROP PROCEDURE IF EXISTS sp_submit_product_audit;
DROP PROCEDURE IF EXISTS sp_record_audit_log;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS knowledge_audit;
DROP TABLE IF EXISTS workflow_task;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS ai_model_call_log;
DROP TABLE IF EXISTS ai_filter_history;
DROP TABLE IF EXISTS ai_conversation;
DROP TABLE IF EXISTS feedback_ticket;
DROP TABLE IF EXISTS anomaly_record;
DROP TABLE IF EXISTS product_audit;
DROP TABLE IF EXISTS product_review;
DROP TABLE IF EXISTS payment_record;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS order_info;
DROP TABLE IF EXISTS browsing_history;
DROP TABLE IF EXISTS favorite;
DROP TABLE IF EXISTS cart_item;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS product_nutrition;
DROP TABLE IF EXISTS product_ingredient_snapshot;
DROP TABLE IF EXISTS inventory_change_log;
DROP TABLE IF EXISTS product_inventory;
DROP TABLE IF EXISTS product_price;
DROP TABLE IF EXISTS product_image;
DROP TABLE IF EXISTS product_spec;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS merchant;
DROP TABLE IF EXISTS user_ingredient_preference;
DROP TABLE IF EXISTS user_address;
DROP TABLE IF EXISTS user_profile;
DROP TABLE IF EXISTS sys_role_permission;
DROP TABLE IF EXISTS sys_user_role;
DROP TABLE IF EXISTS sys_permission;
DROP TABLE IF EXISTS sys_role;
DROP TABLE IF EXISTS sys_user;
SET FOREIGN_KEY_CHECKS = 1;
