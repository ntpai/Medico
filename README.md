# Medico

This project uses python3.12 version and has been tested in linux systems only( if testing in other OS, just refer to the below simple setup and edit the commands based on your device).

## Setup 

- Clone this project.
- Move to the cloned directory and create a virtual environment.
  ```
  python3.12 -m venv .venv
  ```
- Activate the virtual environment and install the requirements from the requirements.txt
- Move to the melanoma dir and run 
  ```
  python manage.py makemigrations

  python manage.py migrate
  ```

- Setup complete. Now run the server with
  ```
  python manage.py runserver
  ```

- Before running the server, you can create the superuser(admin) with django's createsuper command. Example:
  ```
  python manage.py createsuperuser
  ```
