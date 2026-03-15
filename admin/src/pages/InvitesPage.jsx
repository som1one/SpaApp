import {
  Button,
  Card,
  Form,
  Input,
  Select,
  Table,
  Tag,
  message,
  Typography,
} from 'antd';
import {
  CopyOutlined,
  ReloadOutlined,
  UserAddOutlined,
} from '@ant-design/icons';
import { useCallback, useEffect, useMemo, useState } from 'react';
import dayjs from '../utils/dayjs';
import { createInvite, fetchInvites } from '../api/invites';
import { useAuth } from '../context/AuthContext';

// В Ant Design v5 нет отдельного экспорта InputGroup,
// используем дочерний компонент Input.Group
const InputGroup = Input.Group;

const { Text } = Typography;

const statusTag = (status) => {
  const map = {
    active: 'green',
    expired: 'default',
    accepted: 'blue',
  };
  const label = {
    active: 'Активно',
    expired: 'Истекло',
    accepted: 'Принято',
  };
  return <Tag color={map[status] ?? 'default'}>{label[status] ?? status}</Tag>;
};

const buildInviteLink = (token) => `${window.location.origin}/invite/${token}`;

const InvitesPage = () => {
  const { user } = useAuth();
  const [form] = Form.useForm();
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const loadInvites = async () => {
    try {
      setLoading(true);
      const data = await fetchInvites();
      setInvites(data);
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось загрузить приглашения');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInvites();
  }, []);

  const onFinish = async (values) => {
    try {
      setCreating(true);
      const invite = await createInvite(values);
      const inviteLink = buildInviteLink(invite.token);
      message.success({
        content: (
          <div>
            <div>Приглашение отправлено на {invite.email}</div>
            <div style={{ marginTop: 8 }}>
              <Text copyable={{ text: inviteLink }} style={{ fontSize: 12 }}>
                Ссылка: {inviteLink}
              </Text>
            </div>
          </div>
        ),
        duration: 10,
      });
      form.resetFields();
      setInvites((prev) => [invite, ...prev.filter((item) => item.email !== invite.email)]);
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось создать приглашение');
    } finally {
      setCreating(false);
    }
  };

  const handleCopy = useCallback(async (token) => {
    const link = buildInviteLink(token);
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(link);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = link;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }
      message.success('Ссылка скопирована');
    } catch (error) {
      message.error('Не удалось скопировать ссылку');
    }
  }, []);

  const columns = useMemo(() => [
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      render: (role) => (role === 'super_admin' ? 'Супер-админ' : 'Админ'),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: statusTag,
    },
    {
      title: 'Истекает',
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (date) => date ? dayjs(date).tz('Europe/Moscow').format('DD MMM HH:mm') : '—',
    },
    {
      title: 'Ссылка приглашения',
      key: 'token',
      width: 300,
      render: (_, record) => {
        const link = buildInviteLink(record.token);
        return (
          <InputGroup compact>
            <Input
              value={link}
              readOnly
              style={{ width: 'calc(100% - 40px)', fontSize: 12 }}
            />
            <Button
              icon={<CopyOutlined />}
              onClick={() => handleCopy(record.token)}
              title="Копировать ссылку"
            />
          </InputGroup>
        );
      },
    },
  ], [handleCopy]);

  if (user?.role !== 'super_admin') {
    return (
      <Card className="invites-card">
        <p>Только супер-администраторы могут управлять приглашениями.</p>
      </Card>
    );
  }

  return (
    <div className="invites-page">
      <Card
        title="Пригласить администратора"
        className="invites-card"
        extra={(
          <Button
            icon={<ReloadOutlined />}
            type="text"
            onClick={loadInvites}
          >
            Обновить список
          </Button>
        )}
      >
        <Form
          layout="vertical"
          form={form}
          onFinish={onFinish}
          initialValues={{ role: 'admin' }}
          requiredMark={false}
        >
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: 'Введите email' },
              { type: 'email', message: 'Некорректный email' },
            ]}
          >
            <Input placeholder="admin@company.com" />
          </Form.Item>
          <Form.Item
            label="Роль"
            name="role"
            rules={[{ required: true, message: 'Выберите роль' }]}
          >
            <Select
              options={[
                { value: 'admin', label: 'Администратор' },
                { value: 'super_admin', label: 'Супер-администратор' },
              ]}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<UserAddOutlined />}
              loading={creating}
            >
              Отправить приглашение
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title="Текущие приглашения" className="invites-card">
        <Table
          rowKey="token"
          dataSource={invites}
          columns={columns}
          loading={loading}
          pagination={false}
          locale={{
            emptyText: 'Пока нет приглашений',
          }}
        />
      </Card>
    </div>
  );
};

export default InvitesPage;


