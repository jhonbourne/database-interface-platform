import { useState } from 'react';
import { Button, Form, Input, Alert } from "antd";
import { useNavigate } from 'react-router-dom';
import {URLS} from '../utils/request_urls';
import { requestSettings } from '../utils/request_settings';

function Register() {
    const [submittedValues, setSubmittedValues] = useState(null);
    const [feedbackMessage, setFeedbackMessage] = useState(null);
    const registerUrl = URLS['Register'];
    const navigate = useNavigate();

    // called when the form is successfully submitted
    const handleFinish = (values) => {
        // update state (or call other functions here)
        setSubmittedValues(values);
        // Send registration request
        const settings = { ...requestSettings, method: 'POST', body: JSON.stringify(values) };
        fetch(registerUrl, settings)
          .then(async response => {
            if (!response.ok) {
              const msg = await response.json().catch(() => null);
              const text = (msg && (msg.status || msg.message)) || `HTTP ${response.status}`;
              throw new Error(text);
            }
            return response.json();
          })
          .then(() => {
            // successful registration -> go to login
            setFeedbackMessage(null);
            navigate('/user/login');
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
    <header className="Register-header">
        <h1>User Register</h1>
    </header>
    <Form
      name="register"
      onFinish={handleFinish}
      onFinishFailed={handleFinishFailed}
      labelCol={{ span: 8 }}
      wrapperCol={{ span: 16 }}
      style={{ maxWidth: 600, margin: "0 auto", marginTop: "50px" }}
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
            Register
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

    </>
  );
}

export default Register;