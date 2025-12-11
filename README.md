# database-interface-platform
A platform for data query and visualization.
## Dependencies
Developed in Windows.
- python >= 3.8  
- python dependencies:  
    pymysql (for MySQL interface)  
    lxml (for spider)  
    flask, flask_cors (for backend)  
    jieba (for wordclould function)
    numpy, opencv-python (for image processing)

- JavaScript dependencies:  
    Node.js (with NPM included)
    Use `npm install` in `frontend` folder to install the dependent packages.
    Packages mainly include: React, react-router-dom, antd, echarts-for-react, etc.
    Your browser should support ES6, HTML5  

## Test of frontend and backend during development
### Frontend
Execute command: `path-to-the-project/frontend> npm start`
Running on `http://localhost:3000` by default.
### Backend
Execute command: `path-to-the-project/backend> python run.py`
Running on `http://localhost:5000` by default.