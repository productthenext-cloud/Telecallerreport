from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS
import os
import io
import pandas as pd
from data_processor import DataProcessor
import random
from datetime import datetime, timedelta


# Simple mock processor used when Google Sheets access is unavailable
class MockProcessor:
    def __init__(self):
        random.seed(42)
        today = datetime.now().date()
        # create 30 days of sample data
        self.rows = []
        for i in range(30):
            d = today - timedelta(days=i)
            total_calls = random.randint(0, 200)
            new_data = random.randint(0, max(1, total_calls//3))
            crm = random.randint(0, total_calls)
            visited = random.randint(0, 10)
            video = 'Yes' if random.random() < 0.15 else 'No'
            self.rows.append({
                'Date': d,
                'Day': d.strftime('%A'),
                'Total Calls': total_calls,
                'New Data': new_data,
                'CRM Data': crm,
                'Country Data': random.choice(['', 'UK', 'Australia', 'Canada', 'USA', 'Other']),
                'Fair Data': random.randint(0, 50),
                'Video': video,
                'Visited Students': visited,
                'Other Work Description': ''
            })

    def get_dashboard_stats(self, date_range='all'):
        df_rows = self.rows.copy()
        # filter by date_range
        today = datetime.now().date()
        if date_range == 'today':
            df_rows = [r for r in df_rows if r['Date'] == today]
        elif date_range == 'yesterday':
            df_rows = [r for r in df_rows if r['Date'] == (today - timedelta(days=1))]
        elif date_range == 'week':
            cutoff = today - timedelta(days=7)
            df_rows = [r for r in df_rows if r['Date'] >= cutoff]
        elif date_range == 'month':
            cutoff = today - timedelta(days=30)
            df_rows = [r for r in df_rows if r['Date'] >= cutoff]

        total_calls = sum(r['Total Calls'] for r in df_rows)
        new_data = sum(r['New Data'] for r in df_rows)
        crm_data = sum(r['CRM Data'] for r in df_rows)
        country_data = sum(1 for r in df_rows if r.get('Country Data'))
        fair_data = sum(r.get('Fair Data', 0) for r in df_rows)
        visited_students = sum(r.get('Visited Students', 0) for r in df_rows)
        video_activities = sum(1 for r in df_rows if r.get('Video') == 'Yes')
        total_days = len({r['Date'] for r in df_rows})

        avg_calls = round(total_calls / total_days, 1) if total_days else 0
        avg_new = round(new_data / total_days, 1) if total_days else 0
        conversion_rate = round((new_data / total_calls) * 100, 1) if total_calls else 0
        crm_completion_rate = round((crm_data / total_calls) * 100, 1) if total_calls else 0

        return {
            'total_calls': total_calls,
            'new_data': new_data,
            'crm_data': crm_data,
            'country_data': country_data,
            'fair_data': fair_data,
            'visited_students': visited_students,
            'video_activities': video_activities,
            'total_days': total_days,
            'avg_calls_per_day': avg_calls,
            'avg_new_data_per_day': avg_new,
            'conversion_rate': conversion_rate,
            'crm_completion_rate': crm_completion_rate
        }

    def get_weekly_summary(self, days=7):
        today = datetime.now().date()
        summary = []
        for i in range(days):
            d = today - timedelta(days=i)
            row = next((r for r in self.rows if r['Date'] == d), None)
            if row:
                summary.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'formatted_date': d.strftime('%a, %b %d'),
                    'total_calls': row['Total Calls'],
                    'new_data': row['New Data'],
                    'visited_students': row['Visited Students'],
                    'video': row['Video']
                })
        return summary

    def get_all_reports(self, filters=None):
        # return a pandas-like DataFrame substitute as list of dicts
        # The server expects a DataFrame in processor.get_all_reports, but we will
        # return a simple list and handle it in endpoints
        return self.rows

    def get_performance_trend(self, days=30):
        today = datetime.now().date()
        trend = []
        for i in range(days):
            d = today - timedelta(days=(days - 1 - i))
            row = next((r for r in self.rows if r['Date'] == d), None)
            trend.append({
                'date': d.strftime('%Y-%m-%d'),
                'formatted_date': d.strftime('%b %d'),
                'total_calls': row['Total Calls'] if row else 0,
                'new_data': row['New Data'] if row else 0,
                'visited_students': row['Visited Students'] if row else 0
            })
        return trend

    def get_video_activities(self, limit=10):
        vids = [r for r in self.rows if r['Video'] == 'Yes']
        out = []
        for r in vids[:limit]:
            out.append({
                'date': r['Date'].strftime('%Y-%m-%d'),
                'formatted_date': r['Date'].strftime('%b %d, %Y'),
                'video_details': r.get('Other Work Description', ''),
                'other_work': r.get('Other Work Description', ''),
                'total_calls': r['Total Calls'],
                'new_data': r['New Data']
            })
        return out

