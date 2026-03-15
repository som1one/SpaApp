import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  Result,
  Spin,
  Typography,
  message,
} from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getInviteByToken } from '../api/invites';
import { useAuth } from '../context/AuthContext';

const { Title, Text } = Typography;

const statusMessages = {
  expired: {
    status: 'warning',
    title: 'Срок действия приглашения истёк',
    subtitle: 'Попросите супер-админа отправить новое приглашение.',
  },
  accepted: {
    status: 'success',
    title: 'Приглашение уже активировано',
    subtitle: 'Можете войти, используя установленный пароль.',
  },
};

const AcceptInvitePage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const { completeInvite } = useAuth();
  const [form] = Form.useForm();
  const [invite, setInvite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadInvite = async () => {
      try {
        setLoading(true);
        const data = await getInviteByToken(token);
        setInvite(data);
        setError(null);
      } catch (err) {
        setError(err?.response?.data?.detail ?? 'Приглашение не найдено');
      } finally {
        setLoading(false);
      }
    };
    loadInvite();
  }, [token]);

  const onFinish = async ({ password }) => {
    try {
      setSubmitting(true);
      await completeInvite(token, password);
      message.success('Пароль установлен, добро пожаловать!');
      navigate('/', { replace: true });
    } catch (err) {
      message.error(err?.response?.data?.detail ?? 'Не удалось принять приглашение');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="invite-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Result
        status="error"
        title="Приглашение недоступно"
        subTitle={error}
        extra={(
          <Button type="primary" onClick={() => navigate('/login')}>
            На страницу входа
          </Button>
        )}
      />
    );
  }

  const statusInfo = statusMessages[invite.status];
  const formDisabled = invite.status !== 'active';

  return (
    <div className="accept-invite-page">
      <Card className="accept-invite-card">
        <Title level={3}>Добро пожаловать в PRIRODA SPA Admin</Title>
        <Text type="secondary">
          Вы приглашены как
          {' '}
          <strong>{invite.role === 'super_admin' ? 'супер-администратор' : 'администратор'}</strong>
          .
        </Text>

        <div className="invite-details">
          <div>
            <Text type="secondary">Email:</Text>
            <div>{invite.email}</div>
          </div>
          <div>
            <Text type="secondary">Статус:</Text>
            <div>{invite.status === 'active' ? 'Активно' : statusInfo?.title ?? invite.status}</div>
          </div>
        </div>

        {statusInfo ? (
          <Alert
            style={{ marginBottom: 16 }}
            type={statusInfo.status}
            message={statusInfo.title}
            description={statusInfo.subtitle}
          />
        ) : (
          <Alert
            style={{ marginBottom: 16 }}
            type="info"
            message="Установите пароль для завершения регистрации"
          />
        )}

        <Form
          layout="vertical"
          form={form}
          onFinish={onFinish}
          disabled={formDisabled}
          requiredMark={false}
        >
          <Form.Item
            label="Новый пароль"
            name="password"
            rules={[
              { required: true, message: 'Введите пароль' },
              { min: 8, message: 'Минимум 8 символов' },
            ]}
          >
            <Input.Password placeholder="Введите новый пароль" />
          </Form.Item>
          <Form.Item
            label="Повторите пароль"
            name="confirm"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Повторите пароль' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Пароли не совпадают'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="Повторите пароль" />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={submitting}
            >
              Установить пароль и войти
            </Button>
          </Form.Item>
          <Button type="link" onClick={() => navigate('/login')}>
            Перейти к входу
          </Button>
        </Form>
      </Card>
    </div>
  );
};

export default AcceptInvitePage;


