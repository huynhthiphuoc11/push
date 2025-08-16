from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['matching_db']
jobs = db['jobs']

def ensure_job_id():
    count = 0
    for idx, doc in enumerate(jobs.find()):
        # Nếu đã có job_id và là số > 0 thì giữ nguyên
        job_id = doc.get('job_id')
        if isinstance(job_id, int) and job_id > 0:
            continue
        # Gán job_id mới (tăng dần, bắt đầu từ 1)
        jobs.update_one({'_id': doc['_id']}, {'$set': {'job_id': idx + 1}})
        count += 1
    print(f"Updated job_id for {count} jobs.")

if __name__ == "__main__":
    ensure_job_id()
