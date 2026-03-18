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
  Typography,
  message,
} from 'antd';
import dayjs from '../utils/dayjs';
import { useCallback, useEffect, useState } from 'react';
import {
  createNotification,
  fetchNotifications,
  updateNotificationStatus,
} from '../api/notifications';
import { useAuth } from '../context/useAuth';

const statusColors = {
  draft: 'default',
  scheduled: 'gold',
  sent: 'green',
  cancelled: 'red',
};

const statusLabels = {
  draft: 'Черновик',
  scheduled: 'Запланировано',
  sent: 'Отправлено',
  cancelled: 'Отменено',
};

const categoryOptions = [
  { value: 'general', label: 'Общее' },
  { value: 'promo', label: 'Промо' },
  { value: 'bookings', label: 'Записи' },
  { value: 'loyalty', label: 'Лояльность' },
  { value: 'news', label: 'Новости' },
  { value: 'system', label: 'Системное' },
];

const NotificationsPage = () => {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === 'super_admin';
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: undefined, category: undefined });
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [modalOpen, setModalOpen] = useState(false);

  const load = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      const response = await fetchNotifications({
        status: params.status ?? filters.status,
        category: params.category ?? filters.category,
        page: params.page ?? pagination.current,
        pageSize: params.pageSize ?? pagination.pageSize,
      });
      setData(response.items);
      setTotal(response.total);
    } catch {
      message.error('Не удалось загрузить кампании');
    } finally {
      setLoading(false);
    }
  }, [filters.status, filters.category, pagination]);

  useEffect(() => {
    if (!isSuperAdmin) {
      setLoading(false);
      return;
    }
    load();
  }, [isSuperAdmin, load]);

  const handleStatusChange = async (record, status) => {
    try {
      await updateNotificationStatus(record.id, status);
      message.success('Статус обновлён');
      load();
    } catch {
      message.error('Не удалось обновить статус');
    }
  };

  const columns = [
    {
      title: 'Название',
      dataIndex: 'title',
    },
    {
      title: 'Категория',
      dataIndex: 'category',
      render: (value) => categoryOptions.find((item) => item.value === value)?.label || 'Общее',
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
      render: (value) => (value ? dayjs(value).tz('Asia/Kamchatka').format('DD MMM YYYY HH:mm') : '—'),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      render: (value) => (
        <Tag color={statusColors[value] || 'default'}>{statusLabels[value] || value}</Tag>
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
    const nextFilters = { ...filters, status: value };
    setFilters(nextFilters);
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({ ...nextFilters, page: 1 });
  };

  const handleCategoryFilter = (value) => {
    const nextFilters = { ...filters, category: value };
    setFilters(nextFilters);
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({ ...nextFilters, page: 1 });
  };

  const handleCreate = async (values) => {
    try {
      const scheduledAt = values.scheduled_at
        ? dayjs(values.scheduled_at).tz('Asia/Kamchatka', true).toISOString()
        : null;
      await createNotification({
        title: values.title,
        message: values.message,
        category: values.category,
        channel: values.channel,
        audience: values.audience,
        scheduled_at: scheduledAt,
      });
      message.success('Кампания создана');
      setModalOpen(false);
      load();
    } catch {
      message.error('Не удалось создать кампанию');
    }
  };

  if (!isSuperAdmin) {
    return (
      <Card>
        <Typography.Text>
          Управлять рассылками и уведомлениями могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }

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
        <Select
          allowClear
          placeholder="Категория"
          onChange={handleCategoryFilter}
          options={categoryOptions}
          style={{ width: 220 }}
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
          <Form.Item label="Категория" name="category" initialValue="general">
            <Select options={categoryOptions} />
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
          <Form.Item
            label="Запланировать на (Камчатка, UTC+12)"
            name="scheduled_at"
            extra="Время интерпретируется по часовому поясу Камчатки."
          >
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
