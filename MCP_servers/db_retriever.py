import os
import psycopg2
from typing import List, Tuple
from dotenv import load_dotenv
import mysql.connector

# .env 파일 로드
load_dotenv()

# PostgreSQL 연결 정보 (환경 변수에서 로드)
PG_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT")),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname": os.getenv("PG_DBNAME")
}

def get_fitness_logs(user_id: str, limit: int = 10) -> List[str]:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT f.date, e.exercise_name, e.sets, e.reps, e.weight
        FROM fitness_detail f
        JOIN fitnessdetail_exerciseinfolist e
        ON f.id = e.fitness_detail_id
        WHERE f.user_id = %s
        ORDER BY f.date DESC
        LIMIT %s
    """, (user_id, limit))
    logs = []
    for row in cur.fetchall():
        date, name, sets, reps, weight = row
        logs.append(f"{date}: {name} {sets}세트 x {reps}회 ({weight}kg)")
    cur.close()
    conn.close()
    return logs

def get_running_logs(user_id: str, limit: int = 10) -> List[str]:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, distance, duration, memo
        FROM running_detail
        WHERE user_id = %s
        ORDER BY date DESC
        LIMIT %s
    """, (user_id, limit))
    logs = []
    for row in cur.fetchall():
        date, distance, duration, memo = row
        logs.append(f"{date}: 러닝 {distance}m, {duration}분 - {memo}")
    cur.close()
    conn.close()
    return logs

def get_study_logs(user_id: str, limit: int = 10) -> List[str]:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, subject, duration, memo
        FROM study_detail
        WHERE user_id = %s
        ORDER BY date DESC
        LIMIT %s
    """, (user_id, limit))
    logs = []
    for row in cur.fetchall():
        date, subject, duration, memo = row
        logs.append(f"{date}: {subject} 공부 {duration}분 - {memo}")
    cur.close()
    conn.close()
    return logs

def get_user_activities(user_id: str) -> List[str]:
    fitness = get_fitness_logs(user_id)
    running = get_running_logs(user_id)
    study = get_study_logs(user_id)
    print("📌 user_id:", user_id)
    print("📌 활동 로그:", fitness, running, study)
    return fitness + running + study


"""챗 히스토리는 백엔드에서 보내주기로 함. 리턴은 List[Dict()]"""
# def get_chat_history(user_id: int, limit: int = 10) -> List[Tuple[str, str]]:
#     """
#     주어진 user_id의 최근 chat history를 불러옴
#     :return: [(role, message), ...] 형태
#     """
#     conn = mysql.connector.connect(
#         host=os.getenv("MYSQL_HOST"),
#         port=int(os.getenv("MYSQL_PORT", "3306")),
#         user=os.getenv("MYSQL_USER"),
#         password=os.getenv("MYSQL_PASSWORD"),
#         database=os.getenv("MYSQL_DB")
#     )
#     cursor = conn.cursor()

#     query = """
#         SELECT role, message
#         FROM chat_history
#         WHERE user_id = %s
#         ORDER BY send_time DESC
#         LIMIT %s
#     """
#     cursor.execute(query, (user_id, limit))
#     result = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return [(role, message) for role, message in result]
