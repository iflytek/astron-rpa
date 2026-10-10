import sqlite3
from importlib import import_module

from astronverse.database import DatabaseType
from astronverse.database.core import IDatabaseCore

# try:
#     import ibm_db_dbi
# except Exception as e:
#     logger.error(f"加载ibm_db_dll出错：{str(e)}")


def _load_driver(module: str, package: str, database: str):
    try:
        return import_module(module)
    except ImportError as exc:
        raise RuntimeError(
            f"{database} 驱动 {module} 未安装或无法加载。"
            f"请在执行流程的客户端 Python 环境中安装或修复驱动：python -m pip install {package}。"
            "若已安装，请检查驱动所需的本机数据库客户端/ODBC 库及 Python 位数是否匹配。"
        ) from exc


class DatabaseCore(IDatabaseCore):
    @staticmethod
    def connect(db_info_dict: dict, db_type: DatabaseType = DatabaseType.MySQL):
        if db_type == DatabaseType.MySQL:
            import pymysql

            if db_info_dict.get("PORT", ""):
                db_info_dict["port"] = int(db_info_dict.get("PORT", 3306))
            db_conn = pymysql.connect(
                host=db_info_dict["host"],
                port=int(db_info_dict.get("port", 3306)),
                user=db_info_dict["user"],
                password=db_info_dict["password"],
                database=db_info_dict["database"],
                charset=db_info_dict.get("charset", "utf8").replace("-", ""),
            )
        elif db_type == DatabaseType.SQLServer:
            pyodbc = _load_driver("pyodbc", "pyodbc", "SQL Server")

            server = "{},{}".format(db_info_dict.get("host", ""), int(db_info_dict.get("port", 1433)))
            # 连接字符串
            conn_str = (
                r"DRIVER={SQL Server};"
                rf"SERVER={server};"
                rf"DATABASE={db_info_dict.get('database', '')};"
                rf"UID={db_info_dict.get('user', '')};"
                rf"PWD={db_info_dict.get('password', '')};"
            )
            # 连接数据库
            db_conn = pyodbc.connect(conn_str)
        elif db_type == DatabaseType.Oracle:
            cx_Oracle = _load_driver("cx_Oracle", "cx_Oracle", "Oracle")

            if db_info_dict.get("service_type", "") == "service":
                service = db_info_dict.get("service", "")
            else:
                service = db_info_dict.get("sid", "")
            db_conn = cx_Oracle.connect(
                user=db_info_dict.get("user", ""),
                password=db_info_dict.get("password", ""),
                dsn=f"{db_info_dict.get('host', '')}:{int(db_info_dict.get('port', 1521))}/{service}",
            )
        elif db_type == DatabaseType.PostgreSQL:
            psycopg2 = _load_driver("psycopg2", "psycopg2-binary", "PostgreSQL")

            db_conn = psycopg2.connect(
                database=db_info_dict.get("database", ""),
                user=db_info_dict.get("user", ""),
                password=db_info_dict.get("password", ""),
                host=db_info_dict.get("host", ""),
                port=int(db_info_dict.get("port", 5432)),
            )
        elif db_type == DatabaseType.SQLite:
            if db_info_dict.get("read_only") is True:
                from pathlib import Path

                db_conn = sqlite3.connect(Path(db_info_dict["sqlite_path"]).resolve().as_uri() + "?mode=ro", uri=True)
            else:
                db_conn = sqlite3.connect(f"{db_info_dict.get('sqlite_path', '')}")
        elif db_type == DatabaseType.Access:
            pyodbc = _load_driver("pyodbc", "pyodbc", "Access")

            conn_str = (
                r"DRIVER={Driver do Microsoft Access (*.mdb)};"
                rf"DBQ={db_info_dict.get('access_path', '')};"
                rf"PWD={db_info_dict.get('password', '')};"
            )
            db_conn = pyodbc.connect(conn_str)
        elif db_type == DatabaseType.DB2:
            raise NotImplementedError("DB2 connections are not implemented")
            # db_conn = ibm_db_dbi.connect(
            #     f"PORT={int(db_info_dict.get('port', 50000))};PROTOCOL=TCPIP;",
            #     database=db_info_dict.get("database", ""),
            #     user=db_info_dict.get("user", ""),
            #     password=db_info_dict.get("password", ""),
            #     host=db_info_dict.get("host", ""),
            # )
        else:
            raise Exception("找不到该数据库类型!")

        return db_conn

    @staticmethod
    def disconnect(db_conn: object):
        db_conn.close()

    @staticmethod
    def execute(db_conn: object, sql_str: str) -> bool:
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_str)
            db_conn.commit()
        except:
            db_conn.rollback()
            return False
        finally:
            cursor.close()
        return True

    @staticmethod
    def query(db_conn: object, sql_str: str) -> str:
        import datetime
        import json
        from decimal import Decimal

        cursor = db_conn.cursor()
        res_list = []

        try:
            cursor.execute(sql_str)
            key_info = cursor.description
            key_tup = [key[0] for key in key_info]

            result_arr = cursor.fetchall()

            for results in result_arr:
                new_result = []
                # 对查询结果的类型进行转换
                for result in results:
                    if isinstance(result, datetime.datetime):
                        new_result.append(result.strftime("%Y-%m-%d %H:%M:%S"))
                    elif isinstance(result, datetime.date):
                        new_result.append(result.strftime("%Y-%m-%d"))
                    elif isinstance(result, Decimal):
                        # 这个用字符串，用float会造成精度丢失
                        new_result.append(str(result))
                    else:
                        new_result.append(result)
                row_data = dict(zip(key_tup, new_result))

                res_list.append(row_data)
            try:
                res_list = json.dumps(res_list, ensure_ascii=False)
            except Exception as e:
                pass
            # 若是序列化报错，则返回原数据
            return res_list
        finally:
            cursor.close()
