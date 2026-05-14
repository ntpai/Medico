# Medico: ML Integrated Healthcare template

Medico is a foundational Django web application template featuring an integrated Machine Learning model. Designed to accelerate the development of healthcare platforms, this specific boilerplate is configured for **Melanoma detection/analysis**, demonstrating the practical deployment of AI models into a clean web interface.

## Tech stacks

* **Backend** : Python 3.12, Django
* **Frontend**: HTML, CSS, JS
* **Database**: Sqlite
* **Machine Learning**: Scikit-learn

This project uses python3.12 version. Setup steps should be same for every OS.

## Setup

- Clone this project.
  ```
  git clone https://github.com/ntpai/Medico.git
  cd Medico
  ```
- Move to the cloned directory and create a virtual environment.
  ```
  python3.12 -m venv .venv
  ```
- Activate the virtual environment and install the requirements from the requirements.txt.
  ```
    
  On Windows: .venv\Scripts\activate
  On macOS/Linux: source .venv/bin/activate

  pip install -r requirements.txt

  ```  
- Move to the melanoma dir and run 
  ```
  python manage.py makemigrations

  python manage.py migrate
  ```
  
- Before running the server, you can create the superuser(admin) with django's createsuper command. Example:
  ```
  python manage.py createsuperuser
  ```

- Setup complete. Now run the server with
  ```
  python manage.py runserver
  ```
  The application should be up and running at *http://127.0.0.1:8000/*
