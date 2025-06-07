# Mapping of property tax auctions

A python flask project that easily displays properties from any csv file on an interactive map. It achieves this by using the Anthropic API for rough formatting and the Google Maps API for sleek presentation.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

- On macOS/Linux:

```bash
source venv/bin/activate
```

- On Windows:

```bash
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your environment variables:

```
PORT=5000
GOOGLE_API_KEY=xyz
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the application:

```bash
python app.py
```

The application will be available at `http://localhost:5000`
