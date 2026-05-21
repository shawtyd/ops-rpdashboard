import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "dashboard.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class KPIMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, default=0)
    target = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'week': self.week,
            'metric_name': self.metric_name,
            'value': self.value,
            'target': self.target,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class OpsMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    metric_type = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'metric_type': self.metric_type,
            'value': self.value,
            'notes': self.notes,
            'updated_at': self.updated_at.isoformat()
        }


class RetentionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(100), nullable=False)
    brokerage = db.Column(db.String(100))
    record_type = db.Column(db.String(50), nullable=False)  # postcard, birthday, inactive
    status = db.Column(db.String(100))
    date_assigned = db.Column(db.DateTime)
    date_sent = db.Column(db.DateTime)
    birthday = db.Column(db.String(20))
    last_inspection = db.Column(db.DateTime)
    last_contact = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'brokerage': self.brokerage,
            'record_type': self.record_type,
            'status': self.status,
            'date_assigned': self.date_assigned.isoformat() if self.date_assigned else None,
            'date_sent': self.date_sent.isoformat() if self.date_sent else None,
            'birthday': self.birthday,
            'last_inspection': self.last_inspection.isoformat() if self.last_inspection else None,
            'last_contact': self.last_contact.isoformat() if self.last_contact else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# KPI Metric Routes
@app.route('/api/kpi', methods=['POST'])
def save_kpi():
    data = request.json
    metric = KPIMetric.query.filter_by(
        week=data.get('week'),
        metric_name=data.get('metric_name')
    ).first()

    if metric:
        metric.value = data.get('value', metric.value)
        metric.target = data.get('target', metric.target)
        metric.notes = data.get('notes', metric.notes)
    else:
        metric = KPIMetric(
            week=data.get('week'),
            metric_name=data.get('metric_name'),
            value=data.get('value', 0),
            target=data.get('target', 0),
            notes=data.get('notes', '')
        )
        db.session.add(metric)

    db.session.commit()
    return jsonify(metric.to_dict()), 201


@app.route('/api/kpi/<int:week>/<metric_name>', methods=['GET'])
def get_kpi(week, metric_name):
    metric = KPIMetric.query.filter_by(week=week, metric_name=metric_name).first()
    if not metric:
        return jsonify({'error': 'Metric not found'}), 404
    return jsonify(metric.to_dict())


@app.route('/api/kpi/week/<int:week>', methods=['GET'])
def get_week_kpis(week):
    metrics = KPIMetric.query.filter_by(week=week).all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/kpi/metric/<metric_name>', methods=['GET'])
def get_metric_history(metric_name):
    metrics = KPIMetric.query.filter_by(metric_name=metric_name).order_by(KPIMetric.week).all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/kpi/all', methods=['GET'])
def get_all_kpis():
    metrics = KPIMetric.query.all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/kpi/<int:metric_id>', methods=['DELETE'])
def delete_kpi(metric_id):
    metric = KPIMetric.query.get(metric_id)
    if not metric:
        return jsonify({'error': 'Metric not found'}), 404

    db.session.delete(metric)
    db.session.commit()
    return jsonify({'message': 'Metric deleted'}), 200


# Ops Metrics Routes
@app.route('/api/ops-metric', methods=['POST'])
def save_ops_metric():
    data = request.json
    metric = OpsMetric(
        metric_type=data.get('metric_type'),
        value=data.get('value', 0),
        notes=data.get('notes', '')
    )
    db.session.add(metric)
    db.session.commit()
    return jsonify(metric.to_dict()), 201


@app.route('/api/ops-metric/type/<metric_type>', methods=['GET'])
def get_ops_metrics_by_type(metric_type):
    metrics = OpsMetric.query.filter_by(metric_type=metric_type).order_by(OpsMetric.date.desc()).all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/ops-metric/recent/<int:limit>', methods=['GET'])
def get_recent_ops_metrics(limit=10):
    metrics = OpsMetric.query.order_by(OpsMetric.date.desc()).limit(limit).all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/ops-metric/<int:metric_id>', methods=['PUT'])
def update_ops_metric(metric_id):
    metric = OpsMetric.query.get(metric_id)
    if not metric:
        return jsonify({'error': 'Metric not found'}), 404

    data = request.json
    metric.value = data.get('value', metric.value)
    metric.notes = data.get('notes', metric.notes)
    db.session.commit()
    return jsonify(metric.to_dict()), 200


