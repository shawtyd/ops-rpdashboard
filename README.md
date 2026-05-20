# Golden Bear Home Inspections - Operations Dashboard

A comprehensive Flask-based operations dashboard for tracking KPI metrics, growth coordinator activities, and operational performance.

## Features

### Growth Coordinator Dashboard
- **Activity Log**: Track 10 key metrics including calls, conversations, meetings, reviews, CRM updates, and more
- **4-Week KPI Dashboard**: Visualize performance across 4 weeks with automatic average calculations
- **Color-Coded Status**: Green (on target), Yellow (warning), Red (below target)
- **Notes & Obstacles**: Record weekly notes and obstacles
- **Report Generation**: Copy formatted reports for leadership

### Backend Features
- **SQLite Database**: Persistent storage of all KPI data
- **RESTful API**: Full CRUD endpoints for metrics management
- **Analytics Endpoints**: Weekly summaries, monthly trends, and 4-week averages
- **Data Persistence**: Server-side storage with timestamp tracking

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository
```bash
cd ops-rpdashboard
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
flask db init
python app.py
```

5. (Optional) Seed with sample data
```bash
flask seed-db
```

## Running the Application

### Development Mode
```bash
python app.py
```

The dashboard will be available at `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### KPI Metrics

#### Save/Update Metric
```
POST /api/kpi
Content-Type: application/json

{
  "week": 1,
  "metric_name": "Calls",
  "value": 45,
  "target": 50,
  "notes": "Good week"
}
```

#### Get Metrics by Week
```
GET /api/kpi/week/<week>
```

#### Get Metric History
```
GET /api/kpi/metric/<metric_name>
```

#### Get All Metrics
```
GET /api/kpi/all
```

#### Delete Metric
```
DELETE /api/kpi/<metric_id>
```

### Analytics

#### Weekly Summary
```
GET /api/analytics/weekly-summary?week=1
```

#### Monthly Trend
```
GET /api/analytics/monthly-trend?metric_name=Calls&weeks=4
```

#### 4-Week Average
```
GET /api/analytics/4-week-average
```

### Ops Metrics

#### Save Ops Metric
```
POST /api/ops-metric
Content-Type: application/json

{
  "metric_type": "daily_outreach",
  "value": 25,
  "notes": "High engagement today"
}
```

#### Get Ops Metrics by Type
```
GET /api/ops-metric/type/<metric_type>
```

#### Get Recent Ops Metrics
```
GET /api/ops-metric/recent/<limit>
```

## Tracked Metrics

The dashboard tracks these 10 key metrics:

1. **Calls** (Target: 50)
2. **Conversations** (Target: 30)
3. **Meetings Scheduled** (Target: 15)
4. **Meetings Completed** (Target: 12)
5. **Inactive Outreach** (Target: 8)
6. **Reviews Requested** (Target: 10)
7. **Reviews Generated** (Target: 8)
8. **CRM Updates** (Target: 20)
9. **Duplicates Removed** (Target: 5)
10. **Postcards** (Target: 15)

## Dashboard Features

### Activity Log
- Quick input cards for daily metrics
- Shows target for each metric
- Real-time counter updates

### KPI Table
- 4-week view with individual week columns
- Auto-calculated 4-week average
- Color-coded status indicators
- Target comparison column

### Report Generation
- Copy formatted report for leadership
- Includes metric values, percentages, and notes
- Easy clipboard integration

### Data Persistence
- All data saved to SQLite database
- Server-side timestamps for all entries
- Automatic sync status indication

## Database Schema

### KPIMetric
- `id`: Primary key
- `week`: Week number (1-4)
- `metric_name`: Name of the metric
- `value`: Current value
- `target`: Target value for comparison
- `notes`: Optional notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### OpsMetric
- `id`: Primary key
- `date`: Date of metric
- `metric_type`: Type of operational metric
- `value`: Metric value
- `notes`: Optional notes
- `updated_at`: Last update timestamp

## Troubleshooting

### Database Issues
If you encounter database errors, reset the database:
```bash
rm dashboard.db
python app.py
```

### Port Already in Use
If port 5000 is in use, specify a different port:
```bash
python -c "from app import app; app.run(port=5001)"
```

### Virtual Environment Issues
Ensure you're in the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Contributing

When adding new features:
1. Add new metrics to the `METRICS` array in `dashboard.html`
2. Update the database schema in `app.py` if needed
3. Create corresponding API endpoints
4. Update this README with new features

## License

Internal Use Only - Golden Bear Home Inspections

## Support

For issues or questions, contact the development team.
