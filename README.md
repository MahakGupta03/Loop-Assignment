# Store Monitoring System

## Installation

1. Create a virtual environment and activate it:
    ```
    python -m venv env
    ```
    activate it using 
    ```
    env\Scripts\activate
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

\on manage.py migrate
    ```

3. ```sh
    python manage.py makemigrations
    ```

4. ```sh
    python manage.py migrate
    ```

5. Load the data to database:
    ```sh
    pip manage.py load_data
    ```

6. Run Server:
    ```sh
    pip manage.py runserver
    ```

## API Endpoints

### `POST monitor/trigger_report/`

Triggers the report generation process.

**Response:**
```json
{
    "report_id": "unique-report-id"
}
```

### `GET /monitor/get_report/<unique-report-id>/`

