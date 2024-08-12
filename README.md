# DNS Health Check API

This FastAPI application checks the DNS health of a given domain by querying various DNS records (A, AAAA, SOA, NS, MX) and performing a DNSSEC analysis.

## Features
- Query DNS records for A, AAAA, SOA, NS, and MX.
- Perform DNSSEC analysis using `dnssec-analyzer`.
- Store the results in a MongoDB database.

## Requirements
- Python 3.8+
- MongoDB
- `dnssec-analyzer` binary (or a script to install it)

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/yourusername/dns-health-check.git
    cd dns-health-check
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure MongoDB is running locally on the default port.

4. Run the FastAPI application:
    ```sh
    uvicorn main:app --reload
    ```

5. Access the API at `http://localhost:8000`.

## Usage

- Check DNS health by accessing:
    ```
    GET /dns-health/{domain}
    ```

- Example:
    ```
    GET /dns-health/example.com
    ```

## Project Structure

- `main.py`: The main FastAPI application.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files to ignore in the repository.
- `dnssec-analyzer`: DNSSEC analysis tool.

## License
[MIT License](LICENSE)
