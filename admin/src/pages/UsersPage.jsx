import {
  Button,
  Card,
  Descriptions,
  Drawer,
  Empty,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Skeleton,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import { useAuth } from '../context/useAuth';
import dayjs from '../utils/dayjs';
import { useEffect, useMemo, useState } from 'react';
import { exportUsersExcel, fetchUserYclientsSnapshot, fetchUsers } from '../api/users';
import { fetchBookings } from '../api/bookings';
import { useDebounce } from '../hooks/useDebounce';
import { adjustUserLoyalty } from '../api/loyalty';

const UsersPage = () => {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 500);
  const [filters, setFilters] = useState({ isActive: undefined, isVerified: undefined, minLoyalty: undefined });
  const [sort, setSort] = useState({ sortBy: 'created_at', sortDir: 'desc' });
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [selectedUser, setSelectedUser] = useState(null);
  const [userBookings, setUserBookings] = useState([]);
  const [userBookingsLoading, setUserBookingsLoading] = useState(false);
  const [yclientsData, setYclientsData] = useState(null);
  const [yclientsLoading, setYclientsLoading] = useState(false);
  const [adjustModalOpen, setAdjustModalOpen] = useState(false);
  const [adjustLoading, setAdjustLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [adjustForm] = Form.useForm();
  const isSuperAdmin = user?.role === 'super_admin';

  const loadUserBookings = async (userId) => {
    try {
      setUserBookingsLoading(true);
      const response = await fetchBookings({ userId, pageSize: 5 });
      setUserBookings(response.items);
    } catch {
      message.error('Не удалось загрузить записи пользователя');
    } finally {
      setUserBookingsLoading(false);
    }
  };

  const load = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchUsers({
        search: params.search ?? debouncedSearch,
        isActive: params.isActive ?? filters.isActive,
        isVerified: params.isVerified ?? filters.isVerified,
        minLoyalty: params.minLoyalty ?? filters.minLoyalty,
        sortBy: params.sortBy ?? sort.sortBy,
        sortDir: params.sortDir ?? sort.sortDir,
        page: params.page ?? pagination.current,
        pageSize: params.pageSize ?? pagination.pageSize,
      });
      setData(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
      const errorMessage = error.message || 'Не удалось загрузить пользователей';
      setError(errorMessage);
      message.error(errorMessage, 5);
      // Устанавливаем пустые данные при ошибке, чтобы не показывать бесконечную загрузку
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setExportLoading(true);
      const blob = await exportUsersExcel({
        search: debouncedSearch,
        isActive: filters.isActive,
        isVerified: filters.isVerified,
        minLoyalty: filters.minLoyalty,
        sortBy: sort.sortBy,
        sortDir: sort.sortDir,
      });
      const fileUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = `users_export_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(fileUrl);
      message.success('Файл выгрузки сформирован');
    } catch (error) {
      message.error(error?.response?.data?.detail || 'Не удалось выгрузить пользователей');
    } finally {
      setExportLoading(false);
    }
  };

  useEffect(() => {
    if (!isSuperAdmin) {
      setLoading(false);
      return;
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSuperAdmin]);

  // Автоматически загружаем при изменении debouncedSearch
  useEffect(() => {
    if (debouncedSearch !== search) {
      setPagination((prev) => ({ ...prev, current: 1 }));
      load({ search: debouncedSearch, page: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch]);

  const columns = useMemo(() => [
    {
      title: 'Имя',
      dataIndex: 'name',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <span>
            {record.name}
            {' '}
            {record.surname}
          </span>
          <small style={{ color: '#6A6F7A' }}>{record.email}</small>
        </Space>
      ),
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
      render: (value) => value || '—',
    },
    {
      title: 'Лояльность',
      dataIndex: 'loyalty_level',
      render: (value) => (typeof value === 'number' ? `Уровень ${value}` : '—'),
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      render: (value, record) => (
        <Space>
          <Tag color={value ? 'green' : 'default'}>
            {value ? 'Активен' : 'Неактивен'}
          </Tag>
          {record.is_verified && <Tag color="blue">Почта подтверждена</Tag>}
        </Space>
      ),
    },
    {
      title: 'Создан',
      dataIndex: 'created_at',
      sorter: true,
      render: (value) => value ? dayjs(value).tz('Europe/Moscow').format('DD.MM.YYYY') : '—',
    },
  ], []);

  const handleTableChange = (paginationConfig, _filters, sorter) => {
    const { current, pageSize } = paginationConfig;
    const sortBy = sorter.field === 'loyalty_level' ? 'loyalty_level' : 'created_at';
    const sortDir = sorter.order === 'ascend' ? 'asc' : 'desc';
    setPagination({ current, pageSize });
    setSort({ sortBy, sortDir });
    load({ page: current, pageSize, sortBy, sortDir });
  };

  const handleSearch = (value) => {
    setSearch(value);
    // Загрузка произойдёт автоматически через useEffect при изменении debouncedSearch
  };

  const handleFilterChange = (key, value) => {
    const nextFilters = { ...filters, [key]: value };
    setFilters(nextFilters);
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({ ...nextFilters, page: 1 });
  };

  const openUserDrawer = (record) => {
    setSelectedUser(record);
    setYclientsData(null);
    loadUserBookings(record.id);
    (async () => {
      try {
        setYclientsLoading(true);
        const response = await fetchUserYclientsSnapshot(record.id);
        setYclientsData(response);
      } catch {
        setYclientsData({ found: false, message: 'Не удалось загрузить данные YClients' });
      } finally {
        setYclientsLoading(false);
      }
    })();
  };

  const closeUserDrawer = () => {
    setSelectedUser(null);
    setUserBookings([]);
    setYclientsData(null);
    setAdjustModalOpen(false);
  };

  if (!isSuperAdmin) {
    return (
      <Card>
        <Typography.Text>
          Доступ к управлению пользователями есть только у супер-администраторов.
        </Typography.Text>
      </Card>
    );
  }

  return (
    <Card
      title="Пользователи"
      extra={(
        <Button onClick={handleExport} loading={exportLoading}>
          Выгрузить в Excel
        </Button>
      )}
    >
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search
          allowClear
          placeholder="Поиск по имени или email"
          onSearch={handleSearch}
          style={{ width: 260 }}
        />
        <Select
          allowClear
          placeholder="Статус"
          style={{ width: 160 }}
          onChange={(value) => handleFilterChange('isActive', value)}
          options={[
            { value: true, label: 'Активные' },
            { value: false, label: 'Неактивные' },
          ]}
        />
        <Select
          allowClear
          placeholder="Подтверждение почты"
          style={{ width: 200 }}
          onChange={(value) => handleFilterChange('isVerified', value)}
          options={[
            { value: true, label: 'Подтверждена' },
            { value: false, label: 'Не подтверждена' },
          ]}
        />
        <Select
          allowClear
          placeholder="Мин. уровень лояльности"
          style={{ width: 220 }}
          onChange={(value) => handleFilterChange('minLoyalty', value)}
          options={[
            { value: 0, label: '0 и выше' },
            { value: 1, label: '1 и выше' },
            { value: 2, label: '2 и выше' },
            { value: 3, label: '3 и выше' },
            { value: 4, label: '4 и выше' },
          ]}
        />
      </Space>
      {error && !loading ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <div>
              <div style={{ marginBottom: 16, color: '#ff4d4f' }}>{error}</div>
              <Button type="primary" onClick={() => load()}>
                Повторить попытку
              </Button>
            </div>
          }
        />
      ) : loading && data.length === 0 ? (
        <Skeleton active paragraph={{ rows: 8 }} />
      ) : (
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
          onRow={(record) => ({
            onClick: () => openUserDrawer(record),
            style: { cursor: 'pointer' },
          })}
        />
      )}

      <Drawer
        title={selectedUser ? `${selectedUser.name} ${selectedUser.surname ?? ''}` : ''}
        width={520}
        open={!!selectedUser}
        onClose={closeUserDrawer}
      >
        {selectedUser && (
          <>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Email">{selectedUser.email}</Descriptions.Item>
              <Descriptions.Item label="Телефон">{selectedUser.phone || '—'}</Descriptions.Item>
              <Descriptions.Item label="Бонусы">
                {selectedUser.loyalty_bonuses !== null && selectedUser.loyalty_bonuses !== undefined
                  ? `${selectedUser.loyalty_bonuses} бонусов`
                  : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Потрачено бонусов">
                {selectedUser.spent_bonuses !== null && selectedUser.spent_bonuses !== undefined
                  ? `${selectedUser.spent_bonuses} бонусов`
                  : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Уровень лояльности">
                {typeof selectedUser.loyalty_level === 'number'
                  ? `Уровень ${selectedUser.loyalty_level}`
                  : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Space>
                  <Tag color={selectedUser.is_active ? 'green' : 'default'}>
                    {selectedUser.is_active ? 'Активен' : 'Неактивен'}
                  </Tag>
                  {selectedUser.is_verified && <Tag color="blue">Почта подтверждена</Tag>}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Создан">
                {dayjs(selectedUser.created_at).tz('Europe/Moscow').format('DD.MM.YYYY HH:mm')}
              </Descriptions.Item>
            </Descriptions>

            <Typography.Title level={5} style={{ marginTop: 24 }}>
              YClients
            </Typography.Title>
            {yclientsLoading ? (
              <Skeleton active paragraph={{ rows: 4 }} title={false} />
            ) : (
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Телефон в YClients">
                  {yclientsData?.found ? (yclientsData.phone || '—') : '—'}
                </Descriptions.Item>
                <Descriptions.Item label="Потрачено в YClients">
                  {yclientsData?.found && yclientsData.spent !== null && yclientsData.spent !== undefined
                    ? `${yclientsData.spent}`
                    : '—'}
                </Descriptions.Item>
                <Descriptions.Item label="Баланс в YClients">
                  {yclientsData?.found && yclientsData.balance !== null && yclientsData.balance !== undefined
                    ? `${yclientsData.balance}`
                    : '—'}
                </Descriptions.Item>
                <Descriptions.Item label="Уровень лояльности в YClients">
                  {yclientsData?.found
                    ? (yclientsData.loyalty_level_title || '—')
                    : '—'}
                </Descriptions.Item>
                {!yclientsLoading && yclientsData?.message && (
                  <Descriptions.Item label="Статус YClients">
                    <Tag color={yclientsData.found ? 'green' : 'default'}>
                      {yclientsData.message}
                    </Tag>
                  </Descriptions.Item>
                )}
              </Descriptions>
            )}

            <Space direction="vertical" style={{ marginTop: 16, width: '100%' }}>
              <Button type="primary" onClick={() => setAdjustModalOpen(true)} block>
                Скорректировать баллы лояльности
              </Button>
            </Space>

            <Typography.Title level={5} style={{ marginTop: 24 }}>
              Последние записи
            </Typography.Title>
            <Table
              size="small"
              rowKey="id"
              loading={userBookingsLoading}
              dataSource={userBookings}
              pagination={false}
              columns={[
                {
                  title: 'Услуга',
                  dataIndex: 'service_name',
                },
                {
                  title: 'Дата',
                  dataIndex: 'appointment_datetime',
                  render: (value) => value ? dayjs(value).tz('Europe/Moscow').format('DD MMM HH:mm') : '—',
                },
                {
                  title: 'Статус',
                  dataIndex: 'status',
                  render: (value) => (
                    <Tag color={value === 'confirmed' ? 'green' : value === 'pending' ? 'gold' : 'default'}>
                      {value}
                    </Tag>
                  ),
                },
              ]}
            />
          </>
        )}
      </Drawer>

      <Modal
        title="Корректировка баллов лояльности"
        open={adjustModalOpen}
        confirmLoading={adjustLoading}
        onCancel={() => {
          setAdjustModalOpen(false);
          adjustForm.resetFields();
        }}
        onOk={() => adjustForm.submit()}
        okText="Сохранить"
      >
        <Form
          layout="vertical"
          form={adjustForm}
          onFinish={async (values) => {
            if (!selectedUser) return;
            try {
              setAdjustLoading(true);
              if ((values.bonuses_delta ?? 0) < 0) {
                message.error('Списание бонусов отключено. Укажите неотрицательное значение.');
                return;
              }
              const payload = {
                bonuses_delta: values.bonuses_delta,
                reason: values.reason || null,
                expires_in_days: values.expires_in_days || null,
              };
              const result = await adjustUserLoyalty(selectedUser.id, payload);
              message.success('Бонусы обновлены');
              setSelectedUser((prev) => (prev
                ? { ...prev, loyalty_bonuses: result.current_bonuses }
                : prev));
              setAdjustModalOpen(false);
              adjustForm.resetFields();
              load();
            } catch (error) {
              message.error(error?.response?.data?.detail ?? 'Не удалось изменить баллы');
            } finally {
              setAdjustLoading(false);
            }
          }}
        >
          <Form.Item
            label="Изменение бонусов"
            name="bonuses_delta"
            rules={[{ required: true, message: 'Укажите количество бонусов для начисления' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              placeholder="Например, 50"
            />
          </Form.Item>
          <Form.Item
            label="Срок действия временных бонусов (дней, необязательно)"
            name="expires_in_days"
            extra="Оставьте пустым, если начисление должно быть бессрочным."
          >
            <InputNumber
              style={{ width: '100%' }}
              min={1}
              placeholder="Например, 30"
            />
          </Form.Item>
          <Form.Item
            label="Комментарий (необязательно)"
            name="reason"
          >
            <Input.TextArea rows={3} placeholder="Причина корректировки, видно только в аудите" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default UsersPage;
