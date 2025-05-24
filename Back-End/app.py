from flask import Flask, render_template, jsonify, request
from src.model import Categories, Countries, Channel
from src.functions import update_categories, update_countries, update_channels
from apscheduler.schedulers.background import BackgroundScheduler
from src.logger import logger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AUTO_CRAWLER_INTERVAL = 30 # in minutes
scheduler = BackgroundScheduler()

# job definitions
job_map = {
    'ctg': {
        'job': scheduler.add_job(update_categories, 'interval', minutes=AUTO_CRAWLER_INTERVAL, id='ctg'),
        'update_func': update_categories,
        'model': Categories,
        "serializer": lambda c: {
            "id": c.id,
            "title": c.title
        }
    },
    'ctr': {
        'job': scheduler.add_job(update_countries, 'interval', minutes=AUTO_CRAWLER_INTERVAL, id='ctr'),
        'update_func': update_countries,
        'model': Countries,
        "serializer": lambda c: {
            "id": c.id,
            "country_code": c.country_code,
            "country_name": c.country_name,
            "emoji": c.emoji,
            "time_zone": c.time_zone,
            "capital": c.capital
        }
    },
    'chn': {
        'job': scheduler.add_job(update_channels, 'interval', minutes=AUTO_CRAWLER_INTERVAL, id='chn'),
        'update_func': update_channels,
        'model': Channel,
        "serializer": lambda c: {
            "id": c.id,
            "unique_code": c.unique_code,
            "title": c.title,
            "video_url": c.video_url,
            "youtube_url": c.youtube_url,
            "country": c.country.id if c.country else None,
            "category_ids": c.category_ids,
            "youtube": c.youtube,
            "geo_block": c.geo_block
        }
    }
}

scheduler.start()

# =======================
# Unified API Handlers
# =======================

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        job_type = data.get("Type")

        if job_type not in job_map:
            return jsonify({"status": "error", "message": "Invalid Type"}), 400

        logger.info(f"/get_data called for Type={job_type}")

        model = job_map[job_type]['model']
        serializer = job_map[job_type]['serializer']
        
        items = model.select()
        serialized_data = [serializer(item) for item in items]

        return jsonify({"status": "success", "data": serialized_data}), 200

    except Exception as e:
        logger.error(f"Error in /get_data (Type : {data.get('Type', 'unknown')}): {e}")
        return jsonify({"status": "error"}), 500


@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        data = request.get_json()
        job_type = data.get("Type")
        if job_type not in job_map:
            return jsonify({"status": "error", "message": "Invalid Type"}), 400

        logger.info(f"/update_data called for Type={job_type}")
        success = job_map[job_type]['update_func']()
        logger.info(f"/update_data finished for Type={job_type}: {'success' if success else 'failure'}")
        return jsonify({"status": "success" if success else "error"})
    except Exception as e:
        logger.error(f"Error in /update_data: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/get_status', methods=['POST'])
def get_status():
    try:
        data = request.get_json()
        job_type = data.get("Type")
        if job_type not in job_map:
            return jsonify({"status": "error", "message": "Invalid Type"}), 400
        
        job = job_map[job_type]['job']
        return jsonify({
            "status": job.next_run_time is not None,
            "interval": job.trigger.interval.seconds / 60,
        })
    except Exception as e:
        logger.error(f"Error in /get_status: {e}")
        return jsonify({"status": "error"})


@app.route('/toggle_updater', methods=['POST'])
def toggle_updater():
    try:
        data = request.get_json()
        job_type = data.get("Type")
        if job_type not in job_map:
            return jsonify({"status": "error", "message": "Invalid Type"}), 400

        job = job_map[job_type]['job']
        if job.next_run_time is None:
            job.resume()
            logger.info(f"{job_type} updater resumed")
        else:
            job.pause()
            logger.info(f"{job_type} updater paused")

        return jsonify({"status": True})
    except Exception as e:
        logger.error(f"Error in toggle_updater: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/set_interval/<int:interval>', methods=['POST'])
def set_interval(interval):
    try:
        data = request.get_json()
        job_type = data.get("Type")
        if job_type not in job_map:
            return jsonify({"status" : "error", "message": "Invalid Type"}), 400

        job_map[job_type]['job'].reschedule('interval', minutes=interval)
        logger.info(f"{job_type} updater interval set to {interval} minutes")
        return jsonify({"status" : "success"})
    except Exception as e:
        logger.error(f"Error in set_interval: {e}")
        return jsonify({"status" : "success"})

# =======================
# Run Server
# =======================
if __name__ == '__main__':
    # Pause all jobs initially
    for item in job_map.values():
        item['job'].pause()

    logger.info("All jobs paused")
    logger.info("Starting the server")
    app.run(debug=True, port=5000, host='localhost')
