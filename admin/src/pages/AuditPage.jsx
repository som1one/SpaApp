import { Card, Input, Select, Space, Table, Tag, Typography, message } from 'antd';
import dayjs from '../utils/dayjs';
import { useEffect, useState } from 'react';
import { fetchAudit } from '../api/audit';
import { useAuth } from '../context/AuthContext';

const actionLabels = {
  create_category: 'Создание категории',
  update_category: 'Изменение категории',
  delete_category: 'Удаление категории',
  create_service: 'Создание услуги',
  update_service: 'Изменение услуги',
  delete_service: 'Удаление услуги',
  invite_admin: 'Приглашение администратора',
};

const AuditPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Журнал действий доступен только супер-администраторам.
        </Typography.Text>
      </Card>
    );
  }
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ action: undefined, adminId: undefined });
  const [pagination, setPagination] = useState({ current: 1, pageSize: 30 });

  const load = async (params = {}) => {
    try {
      setLoading(true);
      const response = await fetchAudit({
        action: params.action ?? filters.action,
        adminId: params.adminId ?? filters.adminId,
        page: params.page ?? pagination.current,
        pageSize: params.pageSize ?? pagination.pageSize,
      });
      setData(response.items);
      setTotal(response.total);
    } catch (error) {
      message.error('Не удалось загрузить журнал');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const columns = [
    {
      title: 'Дата',
      dataIndex: 'executed_at',
      render: (value) => value ? dayjs(value).tz('Europe/Moscow').format('DD MMM HH:mm') : '—',
    },
    {
      title: 'Админ',
      dataIndex: 'admin_id',
    },
    {
      title: 'Действие',
      dataIndex: 'action',
      render: (value) => <Tag>{actionLabels[value] ?? value}</Tag>,
    },
    {
      title: 'Объект',
      dataIndex: 'entity',
      render: (_, record) => (
        <span>
          {record.entity || '—'}
          {record.entity_id ? ` #${record.entity_id}` : ''}
        </span>
      ),
    },
    {
      title: 'IP / User Agent',
      dataIndex: 'ip_address',
      render: (value, record) => (
        <span>
          {value || '—'}
          <br />
          <small style={{ color: '#6A6F7A' }}>{record.user_agent || ''}</small>
        </span>
      ),
    },
  ];

  const handleTableChange = (paginationConfig) => {
    setPagination({ current: paginationConfig.current, pageSize: paginationConfig.pageSize });
    load({ page: paginationConfig.current, pageSize: paginationConfig.pageSize });
  };

  return (
    <Card title="Журнал действий">
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Тип действия"
          options={Object.entries(actionLabels).map(([value, label]) => ({ value, label }))}
          onChange={(value) => {
            setFilters((prev) => ({ ...prev, action: value }));
            setPagination((prev) => ({ ...prev, current: 1 }));
            load({ action: value, page: 1 });
          }}
          style={{ width: 220 }}
        />
        <Input.Search
          allowClear
          placeholder="ID администратора"
          onSearch={(value) => {
            const parsed = value ? Number(value) : undefined;
            setFilters((prev) => ({ ...prev, adminId: parsed }));
            setPagination((prev) => ({ ...prev, current: 1 }));
            load({ adminId: parsed, page: 1 });
          }}
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
    </Card>
  );
};

export default AuditPage;

