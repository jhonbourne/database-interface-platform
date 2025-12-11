import { useState } from 'react';
import { Button, Form, Input, Alert } from "antd";
import { useNavigate, Link } from 'react-router-dom';
import {URLS} from '../utils/request_urls';
import { requestSettings } from '../utils/request_settings';

function Login() {
    const [submittedValues, setSubmittedValues] = useState(null);
    const [feedbackMessage, setFeedbackMessage] = useState(null);
    const loginUrl = URLS['Login'];
    const navigate = useNavigate();

    // called when the form is successfully submitted
    const handleFinish = (values) => {
        // update state (or call other functions here)
        setSubmittedValues(values);
        // Send registration request
        const settings = { ...requestSettings, method: 'POST', 
            body: JSON.stringify(values) };
        fetch(loginUrl, settings)
        .then(async response => {
          if (!response.ok) {
            const msg = await response.json().catch(() => null);
            const text = (msg && (msg.status || msg.message)) || `HTTP ${response.status}`;
            throw new Error(text);
          }
          return response.json();
        })
        .then(() => {
          // successful registration -> go to display board
          setFeedbackMessage(null);
          navigate('/start');
        })
        .catch(error => {
          setFeedbackMessage(error.toString());
        });
        
    };

    // called when form submit fails validation
    const handleFinishFailed = (errorInfo) => {
        console.log('Submit failed:', errorInfo);
    };

  return (
    <>
    <header className="Login-header">
        <h1>User Login</h1>
    </header>
    <Form
      name="login"
      onFinish={handleFinish}
      onFinishFailed={handleFinishFailed}
      labelCol={{ span: 8 }}
      wrapperCol={{ span: 16 }}
      style={{ maxWidth: 600, margin: "0 auto", marginTop: "50px",
        textAlign: 'center'
       }}
      initialValues={{ remember: true }}
      autoComplete="off"
    >
      <Form.Item
        label="Username"
        name="username"
        rules={[{ required: true, message: "Please input your username!" }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="Password"
        name="password"
        rules={[{ required: true, message: "Please input your password!" }]}
      >
        <Input.Password />
      </Form.Item>

      <Form.Item
        label={null}
      >
        <Button type="primary" htmlType="submit">
            Login
        </Button>
      </Form.Item>

    </Form>

    {feedbackMessage && (
      <Alert
        message={feedbackMessage}
        type="error"
        closable
        onClose={() => setFeedbackMessage(null)}
        style={{ maxWidth: 600, margin: '16px auto' }}
      />
    )}
    
    <div style={{ textAlign: 'center', marginTop: '16px' }}>
        <span>Don't have an account? </span>
        <Link to="/user/register">Register here</Link>
    </div>
    </>
  );
}

export default Login;