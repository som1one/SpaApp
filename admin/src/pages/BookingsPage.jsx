import {
  Button,
  Card,
  DatePicker,
  Drawer,
  Input,
  InputNumber,
  Popover,
  Select,
  Skeleton,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import dayjs from '../utils/dayjs';
import { useEffect, useMemo, useState } from 'react';
import { fetchBookings, updateBookingStatus, confirmBookingPayment } from '../api/bookings';
import { useDebounce } from '../hooks/useDebounce';

const statusOptions = [
  { label: 'Все', value: undefined },
  { label: 'В ожидании', value: 'pending' },
  { label: 'Подтверждено', value: 'confirmed' },
  { label: 'Завершено', value: 'completed' },
  { label: 'Отменено', value: 'cancelled' },
];

const statusColors = {
  pending: 'gold',
  confirmed: 'green',
  completed: 'blue',
  cancelled: 'red',
};

const formatPrice = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  return (value / 100).toFixed(2);
};

const BookingsPage = ({ defaultStatus } = {}) => {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: defaultStatus, search: '', dateRange: null });
  const debouncedSearch = useDebounce(filters.search, 500);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState(null);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [editingDateTime, setEditingDateTime] = useState(null);
  const [savingDateTime, setSavingDateTime] = useState(false);

  const load = async (params = {}) => {
    try {
      setLoading(true);
      const response = await fetchBookings({
        status: params.status ?? filters.status,
        search: params.search ?? debouncedSearch,
        dateFrom: params.dateFrom ?? (filters.dateRange ? filters.dateRange[0].toISOString() : undefined),
        dateTo: params.dateTo ?? (filters.dateRange ? filters.dateRange[1].toISOString() : undefined),
        page: params.page ?? pagination.current,
        pageSize: params.pageSize ?? pagination.pageSize,
      });
      setData(response.items);
      setTotal(response.total);
      return response;
    } catch (error) {
      message.error('Не удалось загрузить записи');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Применяем defaultStatus при монтировании, если задан
  useEffect(() => {
    if (defaultStatus) {
      setFilters((prev) => ({ ...prev, status: defaultStatus }));
      setPagination((prev) => ({ ...prev, current: 1 }));
      load({ status: defaultStatus, page: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultStatus]);

  // Автоматически загружаем при изменении debouncedSearch
  useEffect(() => {
    if (debouncedSearch !== filters.search) {
      setPagination((prev) => ({ ...prev, current: 1 }));
      load({ search: debouncedSearch, page: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch]);

  const handleStatusChange = async (record, status) => {
    try {
      await updateBookingStatus(record.id, { status });
      message.success('Статус обновлен');
      const response = await load();
      if (selectedBooking?.id === record.id && response) {
        const updatedRecord = response.items.find((item) => item.id === record.id);
        if (updatedRecord) {
          setSelectedBooking(updatedRecord);
        }
      }
    } catch (error) {
      message.error('Не удалось обновить статус');
    }
  };

  const columns = useMemo(() => [
    {
      title: 'Услуга',
      dataIndex: 'service_name',
    },
    {
      title: 'Клиент',
      dataIndex: 'client_name',
      render: (value, record) => (
        <Space direction="vertical" size={0}>
          <span>{value || 'Гость'}</span>
          <small style={{ color: '#6A6F7A' }}>{record.client_email}</small>
        </Space>
      ),
    },
    {
      title: 'Когда',
      dataIndex: 'appointment_datetime',
      render: (value) => value ? dayjs(value).tz('Europe/Moscow').format('DD MMM HH:mm') : '—',
    },
    {
      title: 'Сумма, ₽',
      dataIndex: 'service_price_cents',
      render: (value) => formatPrice(value),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      render: (value, record) => (
        <Popover
          content={(
            <Space direction="vertical">
              {Object.keys(statusColors).map((key) => (
                <Button key={key} size="small" onClick={() => handleStatusChange(record, key)}>
                  {statusOptions.find((item) => item.value === key)?.label}
                </Button>
              ))}
            </Space>
          )}
          title="Изменить статус"
          trigger="click"
        >
          <Tag color={statusColors[value]} style={{ cursor: 'pointer' }}>
            {statusOptions.find((item) => item.value === value)?.label ?? value}
          </Tag>
        </Popover>
      ),
    },
    {
      title: 'Контакт',
      dataIndex: 'phone',
      render: (value) => value || '—',
    },
  ], []);

  const handleTableChange = (paginationConfig) => {
    setPagination({ current: paginationConfig.current, pageSize: paginationConfig.pageSize });
    load({ page: paginationConfig.current, pageSize: paginationConfig.pageSize });
  };

  const handleStatusFilter = (value) => {
    setFilters((prev) => ({ ...prev, status: value }));
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({ status: value, page: 1 });
  };

  const handleSearch = (value) => {
    setFilters((prev) => ({ ...prev, search: value }));
    // Загрузка произойдёт автоматически через useEffect при изменении debouncedSearch
  };

  const handleDateRangeChange = (range) => {
    setFilters((prev) => ({ ...prev, dateRange: range }));
    setPagination((prev) => ({ ...prev, current: 1 }));
    load({
      dateFrom: range ? range[0].toISOString() : undefined,
      dateTo: range ? range[1].toISOString() : undefined,
      page: 1,
    });
  };

  const handleBulkStatusChange = async (status) => {
    if (selectedRowKeys.length === 0) return;
    try {
      await Promise.all(selectedRowKeys.map((id) => updateBookingStatus(id, { status })));
      message.success('Статусы обновлены');
      setSelectedRowKeys([]);
      await load();
    } catch (error) {
      message.error('Не удалось обновить статусы');
    }
  };

  const handleConfirmPayment = async () => {
    if (!selectedBooking) return;
    if (!paymentAmount || paymentAmount <= 0) {
      message.error('Введите положительную сумму');
      return;
    }

    try {
      setPaymentLoading(true);
      await confirmBookingPayment(selectedBooking.id, { amount_rub: paymentAmount });
      message.success('Оплата подтверждена и бонусы начислены');
      const response = await load();
      if (selectedBooking?.id && response) {
        const updatedBooking = response.items.find((item) => item.id === selectedBooking.id);
        if (updatedBooking) {
          setSelectedBooking(updatedBooking);
        }
      }
      setPaymentAmount(null);
    } catch (error) {
      message.error(error?.response?.data?.detail || 'Не удалось подтвердить оплату');
    } finally {
      setPaymentLoading(false);
    }
  };

  const openBookingDrawer = (record) => {
    setSelectedBooking(record);
    setEditingDateTime(dayjs(record.appointment_datetime));
  };

  const closeBookingDrawer = () => {
    setSelectedBooking(null);
    setPaymentAmount(null);
    setEditingDateTime(null);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys),
  };

  const selectedBookingFormattedPrice = selectedBooking
    ? formatPrice(selectedBooking.service_price_cents)
    : '—';
  const selectedBookingPriceLabel = selectedBookingFormattedPrice === '—'
    ? '—'
    : `${selectedBookingFormattedPrice} ₽`;

  return (
    <Card title="Записи">
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          options={statusOptions}
          value={filters.status}
          onChange={handleStatusFilter}
          style={{ width: 200 }}
          placeholder="Статус"
          allowClear
        />
        <Input.Search
          allowClear
          placeholder="Поиск по клиенту или услуге"
          onSearch={handleSearch}
          style={{ width: 260 }}
        />
        <DatePicker.RangePicker
          onChange={handleDateRangeChange}
          style={{ minWidth: 260 }}
          placeholder={['Дата от', 'Дата до']}
        />
        {selectedRowKeys.length > 0 && (
          <Space>
            <Typography.Text>
              Выбрано:
              {' '}
              {selectedRowKeys.length}
            </Typography.Text>
            <Button onClick={() => handleBulkStatusChange('confirmed')}>Подтвердить</Button>
            <Button danger onClick={() => handleBulkStatusChange('cancelled')}>Отменить</Button>
          </Space>
        )}
      </Space>
      {loading && data.length === 0 ? (
        <Skeleton active paragraph={{ rows: 8 }} />
      ) : (
        <Table
          rowKey="id"
          loading={loading}
          dataSource={data}
          columns={columns}
          rowSelection={rowSelection}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total,
            showSizeChanger: true,
          }}
          onChange={handleTableChange}
          onRow={(record) => ({
            onClick: () => openBookingDrawer(record),
            style: { cursor: 'pointer' },
          })}
        />
      )}

      <Drawer
        title="Детали записи"
        width={480}
        open={!!selectedBooking}
        onClose={closeBookingDrawer}
      >
        {selectedBooking && (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Typography.Title level={5}>{selectedBooking.service_name}</Typography.Title>
            <Typography.Text>
              Клиент:
              {' '}
              {selectedBooking.client_name ?? 'Гость'}
              {' '}
              •
              {' '}
              {selectedBooking.client_email}
            </Typography.Text>
            <Typography.Text>
              Дата и время:
              {' '}
              {dayjs(selectedBooking.appointment_datetime).tz('Europe/Moscow').format('DD.MM.YYYY HH:mm')}
            </Typography.Text>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Typography.Text strong>Изменить дату и время</Typography.Text>
              <DatePicker
                showTime
                style={{ width: '100%' }}
                value={editingDateTime}
                onChange={(val) => setEditingDateTime(val)}
                format="DD.MM.YYYY HH:mm"
              />
              <Button
                onClick={async () => {
                  if (!editingDateTime) return;
                  try {
                    setSavingDateTime(true);
                    const iso = editingDateTime.toISOString();
                    await updateBookingStatus(selectedBooking.id, {
                      status: selectedBooking.status,
                      appointment_datetime: iso,
                    });
                    message.success('Дата и время обновлены');
                    const response = await load();
                    if (selectedBooking?.id && response) {
                      const updatedBooking = response.items.find((item) => item.id === selectedBooking.id);
                      if (updatedBooking) {
                        setSelectedBooking(updatedBooking);
                        setEditingDateTime(dayjs(updatedBooking.appointment_datetime));
                      }
                    }
                  } catch (e) {
                    message.error('Не удалось обновить дату/время');
                  } finally {
                    setSavingDateTime(false);
                  }
                }}
                loading={savingDateTime}
                type="primary"
                block
              >
                Сохранить дату и время
              </Button>
            </Space>
            <Typography.Text>
              Телефон:
              {' '}
              {selectedBooking.phone || '—'}
            </Typography.Text>
            <Typography.Text>
              Статус:
              {' '}
              <Tag color={statusColors[selectedBooking.status]}>
                {statusOptions.find((item) => item.value === selectedBooking.status)?.label}
              </Tag>
            </Typography.Text>
            <Typography.Text>
              Сумма:
              {' '}
              {selectedBookingPriceLabel}
            </Typography.Text>
            <Typography.Text>
              Бонусы начислены:
              {' '}
              {selectedBooking.loyalty_bonuses_awarded ? 'да' : 'нет'}
            </Typography.Text>
            <Space>
              <Button onClick={() => handleStatusChange(selectedBooking, 'confirmed')}>
                Подтвердить
              </Button>
              <Button onClick={() => handleStatusChange(selectedBooking, 'completed')}>
                Завершить
              </Button>
              <Button danger onClick={() => handleStatusChange(selectedBooking, 'cancelled')}>
                Отменить
              </Button>
            </Space>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Typography.Text strong>Подтвердить оплату вручную</Typography.Text>
              <InputNumber
                value={paymentAmount}
                onChange={(value) => setPaymentAmount(value ?? null)}
                placeholder="Сумма, ₽"
                min={0}
                step={0.01}
                style={{ width: '100%' }}
              />
              <Button
                type="primary"
                block
                loading={paymentLoading}
                onClick={handleConfirmPayment}
                disabled={paymentLoading || selectedBooking.loyalty_bonuses_awarded}
              >
                Подтвердить оплату и начислить бонусы
              </Button>
              {selectedBooking.loyalty_bonuses_awarded && (
                <Typography.Text type="success">Бонусы уже начислены</Typography.Text>
              )}
            </Space>
          </Space>
        )}
      </Drawer>
    </Card>
  );
};

export default BookingsPage;

