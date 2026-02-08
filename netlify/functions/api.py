import json
import re
from urllib.parse import unquote

# Try to import real processor, otherwise fall back to mock
try:
    from data_processor import DataProcessor
    real_processor_available = True
except Exception:
    DataProcessor = None
    real_processor_available = False

# Import MockProcessor from server.py to replicate server behavior without running the Flask app
try:
    from server import MockProcessor
except Exception:
    MockProcessor = None


def _make_response(body, status=200, headers=None):
    return {
        'statusCode': status,
        'body': json.dumps(body),
        'headers': headers or {'Content-Type': 'application/json'}
    }


def _get_processor():
    if real_processor_available and DataProcessor:
        try:
            return DataProcessor()
        except Exception:
            pass
    # fallback
    if MockProcessor:
        return MockProcessor()
    # minimal fallback
    class _SimpleMock:
        def get_dashboard_stats(self, *_a, **_k):
            return {}
        def get_weekly_summary(self, *_a, **_k):
            return []
        def get_all_reports(self, *_a, **_k):
            return []
        def get_performance_trend(self, *_a, **_k):
            return []
        def get_video_activities(self, *_a, **_k):
            return []
        def gs_service(self):
            return None
    return _SimpleMock()


def _route(event_path, method, body=None):
    # Expect paths like /api/stats/today
    m = re.search(r"/api(?P<suffix>/.*)?$", event_path)
    suffix = m.group('suffix') if m else ''
    if not suffix:
        # root: serve simple status
        return _make_response({'status': 'ok'})

    parts = [p for p in suffix.split('/') if p]
    processor = _get_processor()

    # /api/stats/<date_range>
    if len(parts) >= 2 and parts[0] == 'stats':
        date_range = parts[1]
        data = processor.get_dashboard_stats(date_range)
        return _make_response(data)

    if parts[0] == 'weekly-summary':
        data = processor.get_weekly_summary()
        return _make_response(data)

    if parts[0] == 'recent-reports':
        df = processor.get_all_reports()
        # DataProcessor returns a pandas DataFrame; Mock returns list
        if hasattr(df, 'to_dict'):
            rows = df.head(20).to_dict(orient='records')
        else:
            rows = df if isinstance(df, list) else []
        return _make_response(rows)

    if parts[0] == 'performance-trend':
        data = processor.get_performance_trend()
        return _make_response(data)

    if parts[0] == 'video-activities':
        data = processor.get_video_activities()
        return _make_response(data)

    if parts[0] == 'export-csv':
        # For serverless function return CSV as text/plain
        df = processor.get_all_reports()
        try:
            if hasattr(df, 'to_csv'):
                csv = df.to_csv(index=False)
            else:
                # convert list of dicts to CSV minimal
                import io, csv
                rows = df if isinstance(df, list) else []
                if not rows:
                    csv = ''
                else:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                    csv = output.getvalue()
            return {
                'statusCode': 200,
                'body': csv,
                'headers': {'Content-Type': 'text/csv'}
            }
        except Exception as e:
            return _make_response({'error': str(e)}, status=500)

    # Add /add-report (POST)
    if parts[0] == 'add-report' and method == 'POST':
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}
        try:
            success = processor.gs_service.add_report(data)
            if success:
                return _make_response({'message': 'Report added'}, status=201)
            return _make_response({'error': 'Failed to add report'}, status=500)
        except Exception as e:
            return _make_response({'error': str(e)}, status=500)

    # update-report/{row_id} PUT
    if parts[0] == 'update-report' and len(parts) >= 2 and method == 'PUT':
        try:
            row_id = int(parts[1])
        except Exception:
            return _make_response({'error': 'Invalid row id'}, status=400)
        try:
            updates = json.loads(body) if body else {}
        except Exception:
            updates = {}
        try:
            success = processor.gs_service.update_report(row_id, updates)
            if success:
                return _make_response({'message': 'Updated'})
            return _make_response({'error': 'Update failed'}, status=500)
        except Exception as e:
            return _make_response({'error': str(e)}, status=500)

    # delete-report/{row_id} DELETE
    if parts[0] == 'delete-report' and len(parts) >= 2 and method == 'DELETE':
        try:
            row_id = int(parts[1])
        except Exception:
            return _make_response({'error': 'Invalid row id'}, status=400)
        try:
            success = processor.gs_service.delete_report(row_id)
            if success:
                return _make_response({'message': 'Deleted'})
            return _make_response({'error': 'Delete failed'}, status=500)
        except Exception as e:
            return _make_response({'error': str(e)}, status=500)

    return _make_response({'error': 'Not found'}, status=404)


def handler(event, context):
    # Netlify passes the original path in event['path']
    path = event.get('path') or event.get('rawPath') or '/'
    method = event.get('httpMethod', 'GET')
    body = event.get('body')
    # Event bodies might be base64 encoded; Netlify normally sends raw string
    return _route(unquote(path), method, body)
