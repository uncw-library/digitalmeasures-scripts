from datetime import datetime
import psycopg2

def update_joblog():
    query = f"""
        UPDATE daily_jobs
        SET last_ran = '{datetime.now().isoformat()[:10]}'
        WHERE name = 'vivo_data_update'
    """
    host = os.getenv("JOBLOG_DB_HOST")
    user = os.getenv("JOBLOG_DB_USER")
    password = os.getenv("JOBLOG_DB_PASS")
    try:
        conn = psycopg2.connect(f"dbname=JobLog user={user} host={host} password={password}")
        conn.autocommit = True
    except Exception:
        print('no joblog db connection')
        return
    
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
