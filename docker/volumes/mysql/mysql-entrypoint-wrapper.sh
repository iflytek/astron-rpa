#!/bin/bash
# MySQL Entrypoint 包装脚本
# 在MySQL启动后执行数据初始化（每次启动都会执行）

set -e

# 检查数据目录是否存在（判断是否为首次启动）
DATA_DIR="/var/lib/mysql"
IS_FIRST_START=false
if [ ! -d "$DATA_DIR/mysql" ]; then
  IS_FIRST_START=true
  echo "First start detected, MySQL entrypoint will handle initial setup..."
fi

# 处理容器停止信号，尽量优雅退出（把信号转发给 mysqld）
MYSQL_PID=""
term_handler() {
  echo "Signal received, stopping MySQL..."
  if [ -n "${MYSQL_PID}" ] && kill -0 "${MYSQL_PID}" 2>/dev/null; then
    kill -TERM "${MYSQL_PID}" 2>/dev/null || true
    wait "${MYSQL_PID}" 2>/dev/null || true
  fi
  exit 0
}
trap term_handler TERM INT

# 执行原始的MySQL entrypoint（在后台）
docker-entrypoint.sh "$@" &
MYSQL_PID=$!

# 等待MySQL完全启动
echo "Waiting for MySQL to be ready..."
RETRY_COUNT=0
MAX_RETRIES=60
until mysqladmin ping -h localhost --silent 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "MySQL failed to start after $MAX_RETRIES retries"
    exit 1
  fi
  echo "MySQL is not ready yet, waiting... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done

echo "MySQL is ready!"

# 获取MySQL root密码
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-${MYSQL_PASSWORD}}"

# 首次启动：让官方 initdb.d 机制完成（包含 01/02/03/04/05/06），避免我们在表尚未创建时清空导致失败
if [ "$IS_FIRST_START" = true ]; then
  echo "First start: skip refresh. Init scripts under /docker-entrypoint-initdb.d will run automatically."
  wait $MYSQL_PID
  exit 0
fi

# 非首次启动：每次启动都执行数据刷新（清空并重新插入）
echo "Starting data refresh (clearing and re-inserting initialization data)..."

# 执行清空表的SQL
echo "Clearing initialization tables..."
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /opt/rpa-init/00-clear_init_tables.sql 2>/dev/null || {
  echo "Warning: Failed to clear initialization tables, continuing..."
}

# 执行初始化数据插入（按顺序）
echo "Inserting initialization data..."
if ! mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/02-init_data.sql 2>&1; then
  echo "ERROR: Failed to execute 02-init_data.sql"
fi
if ! mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/03-init_data.sql 2>&1; then
  echo "ERROR: Failed to execute 03-init_data.sql"
fi
if ! mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/04-init_data.sql 2>&1; then
  echo "ERROR: Failed to execute 04-init_data.sql"
fi
if ! mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/05-init_data.sql 2>&1; then
  echo "ERROR: Failed to execute 05-init_data.sql"
fi
if ! mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" < /docker-entrypoint-initdb.d/06-init_data.sql 2>&1; then
  echo "ERROR: Failed to execute 06-init_data.sql (c_atom_meta_new)"
fi

echo "Data initialization completed!"

# 等待MySQL进程（保持容器运行）
wait $MYSQL_PID

