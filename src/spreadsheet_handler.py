from src import file_handler
import xml.etree.ElementTree as ET
import pandas as pd
import sqlite3
import json
import yaml
import os

common_xpaths = ["//*[contains(translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'item')]",
                 "//*[contains(translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'row')]",
                 "//*[contains(translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'record')]",
                 "//*[contains(translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'entry')]",
                 "//*[contains(translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'data')]",
                 "empty"]  # ik this looks random but what it does is basically
                         # to see if the word is included in any position and
                         # uppercase will be seen as lowercase, so it detects
                         # almost every possible variants of the word, from
                         # item to rowItem to itEm_DATA to wHaTeVeRtHeFuCkThIsItEmIs
                         # and if nothing was matched it gon use anything available

def handle_spreadsheets(files):
    file_handler.skip_command = True
    # first, theres no point to search the exact same file twice
    # say, if youre asking the models opinions on the documents, it makes sense to have both model running for rag
    # but i couldnt think of an instance of anyone wanting to ask for different answers based on a damn spreadsheet
    # second, i cant be FUCKING BOTHERED to fuck around with function calling anymore
    for file in files:
        path = "embeds/" + file
        name, ext = os.path.splitext(file)
        # 依照檔案類型使用最適合的方式統一轉換成dataframe
        # 如果檔案類型不支援 則將其轉換為血緣關係最親近的檔案類型再讀取
        if ext.lower() in [".xlsx", ".xlsm", ".xltx", ".xltm", ".xls", ".xlsb", ".odf", ".ods", ".odt"]:
            df = pd.read_excel(path, sheet_name=None, parse_dates=True)
        elif ext.lower() in [".xlt"]:  # xls範本
            df = pd.read_excel(file_handler.file_to_libreoffice(path, "xls"), sheet_name=None, parse_dates=True)
        elif ext.lower() in [".ots", ".fods"]:  # ods範本和扁平化版
            df = pd.read_excel(file_handler.file_to_libreoffice(path, "ods"), sheet_name=None, parse_dates=True)
        elif ext.lower() in [".csv"]:
            df = pd.read_csv(path, on_bad_lines="warn", parse_dates=True)
        elif ext.lower() in [".tsv"]:  # 跟csv一模一樣 只不過是換行從用逗號變成用Tab而已
            df = pd.read_csv(path, sep="	", on_bad_lines="warn", parse_dates=True)
        elif ext.lower() in [".xml"]:
            root = ET.parse(path).getroot()  # 拆解xml
            tags = set()  # 合集 跟list一樣 只是沒有排序 也不會有重複的物品
            for elem in root.iter(): tags.add(elem.tag)  # 如果你願意一層一層一層的剝開xml檔 把每個找到的不同標籤加進合集裡
            for xpath in common_xpaths:  # 嘗試每一個常見的XPath
                if xpath == "empty":
                    df = pd.read_xml(path, parse_dates=True)
                    break
                elif xpath in tags:
                    df = pd.read_xml(path, xpath=xpath, parse_dates=True)
                    break  # 中獎的話就用那個找資料
        elif ext.lower() in [".json"]:
            with open(path, "r", encoding="utf-8") as f: df = pd.json_normalize(json.load(f))  # 把巢狀json扁平化 接著做跟read_json一樣的事
        elif ext.lower() in [".yaml"]:  # pandas不支援這個東東 fair因為我這輩子沒看過這種檔案類型
            with open(path, "r", encoding="utf-8") as f: df = pd.DataFrame(yaml.safe_load(f))
        if len(df) == 0: return "error!"  # 如果dataframe是空的 放檔案這個人蠻厲害的
        datas = []
        if isinstance(df, dict):
            for sheet_title, sheet_df in df.items():
                if sheet_title: sheet_title = name + "_" + sheet_title + ext
                else: sheet_title = file  # fixes yaml
                data = []
                sheet_df.to_sql(sheet_title, sqlite3.connect("caches/database.db"), if_exists="replace")
                for col in sheet_df.columns:  # 在dataframe裡一行一行掃描 儲存那行的名稱 儲存的資料類型(str, datetime, etc.) 還有前面三行是什麼
                    data.append({"name": col, "datatype": str(sheet_df[col].dtype), "example": sheet_df[col].head(3).tolist()})
                datas.append({"table": sheet_title, "columns": data})
        else:
            data = []
            df.to_sql(file, sqlite3.connect("caches/database.db"), if_exists="replace")  # 建立一個db檔案來存放dataframe 如果檔案已經存在 取代原本檔案
            for col in df.columns:  # 在dataframe裡一行一行掃描 儲存那行的名稱 儲存的資料類型(str, datetime, etc.) 還有前面三行是什麼
                data.append({"name": col, "datatype": str(df[col].dtype), "example": df[col].head(3).tolist()})
            datas = [{"table": file, "columns": data}]

        with open("embeds/temp/" + file + "_schema.json", "w", encoding="utf8") as f:
            json.dump(datas, f, ensure_ascii=False)
    return f"""
You are an expert SQL analyst. Your goal is to help users query data from multiple files using standard SQL.

1. Analyze the provided `database_schema` to understand the available tables, columns, and data types.
2. When a user asks a question, identify the relevant table and columns.
3. Generate a syntactically correct SQL query.
4. Use the `sql_query` function to execute your query.
5. Answer the user's question based on the query results.
6. Always use the provided table name and column names exactly as shown in the JSON schema.

The following metadata describes the available tables and their structures:
{datas}
"""
    raise SystemExit(0)  # debug

def sql_query(query: str):
    """Run a SQL SELECT query on a SQLite database and return the results."""
    return pd.read_sql_query(query, sqlite3.connect("caches/database.db")).to_dict(orient="records")