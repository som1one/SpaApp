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
import { useAuth } from '../context/AuthContext';
import dayjs from '../utils/dayjs';
import { useEffect, useMemo, useState } from 'react';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { fetchUsers } from '../api/users';
import { fetchBookings } from '../api/bookings';
import { useDebounce } from '../hooks/useDebounce';
import { adjustUserLoyalty, getUserByCode } from '../api/loyalty';

const UsersPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Доступ к управлению пользователями есть только у супер-администраторов.
        </Typography.Text>
      </Card>
    );
  }
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
  const [adjustModalOpen, setAdjustModalOpen] = useState(false);
  const [adjustLoading, setAdjustLoading] = useState(false);
  const [adjustForm] = Form.useForm();
  const [codeSearchModalOpen, setCodeSearchModalOpen] = useState(false);
  const [codeSearchLoading, setCodeSearchLoading] = useState(false);
  const [codeSearchForm] = Form.useForm();
  const [codeSearchResult, setCodeSearchResult] = useState(null);
  const watchedServices = Form.useWatch('services', codeSearchForm) || [];
  // Расчет бонусов для начисления: сумма услуг * процент кэшбэка уровня
  const servicesTotal = watchedServices
    .filter((service) => service?.service_name && service?.price_rub)
    .reduce((sum, service) => sum + Number(service.price_rub || 0), 0);
  const cashbackPercent = codeSearchResult?.cashback_percent || 3;
  const bonusesToAward = Math.floor(servicesTotal * cashbackPercent / 100);

  const loadUserBookings = async (userId) => {
    try {
      setUserBookingsLoading(true);
      const response = await fetchBookings({ userId, pageSize: 5 });
      setUserBookings(response.items);
    } catch (error) {
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

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Автоматически загружаем при изменении debouncedSearch
  useEffect(() => {
    if (debouncedSearch !== search) {
      setPagination((prev) => ({ ...prev, current: 1 }));
      load({ search: debouncedSearch, page: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch]);

  const handleCodeSearch = async (values) => {
    try {
      setCodeSearchLoading(true);
      setCodeSearchResult(null);
      const user = await getUserByCode(values.code.toUpperCase());
      setCodeSearchResult(user);
      message.success('Пользователь найден');
    } catch (error) {
      message.error(error.response?.data?.detail || 'Пользователь не найден');
      setCodeSearchResult(null);
    } finally {
      setCodeSearchLoading(false);
    }
  };

  const handleSpendBonusesByCode = async (values) => {
    if (!codeSearchResult) {
      message.error('Сначала найдите пользователя по коду');
      return;
    }
    
    try {
      setAdjustLoading(true);
      const services = (values.services || []).filter(
        (service) => service?.service_name && service?.price_rub,
      );
      const availableBonuses = codeSearchResult.loyalty_bonuses || 0;

      const payload = {};
      const messages = [];

      // 1. Начисление бонусов за услуги
      if (services.length > 0) {
        const normalizedServices = services.map((service) => ({
          name: service.service_name.trim(),
          price_rub: Math.round(Number(service.price_rub)),
        }));
        const totalCost = normalizedServices.reduce((sum, service) => sum + service.price_rub, 0);

        if (totalCost <= 0) {
          message.error('Стоимость услуг должна быть больше нуля');
          return;
        }

        payload.services = normalizedServices;
        const cashbackPercent = codeSearchResult.cashback_percent || 3;
        const bonusesToAward = Math.floor(totalCost * cashbackPercent / 100);
        messages.push(`Начислено ${bonusesToAward} бонусов (${cashbackPercent}% от ${totalCost} ₽)`);
      }

      // 2. Списание бонусов (скидка)
      if (values.bonuses_delta !== undefined && values.bonuses_delta !== null && values.bonuses_delta !== '') {
        const bonusesToSpend = parseInt(values.bonuses_delta, 10);
        if (isNaN(bonusesToSpend) || bonusesToSpend <= 0) {
          message.error('Количество бонусов для списания должно быть больше нуля');
          return;
        }

        if (bonusesToSpend > availableBonuses) {
          message.error(`Недостаточно бонусов. Доступно ${availableBonuses}, требуется ${bonusesToSpend}`);
          return;
        }

        payload.bonuses_delta = -bonusesToSpend;
        messages.push(`Списано ${bonusesToSpend} бонусов (скидка)`);
      }

      if (!payload.services && !payload.bonuses_delta) {
        message.error('Укажите услуги для начисления бонусов или количество бонусов для списания');
        return;
      }

      payload.reason = values.reason || (messages.length > 0 ? messages.join(' | ') : undefined);

      const result = await adjustUserLoyalty(codeSearchResult.id, payload);
      
      const successMessages = [];
      if (result.bonuses_awarded > 0) {
        successMessages.push(`Начислено ${result.bonuses_awarded} бонусов`);
      }
      if (result.bonuses_spent > 0) {
        successMessages.push(`Списано ${result.bonuses_spent} бонусов`);
      }
      message.success(successMessages.join(' | '));
      
      setCodeSearchModalOpen(false);
      codeSearchForm.resetFields();
      setCodeSearchResult(null);
      // Обновляем данные пользователя
      const updatedUser = await getUserByCode(codeSearchResult.unique_code);
      setCodeSearchResult(updatedUser);
    } catch (error) {
      message.error(error.response?.data?.detail || 'Ошибка при изменении бонусов');
    } finally {
      setAdjustLoading(false);
    }
  };

  const columns = useMemo(() => [
    {
      title: 'Код',
      dataIndex: 'unique_code',
      width: 100,
      render: (code) => code ? <Tag color="blue">{code}</Tag> : '—',
    },
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
      render: (value) => (typeof value === 'number' ? `${value} баллов` : '—'),
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
  ], [filters]);

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
    loadUserBookings(record.id);
  };

  const closeUserDrawer = () => {
    setSelectedUser(null);
    setUserBookings([]);
    setAdjustModalOpen(false);
  };

  return (
    <Card title="Пользователи">
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
            { value: 1, label: '1 и выше' },
            { value: 2, label: '2 и выше' },
            { value: 3, label: '3 и выше (VIP)' },
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
              {selectedUser.unique_code && (
                <Descriptions.Item label="Уникальный код">
                  <Tag color="blue">{selectedUser.unique_code}</Tag>
                </Descriptions.Item>
              )}
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

            <Space direction="vertical" style={{ marginTop: 16, width: '100%' }}>
              <Button type="primary" onClick={() => setAdjustModalOpen(true)} block>
                Скорректировать баллы лояльности
              </Button>
              <Button 
                type="default" 
                onClick={() => setCodeSearchModalOpen(true)} 
                block
                style={{ borderColor: '#1890ff', color: '#1890ff' }}
              >
                Списать бонусы по коду из профиля
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
              const payload = {
                bonuses_delta: values.bonuses_delta,
                reason: values.reason || null,
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
            rules={[{ required: true, message: 'Укажите изменение бонусов (можно отрицательное)' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="Например, 50 или -20"
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

      {/* Модальное окно для поиска по коду и списания бонусов */}
      <Modal
        title="Списать бонусы по коду пользователя"
        open={codeSearchModalOpen}
        onCancel={() => {
          setCodeSearchModalOpen(false);
          codeSearchForm.resetFields();
          setCodeSearchResult(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={codeSearchForm}
          layout="vertical"
          onFinish={codeSearchResult ? handleSpendBonusesByCode : handleCodeSearch}
        >
          {!codeSearchResult ? (
            <>
              <Form.Item
                name="code"
                label="Уникальный код пользователя"
                rules={[{ required: true, message: 'Введите код из профиля пользователя' }]}
                extra="Код можно найти в профиле пользователя в приложении"
              >
                <Input
                  placeholder="Например: ABC12345"
                  style={{ textTransform: 'uppercase' }}
                  onInput={(e) => {
                    e.target.value = e.target.value.toUpperCase();
                  }}
                  size="large"
                />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={codeSearchLoading} block size="large">
                  Найти пользователя
                </Button>
              </Form.Item>
            </>
          ) : (
            <>
              <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f5f5f5' }}>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="Имя">
                    {codeSearchResult.name} {codeSearchResult.surname || ''}
                  </Descriptions.Item>
                  <Descriptions.Item label="Email">{codeSearchResult.email}</Descriptions.Item>
                  <Descriptions.Item label="Код">
                    <Tag color="blue">{codeSearchResult.unique_code}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="Текущие бонусы">
                    <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                      {codeSearchResult.loyalty_bonuses || 0} бонусов
                    </span>
                  </Descriptions.Item>
                </Descriptions>
              </Card>
              <Form.Item
                name="bonuses_delta"
                label="Количество бонусов для списания"
                extra="Это скидка, которую получает пользователь. Можно оставить пустым, если нужно только начислить бонусы за услуги."
                rules={[
                  {
                    validator: (_, value) => {
                      if (!value) {
                        return Promise.resolve();
                      }
                      if (value <= 0) {
                        return Promise.reject(new Error('Минимум 1 бонус'));
                      }
                      return Promise.resolve();
                    },
                  },
                ]}
              >
                <InputNumber
                  min={1}
                  max={codeSearchResult.loyalty_bonuses || 0}
                  style={{ width: '100%' }}
                  placeholder="Сколько бонусов списать (скидка)?"
                  size="large"
                />
              </Form.Item>
              <Form.List name="services">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field, index) => (
                      <Space
                        key={field.key}
                        align="baseline"
                        style={{ width: '100%', marginBottom: 8 }}
                      >
                        <Form.Item
                          {...field}
                          label={index === 0 ? 'Услуга' : ''}
                          name={[field.name, 'service_name']}
                          fieldKey={[field.fieldKey, 'service_name']}
                          rules={[{ required: true, message: 'Введите название услуги' }]}
                          style={{ flex: 1 }}
                        >
                          <Input placeholder="Например, Массаж спины" />
                        </Form.Item>
                        <Form.Item
                          {...field}
                          label={index === 0 ? 'Стоимость, ₽' : ''}
                          name={[field.name, 'price_rub']}
                          fieldKey={[field.fieldKey, 'price_rub']}
                          rules={[{ required: true, message: 'Укажите стоимость' }]}
                        >
                          <InputNumber
                            min={1}
                            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
                            parser={(value) => value.replace(/\s/g, '')}
                            style={{ width: 140 }}
                          />
                        </Form.Item>
                        <Button
                          type="text"
                          danger
                          icon={<MinusCircleOutlined />}
                          onClick={() => remove(field.name)}
                        />
                      </Space>
                    ))}
                    <Button
                      type="dashed"
                      onClick={() => add()}
                      block
                      icon={<PlusOutlined />}
                      style={{ marginBottom: 8 }}
                    >
                      Добавить услугу для начисления бонусов
                    </Button>
                    {fields.length > 0 && (
                      <Typography.Text type="secondary">
                        Бонусы будут начислены автоматически по проценту уровня пользователя ({cashbackPercent}%).
                        Поле «Количество бонусов для списания» можно не заполнять, если нужно только начислить.
                      </Typography.Text>
                    )}
                  </>
                )}
              </Form.List>
              {servicesTotal > 0 && (
                <Typography.Text strong style={{ display: 'block', marginTop: 8, fontSize: '16px', color: '#1890ff' }}>
                  Итого будет начислено: {bonusesToAward.toLocaleString('ru-RU')} бонусов ({cashbackPercent}% от {servicesTotal.toLocaleString('ru-RU')} ₽)
                </Typography.Text>
              )}
              <Form.Item name="reason" label="Причина (опционально)">
                <Input.TextArea rows={3} placeholder="Например: Скидка на услугу массажа" />
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button
                    onClick={() => {
                      setCodeSearchResult(null);
                      codeSearchForm.resetFields(['bonuses_delta', 'reason', 'services']);
                    }}
                  >
                    Найти другого пользователя
                  </Button>
                  <Button type="primary" htmlType="submit" loading={adjustLoading} block>
                    {servicesTotal > 0 || codeSearchForm.getFieldValue('bonuses_delta') 
                      ? 'Применить изменения' 
                      : 'Списать бонусы'}
                  </Button>
                </Space>
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </Card>
  );
};

export default UsersPage;

