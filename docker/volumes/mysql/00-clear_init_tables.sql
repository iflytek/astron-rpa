-- 清空初始化数据表的脚本
-- 此脚本在每次MySQL启动时执行，确保初始化数据表始终是最新的

USE rpa;

-- 清空 app_market_dict 表
DELETE FROM rpa.app_market_dict;

-- 清空 his_data_enum 表
DELETE FROM rpa.his_data_enum;

-- 清空 sample_templates 表
DELETE FROM rpa.sample_templates;

-- 清空 c_atom_meta 表（如果存在）
DELETE FROM rpa.c_atom_meta;

-- 清空 c_atom_meta_new 表（如果存在）
DELETE FROM rpa.c_atom_meta_new;

