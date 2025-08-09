
Install dependencies:

sudo pip3 install django djangorestframework yfinance plotly django-cors-headers

Start backend:
python3 manage.py migrate
python3 manage.py runserver

Debug in vscode:
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Django",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/manage.py",
      "args": [
        "runserver",
        "--noreload"
      ],
      "django": true
    }
  ]
}

Setup the frontned
Frontend uses plotly.js-dist-min for plotting
In /frontend:
npm install
npm install axios
npm run dev
