## Installation guides

1. Clone the project from Github
    ```
    git clone https://github.com/yxzuz/ku-polls.git
    ```
2. Open the project file in your IDE
3. Go to ku-polls directory
    ```
    cd ku-polls
    ```
4. Create your virtual environment
    ```
    python3 -m venv env
    ```
5. Activate virtual environment
   ```
   # On Mac/Linux
   source env/bin/activate
   
   # On Window
   env\Scripts\activate
   ```
6. Install requirements.txt
    ```
    pip install -r requirements.txt
    ```
7. Set environment variables
   ```
   # create .env file and copy from template: sample.env
   # On Mac/Linux
   cp sample.env .env
   
   # On Window
   copy sample.env .env
   ```
8. Replace SECRET_KEY with your own value
   ```
   # doing this in Python Shell
   from django.core.management.utils import get_random_secret_key
   
   # copy this value and replace SECRET_KEY in .env file
   print(get_random_secret_key())
   ```
9. Run Migrations
    ```
    python manage.py migrate
    ```
10. Load fixture data
    ```
    python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
    ```
11. Run tests
    ```
    python manage.py test
    ```
12. Run server
    ```
    python manage.py runserver
    ```