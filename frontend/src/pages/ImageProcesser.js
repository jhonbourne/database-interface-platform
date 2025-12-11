import { useState } from "react";
import { Link } from "react-router-dom";
import { Button, message } from 'antd'; // TODO: Show error info in Alert component

import './App.css';
import UserMenu from '../components/UserMenu/UserMenu';
import FileUpload from "../components/FileUpload/FileUpload";
import useFetchLogger from '../hooks/useFetchLogger';

import { URLS } from "../utils/request_urls";
import { requestSettings } from '../utils/request_settings';

import { Layout } from 'antd';
const { Header, Footer, Sider, Content } = Layout;

const ImageProcesser = () => {
    const [fileList, setFileList] = useState([]);
    const [resultResp, setResultResp] = useState({ data: null });
    const queryURL = URLS['GetDigit'];

    useFetchLogger('ImageProcesser',queryURL);

    const handleSubmit = async () => {
      const fileToSend = fileList[0];
      if (!fileToSend) {
        message.warning('Select an image first!');
        return;
      }
      const file = fileToSend.originFileObj;
      if (!file) {
        message.error('Unable to obtain the file object.');
        return;
      }

      const formData = new FormData();
      formData.append('image', file);
      for (let [key, value] of formData.entries()){
        console.log(key,value);
      }

      // Don't set Content-Type; browser will set correct multipart boundary
      delete requestSettings.headers;
      const settings = { ...requestSettings, method: 'POST',
         body: formData,
        //  headers: {"Content-Type": "multipart/form-data"}
      };

      try {
        const response = await fetch(queryURL, settings);
        if (!response.ok) {
          const msg = await response.json().catch(() => null);
          const text = (msg && (msg.status || msg.message)) || `HTTP ${response.status}`;
          throw new Error(text);
        }
        const dat = await response.json();
        console.log(dat.status)
        setResultResp(dat);
      } catch (error) {
        message.error(error.toString());
      }
    };
    
    return (
        <Layout>
          <Header className="app-header">
            <span className="app-header-title">Digit Recognition</span>
            <UserMenu />
          </Header>
          
          <div  style={{ position: 'relative', left: '46%' }}>
            <FileUpload
              fileList={fileList}
              setFileList={setFileList}
              maxCount={1}
            />
          </div>

          <div style={{ marginTop: 8 }}>
            <Button type='primary' onClick={handleSubmit}>
              Submit
            </Button>
          </div>
          <div><span>The digit in the image is: {resultResp.data}</span></div>

          <div style={{ textAlign: 'center', marginTop: 16 }}>
              <Link to="/user/register">Return to start page</Link>
          </div>
        </Layout>
    )
}

export default ImageProcesser;