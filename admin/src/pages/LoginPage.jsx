import { Button, Card, Form, Input, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const { Title, Text } = Typography;

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleFinish = async ({ email, password }) => {
    try {
      setLoading(true);
      await login(email, password);
      navigate('/');
    } catch (error) {
      console.error('Ошибка входа:', error);
      let errorMessage = 'Ошибка входа';
      
      if (error?.message) {
        errorMessage = error.message;
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.response?.status === 401) {
        errorMessage = 'Неверный email или пароль';
      } else if (error?.response?.status === 403) {
        errorMessage = 'Доступ запрещён';
      } else if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
        errorMessage = 'Превышено время ожидания. Проверьте подключение к интернету и убедитесь, что сервер запущен.';
      } else if (!error?.response) {
        errorMessage = 'Не удалось подключиться к серверу. Проверьте подключение к интернету и убедитесь, что сервер запущен.';
      }
      
      message.error(errorMessage, 5);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card className="login-card">
        <Title level={3}>PRIRODA SPA · Admin</Title>
        <Text type="secondary">Войдите в систему, чтобы управлять сервисом</Text>
        <Form layout="vertical" onFinish={handleFinish} style={{ marginTop: 24 }}>
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Некорректный email' },
            ]}
          >
            <Input size="large" placeholder="admin@priroda.spa" />
          </Form.Item>
          <Form.Item
            label="Пароль"
            name="password"
            rules={[{ required: true, message: 'Введите пароль' }]}
          >
            <Input.Password size="large" placeholder="Пароль" />
          </Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            block
            loading={loading}
          >
            Войти
          </Button>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;


