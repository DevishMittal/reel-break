# ReelBreak: A Digital Wellbeing Assistant

## Project Overview

ReelBreak is a digital wellbeing assistant designed to help users be more mindful of their short-form video consumption. It monitors screen activity, detects when users are engaged with platforms like TikTok, Instagram Reels, YouTube Shorts, Snapchat, and Facebook Reels, and provides gentle interventions to encourage breaks and promote healthier digital habits.

## Key Features
1. **Platform Detection**: Automatically identifies short-form video platforms using OCR and AI analysis
2. **Usage Tracking**: Monitors session length and total daily screen time across platforms
3. **Smart Interventions**: Provides personalized, non-judgmental reminders when usage limits are approached
4. **Usage Dashboard**: Visualizes usage patterns with detailed charts and statistics
Customizable Limits: Set your own daily and session time goals

## Technologies Used

### Frontend

-   **React**: A JavaScript library for building user interfaces.
-   **Tailwind CSS**: A utility-first CSS framework for rapidly designing custom user interfaces.
-   **Vite**: A build tool that provides a fast and optimized development experience.
-   **Axios**: A promise-based HTTP client for making API requests to the backend.

### Backend

-   **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
-   **aiosqlite**: Asynchronous integration with SQLite for database management.
-   **Groq**: A platform for accessing large language models (LLMs) for platform detection and intervention message generation.
-   **Pydantic**: Data validation and settings management using Python type annotations.


### Other

-   **ScreenPipe**: A tool for capturing screen content and performing OCR (Optical Character Recognition).
-   **Groq LLM**: Used for detecting short-form video platforms and generating intervention messages.

## Installation and Setup

Follow these steps to set up ReelBreak on your local machine:

### Prerequisites

-   **Python 3.7+**: Ensure you have Python installed.
-   **Node.js and npm**: Required for the frontend.
-   **ScreenPipe**: Install and configure ScreenPipe to capture screen content.

### Backend Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd Server
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    -   Create a [.env](http://_vscodecontentref_/0) file in the [Server](http://_vscodecontentref_/1) directory.
    -   Add the following variables:

        ```
        GROQ_API_KEY=<your_groq_api_key>
        ```

    -   Obtain a Groq API key from [GroqCloud](https://console.groq.com/keys).

5.  **Initialize the database:**

    -   Run the `main.py` file to initialize the database:

        ```bash
        python main.py
        ```

### Frontend Setup

1.  **Navigate to the frontend directory:**

    ```bash
    cd ../frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

## Running the Application

1.  **Start the backend server:**

    ```bash
    cd Server
    python main.py
    ```

2.  **Start the frontend development server:**

    ```bash
    cd frontend
    npm run dev
    ```

3.  **Run the ScreenBreak client:**

    ```bash
    cd client
    python main.py
    ```

4.  **Access the application in your browser:**

    -   Open `http://localhost:5173` in your browser to view the ReelBreak dashboard.

## API Endpoints

### Backend (FastAPI)

-   `POST /process_screen`: Processes screen content and detects short-form video platforms.
-   `POST /update_settings`: Updates user preferences and settings.
-   `GET /usage_stats`: Retrieves usage statistics for today.
-   `GET /check_intervention`: Checks if an intervention is needed based on usage patterns.
-   `GET /debug/sessions`: Debug endpoint to view raw session data.
-   `GET /debug/platforms`: Debug endpoint to view all platform names in use.
-   `GET /admin/fix-platform-names`: Admin endpoint to standardize platform names in the database.
-   `GET /admin/reset-database`: Admin endpoint to completely reset the database and start fresh.
-   `GET /admin/generate-test-data`: Admin endpoint to generate test data for Instagram Reels.

## Acknowledgements
1. Groq for their powerful LLM API
2. ScreenPipe for screen content capture and OCR capabilities
3. FastAPI for the efficient Python API framework
4. React and the React community for frontend tools and libraries