@app.route('/api/ops-metric/<int:metric_id>', methods=['DELETE'])
def delete_ops_metric(metric_id):
    metric = OpsMetric.query.get(metric_id)
    if not metric:
        return jsonify({'error': 'Metric not found'}), 404

    db.session.delete(metric)
    db.session.commit()
    return jsonify({'message': 'Metric deleted'}), 200


# Retention Records Routes
@app.route('/api/retention', methods=['POST'])
def save_retention_record():
    data = request.json
    record = RetentionRecord(
        agent_name=data.get('agent_name'),
        brokerage=data.get('brokerage'),
        record_type=data.get('record_type'),
        status=data.get('status'),
        date_assigned=data.get('date_assigned'),
        date_sent=data.get('date_sent'),
        birthday=data.get('birthday'),
        last_inspection=data.get('last_inspection'),
        last_contact=data.get('last_contact'),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@app.route('/api/retention/<record_type>', methods=['GET'])
def get_retention_by_type(record_type):
    records = RetentionRecord.query.filter_by(record_type=record_type).order_by(RetentionRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/retention/<int:record_id>', methods=['PUT'])
def update_retention(record_id):
    record = RetentionRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    data = request.json
    record.status = data.get('status', record.status)
    record.date_sent = data.get('date_sent', record.date_sent)
    record.notes = data.get('notes', record.notes)
    db.session.commit()
    return jsonify(record.to_dict()), 200


@app.route('/api/retention/<int:record_id>', methods=['DELETE'])
def delete_retention(record_id):
    record = RetentionRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Record deleted'}), 200


# Analytics Routes
@app.route('/api/analytics/weekly-summary', methods=['GET'])
def get_weekly_summary():
    week = request.args.get('week', type=int)
    metrics = KPIMetric.query.filter_by(week=week).all()

    summary = {
        'week': week,
        'total_metrics': len(metrics),
        'metrics_on_target': sum(1 for m in metrics if m.value >= m.target),
        'metrics_below_target': sum(1 for m in metrics if m.value < m.target),
        'average_completion': round(sum(m.value / m.target * 100 for m in metrics if m.target > 0) / len(metrics), 2) if metrics else 0
    }
    return jsonify(summary)


@app.route('/api/analytics/monthly-trend', methods=['GET'])
def get_monthly_trend():
    metric_name = request.args.get('metric_name')
    weeks = request.args.get('weeks', 4, type=int)

    metrics = KPIMetric.query.filter_by(metric_name=metric_name).order_by(KPIMetric.week.desc()).limit(weeks).all()
    trend = [{
        'week': m.week,
        'value': m.value,
        'target': m.target,
        'completion_percent': round((m.value / m.target * 100) if m.target > 0 else 0, 2)
    } for m in reversed(metrics)]

    return jsonify(trend)


@app.route('/api/analytics/4-week-average', methods=['GET'])
def get_4week_average():
    metrics_data = {}
    weeks = [1, 2, 3, 4]

    for week in weeks:
        weekly_metrics = KPIMetric.query.filter_by(week=week).all()
        for m in weekly_metrics:
            if m.metric_name not in metrics_data:
                metrics_data[m.metric_name] = {'values': [], 'target': m.target}
            metrics_data[m.metric_name]['values'].append(m.value)

    averages = {}
    for metric_name, data in metrics_data.items():
        avg = round(sum(data['values']) / len(data['values']), 2) if data['values'] else 0
        averages[metric_name] = {
            'average': avg,
            'target': data['target'],
            'completion_percent': round((avg / data['target'] * 100) if data['target'] > 0 else 0, 2)
        }

    return jsonify(averages)


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


# Dashboard route
@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    from datetime import datetime

    # Clear existing data
    KPIMetric.query.delete()
    OpsMetric.query.delete()

    # Growth Coordinator metrics
    metrics = [
        ('Calls', 1, 45, 50),
        ('Conversations', 1, 28, 30),
        ('Meetings Scheduled', 1, 12, 15),
        ('Meetings Completed', 1, 10, 12),
        ('Inactive Outreach', 1, 5, 8),
        ('Reviews Requested', 1, 8, 10),
        ('Reviews Generated', 1, 6, 8),
        ('CRM Updates', 1, 15, 20),
        ('Duplicates Removed', 1, 3, 5),
        ('Postcards', 1, 10, 15),
    ]

    for metric_name, week, value, target in metrics:
        kpi = KPIMetric(
            week=week,
            metric_name=metric_name,
            value=value,
            target=target,
            notes=f'Week {week} data for {metric_name}'
        )
        db.session.add(kpi)

    db.session.commit()
    print('Database seeded with sample data.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
