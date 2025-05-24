# TGS Scraper
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
## Description
TGS Scraper is a Python script that scrapes data from the [TV Garden](https://tv.garden/) website and stores it in a MySQL database.


# Back-End
## Usage

### 🔧 Requirements

- Python 3.9+
- MySQL server
- `pip` or `pipenv` to install dependencies

### 📦 Installation
1. **Clone the repository**
```bash
git clone https://github.com/HDAI654/TGS.git
cd TGS
```
2. **Install dependencies**
```bash
pip install -r Back-End\requirements.txt
```
3. **Configure environment variables**
Create a .env file in the [Back-End](Back-End) folder (if not already exists):
```bash
DB_USER='your_db_user'
DB_PASS='your_db_password'
DB_PORT='3306'
DB_DATABASE='tv_garden_db'
```
### 🛠️ Setting up MySQL Database
Before running the project, ensure your MySQL server is up and running, and a database with the specified name exists.

Example commands:
```bash
mysql -u root -p
CREATE DATABASE tv_garden_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'TEST'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON tv_garden_db.* TO 'TEST'@'localhost';
FLUSH PRIVILEGES;
```

If your system can't find the mysql command, you can try using the example command:
```bash
set PATH=%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin
```
### 🧱 Creating Tables
Tables are automatically created when the script in model.py is run:
```bash
python src\model.py
```
This will initialize the following tables:

- Categories

- Countries

- Channel

### 🚀 Running the Application
```bash
python Back-End\app.py
```
The Flask server will start at:
```bash
http://localhost:5000
```


### 📂 Project Structure
```bash
├── app.py                 # Flask server and API routes
├── src/
│   ├── functions.py       # Crawler and update functions
│   ├── model.py           # DB models and schema
│   ├── logger.py          # Logging setup
├── .env                   # Environment variables
└── requirements.txt       # Dependencies
```
### Logging
Logs are recorded via the internal logger for debugging and monitoring purposes.


### 📡 API Endpoints
These are all the API with the json data that each API must recieve in the request body
---
`POST /get_data`

Get current data from the database.
```json
{
  "Type": "ctg" | "ctr" | "chn"
}
```
---
`POST /update_data`

Manually trigger an update from the remote source.
```json
{
  "Type": "ctg" | "ctr" | "chn"
}
```
---
`POST /get_status`

Check if an updater job is active and its interval.
```json
{
  "Type": "ctg" | "ctr" | "chn"
}
```
---
`POST /toggle_updater`

Pause or resume a background job.
```json
{
  "Type": "ctg" | "ctr" | "chn"
}
```
---
`POST /set_interval/<int:interval>`

Change update interval in minutes for a job.
```json
{
  "Type": "ctg" | "ctr" | "chn"
}
```
---
# Front-End

## Usage
### 🔧 Requirements
- Node.js 18.16.0+
- npm 9.5.1+

### 📦 Installation
1. **Clone the repository**
```bash
git clone https://github.com/HDAI654/TGS.git
cd TGS
```
2. **Install dependencies**
```bash
cd Front-End
npm install
```

### 🚀 Running the Application
**Start the development server**
```bash
npm start
```
The development server will start at:
```bash
http://localhost:3000
```

### 📂 Project Structure
```bash
├── public/
│   ├── index.html # HTML template
│   ├── favicon.ico # Favicon
│   ├── bootstrap.bundle.js # Bootstrap JS
│   └── emoji_font_style.css # Emoji font CSS
├──  src/
│   ├── App.js # Main application
│   ├── index.js # Entry point
│   └── components/
│      ├── Controller.jsx # component to control the update process
│      ├── Manager.jsx # Component to Manage all controllers
│      ├── Table.jsx # Component to display the data in a table
│      └── TableTabs.jsx # Component to show the tables in its tabs
├── .env
└── package.json
```

# 📝 Contributing
Contributions are welcome and encouraged! If you find a bug or have a suggestion for improvement, please open an issue or submit a pull request.

# Important Note
To Use this project you must run the Back-End and Front-End together.

# LICENSE
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