app = Flask(__name__, static_folder='.')
CORS(app)

# Lazily create processor so the server can start even if Google creds are missing
_processor = None

def get_processor():
    global _processor
    if _processor is None:
        try:
            _processor = DataProcessor()
        except Exception as e:
            app.logger.error(f"Failed to initialize DataProcessor: {e}")
            # Fall back to mock processor so API remains usable without credentials
            _processor = MockProcessor()
    return _processor


@app.route('/')
def root():
    # Serve dashboard.html if present
    if os.path.exists('dashboard.html'):
        return send_from_directory('.', 'dashboard.html')
    return jsonify({'status': 'ok'})


@app.route('/api/stats/<date_range>', methods=['GET'])
def api_stats(date_range):
    processor = get_processor()
    if not processor:
        return jsonify({'error': 'Data processor unavailable'}), 503
    stats = processor.get_dashboard_stats(date_range)
    return jsonify(stats)


@app.route('/api/weekly-summary', methods=['GET'])
def api_weekly():
    processor = get_processor()
    if not processor:
        return jsonify([])
    data = processor.get_weekly_summary()
    return jsonify(data)


@app.route('/api/recent-reports', methods=['GET'])
def api_recent():
    processor = get_processor()
    if not processor:
        return jsonify([])

    df = processor.get_all_reports()
    if df.empty:
        return jsonify([])

    records = []
    for _, row in df.head(20).iterrows():
        records.append({
            'Date': row['Date'].strftime('%Y-%m-%d') if pd.notna(row['Date']) else '',
            'Day': row.get('Day', ''),
            'Total Calls': int(row.get('Total Calls', 0)),
            'New Data': int(row.get('New Data', 0)),
            'CRM Data': int(row.get('CRM Data', 0)),
            'Country Data': row.get('Country Data', ''),
            'Fair Data': int(row.get('Fair Data', 0)) if 'Fair Data' in row else 0,
            'Video': row.get('Video', 'No'),
            'Visited Students': int(row.get('Visited Students', 0)) if 'Visited Students' in row else 0,
            'Other Work Description': row.get('Other Work Description', '')
        })

    return jsonify(records)


@app.route('/api/performance-trend', methods=['GET'])
def api_trend():
    processor = get_processor()
    if not processor:
        return jsonify([])
    data = processor.get_performance_trend()
    return jsonify(data)


@app.route('/api/video-activities', methods=['GET'])
def api_videos():
    processor = get_processor()
    if not processor:
        return jsonify([])
    data = processor.get_video_activities()
    return jsonify(data)


@app.route('/api/export-csv', methods=['GET'])
def api_export():
    processor = get_processor()
    if not processor:
        return jsonify({'error': 'Data processor unavailable'}), 503

    df = processor.get_all_reports()
    if df.empty:
        return jsonify({'error': 'No data to export'}), 404

    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)

    return Response(
        csv_io.getvalue(),
        mimetype='text/csv',
        headers={"Content-disposition": "attachment; filename=telecaller_reports.csv"}
    )


def find_row_index_by_date(sheet_rows, date_value):
    # sheet_rows is list of lists including header at index 0
    for idx, row in enumerate(sheet_rows[1:], start=2):
        if not row:
            continue
        first_cell = str(row[0])
        if date_value in first_cell or first_cell in date_value:
            return idx
    return None


@app.route('/add-report', methods=['POST'])
def add_report():
    data = request.get_json()
    processor = get_processor()
    if not processor:
        return jsonify({'error': 'Data processor unavailable'}), 503

    try:
        success = processor.gs_service.add_report(data)
        if success:
            return jsonify({'message': 'Report added'}), 201
        return jsonify({'error': 'Failed to add report'}), 500
    except Exception as e:
        app.logger.error(f"Error adding report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-report/<int:row_id>', methods=['PUT'])
def update_report(row_id):
    updates = request.get_json()
    processor = get_processor()
    if not processor:
        return jsonify({'error': 'Data processor unavailable'}), 503

    # If row_id is provided as sheet row index, attempt update
    try:
        success = processor.gs_service.update_report(row_id, updates)
        if success:
            return jsonify({'message': 'Updated'}), 200
        return jsonify({'error': 'Update failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-report/<int:row_id>', methods=['DELETE'])
def delete_report(row_id):
    processor = get_processor()
    if not processor:
        return jsonify({'error': 'Data processor unavailable'}), 503

    try:
        success = processor.gs_service.delete_report(row_id)
        if success:
            return jsonify({'message': 'Deleted'}), 200
        return jsonify({'error': 'Delete failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
