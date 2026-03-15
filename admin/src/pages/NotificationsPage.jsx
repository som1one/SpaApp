import {
  Badge,
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd';
import dayjs from '../utils/dayjs';
import { useEffect, useState } from 'react';
import {
  createNotification,
  fetchNotifications,
  updateNotificationStatus,
} from '../api/notifications';
import { useAuth } from '../context/AuthContext';

const statusColors = {
  draft: 'default',
  scheduled: 'gold',
  sent: 'green',
  cancelled: 'red',
};

const NotificationsPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Управлять рассылками и уведомлениями могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: undefined });
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [modalOpen, setModalOpen] = useState(false);

  const load = async (params = {}) => {
    try {
      setLoading(true);
      const response = await fetchNotifications({
        status: params.status ?? filters.status,
        page: params.page ?? pagination.current,
        pageSize: params.pageSize ?? pagination.pageSize,
      });
      setData(response.items);
      setTotal(response.total);
    } catch (error) {
      message.error('Не удалось загрузить кампании');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleStatusChange = async (record, status) => {
    try {
      await updateNotificationStatus(record.id, status);
      message.success('Статус обновлён');
      load();
    } catch (error) {
      message.error('Не удалось обновить статус');
    }
  };

  const columns = [
    {
      title: 'Название',
      dataIndex: 'title',
    },
    {
      title: 'Канал',
      dataIndex: 'channel',
      render: (value) => value.toUpperCase(),
    },
    {
      title: 'Аудитория',
      dataIndex: 'audience',
      render: (value) => value || 'Все',
    },
    {
      title: 'Запланировано',
      dataIndex: 'scheduled_at',
      render: (value) => (value ? dayjs(value).tz('Europe/Moscow').format('DD MMM HH:mm') : '—'),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      render: (value) => (
        <Tag color={statusColors[value] || 'default'}>{value}</Tag>
      ),
    },
    {
      title: 'Результат',
      render: (_, record) => (
        <Space size="small">
          <Badge status="success" text={record.success_count ?? 0} />
          <Badge status="error" text={record.failure_count ?? 0} />
        </Space>
      ),
    },
    {
      title: 'Действия',
      render: (_, record) => (
        <Space>
          {record.status !== 'sent' && (
            <Button type="link" onClick={() => handleStatusChange(record, 'sent')}>
              Отправить
            </Button>
          )}
          {record.status !== 'cancelled' && record.status !== 'sent' && (
            <Button type="link" danger onClick={() => handleStatusChange(record, 'cancelled')}>
              Отменить
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const handleTableChange = (paginationConfig) => {
    setPagination({ current: paginationConfig.current, pageSize: paginationConfig.pageSize });
    load({ page: paginationConfig.current, pageSize: paginationConfig.pageSize });
  };

  const handleStatusFilter = (value) => {
    setFilters({ status: value });
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({ status: value, page: 1 });
  };

  const handleCreate = async (values) => {
    try {
      await createNotification({
        title: values.title,
        message: values.message,
        channel: values.channel,
        audience: values.audience,
        scheduled_at: values.scheduled_at?.toISOString(),
      });
      message.success('Кампания создана');
      setModalOpen(false);
      load();
    } catch (error) {
      message.error('Не удалось создать кампанию');
    }
  };

  return (
    <Card
      title="Рассылки и уведомления"
      extra={(
        <Button type="primary" onClick={() => setModalOpen(true)}>
          Новая рассылка
        </Button>
      )}
    >
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Статус"
          onChange={handleStatusFilter}
          options={[
            { value: 'draft', label: 'Черновик' },
            { value: 'scheduled', label: 'Запланировано' },
            { value: 'sent', label: 'Отправлено' },
            { value: 'cancelled', label: 'Отменено' },
          ]}
          style={{ width: 200 }}
        />
      </Space>
      <Table
        rowKey="id"
        loading={loading}
        dataSource={data}
        columns={columns}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total,
          showSizeChanger: true,
        }}
        onChange={handleTableChange}
      />

      <Modal
        title="Новая кампания"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleCreate}>
          <Form.Item label="Название" name="title" rules={[{ required: true, message: 'Введите название' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Сообщение" name="message" rules={[{ required: true, message: 'Введите текст' }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item label="Канал" name="channel" initialValue="all">
            <Select
              options={[
                { value: 'all', label: 'Все' },
                { value: 'push', label: 'Push' },
                { value: 'email', label: 'Email' },
              ]}
            />
          </Form.Item>
          <Form.Item label="Аудитория" name="audience">
            <Select
              allowClear
              placeholder="Кого уведомить"
              options={[
                { value: 'all', label: 'Все пользователи' },
                { value: 'vip', label: 'VIP (loyalty_level ≥ 3)' },
              ]}
            />
          </Form.Item>
          <Form.Item label="Запланировать на" name="scheduled_at">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setModalOpen(false)}>Отмена</Button>
              <Button type="primary" htmlType="submit">
                Сохранить
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default NotificationsPage;

