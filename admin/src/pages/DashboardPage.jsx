import { Button, Card, Col, Form, Input, InputNumber, List, Modal, Row, Space, Statistic, Tag, Typography, message } from 'antd';
import { Column, Pie } from '@ant-design/plots';
import { GiftOutlined, MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import dayjs from '../utils/dayjs';
import { useEffect, useMemo, useState } from 'react';
import apiClient from '../api/client';
import { adjustUserLoyalty, getUserByCode } from '../api/loyalty';

const statusLabels = {
  confirmed: 'Подтверждено',
  pending: 'В ожидании',
  completed: 'Завершено',
  cancelled: 'Отменено',
};

const DashboardPage = () => {
  const [summary, setSummary] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [spendModalOpen, setSpendModalOpen] = useState(false);
  const [codeSearchLoading, setCodeSearchLoading] = useState(false);
  const [spendLoading, setSpendLoading] = useState(false);
  const [codeSearchResult, setCodeSearchResult] = useState(null);
  const [spendForm] = Form.useForm();
  const watchedServices = Form.useWatch('services', spendForm) || [];
  // Расчет бонусов для начисления: сумма услуг * процент кэшбэка уровня
  const servicesTotal = watchedServices
    .filter((service) => service?.service_name && service?.price_rub)
    .reduce((sum, service) => sum + Number(service.price_rub || 0), 0);
  const cashbackPercent = codeSearchResult?.cashback_percent || 3;
  const bonusesToAward = Math.floor(servicesTotal * cashbackPercent / 100);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [summaryRes, bookingsRes] = await Promise.all([
          apiClient.get('/admin/dashboard/summary', { timeout: 10000 }),
          apiClient.get('/admin/dashboard/bookings', { 
            params: { limit: 6 },
            timeout: 10000,
          }),
        ]);
        setSummary(summaryRes.data);
        setBookings(bookingsRes.data?.items ?? []);
      } catch (error) {
        console.error('Failed to load dashboard data', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Не удалось загрузить статистику';
        message.error(`Ошибка загрузки данных: ${errorMessage}`);
        // Устанавливаем пустые данные при ошибке
        setSummary({
          total_users: 0,
          total_bookings: 0,
          confirmed_bookings: 0,
          pending_bookings: 0,
          completed_bookings: 0,
          cancelled_bookings: 0,
          status_breakdown: [],
          monthly_bookings: [],
        });
        setBookings([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const statusData = useMemo(() => (
    summary?.status_breakdown?.map((item) => ({
      type: statusLabels[item.status] ?? item.status,
      value: item.count,
    })) ?? []
  ), [summary]);

  const statusTotal = statusData.reduce((acc, item) => acc + item.value, 0);

  const monthlyData = useMemo(() => {
    if (!summary?.monthly_bookings) return [];
    return summary.monthly_bookings.map((item) => {
      // item.month может быть строкой формата "YYYY-MM" или датой
      let monthStr = item.month;
      if (typeof monthStr === 'string' && monthStr.match(/^\d{4}-\d{2}$/)) {
        // Если это строка "YYYY-MM", добавляем день для парсинга
        monthStr = `${monthStr}-01`;
      }
      // Используем московское время для форматирования
      return {
        month: dayjs(monthStr).tz('Europe/Moscow').format('MMM YY'),
        value: item.count || 0,
      };
    });
  }, [summary]);

  const pieConfig = {
    data: statusData,
    angleField: 'value',
    colorField: 'type',
    innerRadius: 0.65,
    legend: {
      position: 'bottom',
      itemName: { style: { fontSize: 12 } },
    },
    label: {
      type: 'inner',
      offset: '-50%',
      content: '{value}',
      style: { fill: '#fff', fontSize: 12 },
    },
    statistic: {
      title: false,
      content: {
        style: { fontSize: 14, fontWeight: 600 },
        content: statusTotal ? `Всего\n${statusTotal}` : 'Нет данных',
      },
    },
    padding: [16, 16, 40, 16],
  };

  const columnConfig = {
    data: monthlyData,
    xField: 'month',
    yField: 'value',
    columnWidthRatio: 0.5,
    tooltip: { showMarkers: false },
    color: '#415B2F',
    label: {
      position: 'top',
      style: { fontSize: 12 },
    },
  };

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

  const handleSpendBonuses = async (values) => {
    if (!codeSearchResult) {
      message.error('Сначала найдите пользователя по коду');
      return;
    }
    
    try {
      setSpendLoading(true);
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
      
      const updatedUser = await getUserByCode(codeSearchResult.unique_code);
      setCodeSearchResult(updatedUser);
      spendForm.resetFields(['bonuses_delta', 'reason', 'services']);
    } catch (error) {
      message.error(error.response?.data?.detail || 'Ошибка при изменении бонусов');
    } finally {
      setSpendLoading(false);
    }
  };

  return (
    <div className="dashboard-page">
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="Всего записей" 
              value={summary?.total_bookings ?? 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="Подтверждено" 
              value={summary?.confirmed_bookings ?? 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="В ожидании" 
              value={summary?.pending_bookings ?? 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="Завершено" 
              value={summary?.completed_bookings ?? 0}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="Отменено" 
              value={summary?.cancelled_bookings ?? 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic 
              title="Клиенты" 
              value={summary?.total_users ?? 0}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card
            title="Быстрые действия"
            extra={
              <Button
                type="primary"
                icon={<GiftOutlined />}
                onClick={() => setSpendModalOpen(true)}
              >
                Списать бонусы по коду
              </Button>
            }
          >
            <p style={{ color: '#6A6F7A', margin: 0 }}>
              Используйте код из профиля пользователя для быстрого списания бонусов
            </p>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Записи по месяцам" loading={loading}>
            {monthlyData.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#6A6F7A' }}>Недостаточно данных</div>
            ) : (
              <Column {...columnConfig} />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card title="Статусы записей" loading={loading}>
            {statusData.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#6A6F7A' }}>Недостаточно данных</div>
            ) : (
              <Pie {...pieConfig} />
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Ближайшие записи" loading={loading}>
            <List
              dataSource={bookings}
              locale={{ emptyText: 'Нет записей' }}
              renderItem={(item) => {
                const dateStr = item.appointment_datetime 
                  ? dayjs(item.appointment_datetime).tz('Europe/Moscow').format('DD MMM HH:mm')
                  : 'Дата не указана';
                return (
                  <List.Item
                    actions={[
                      <Tag color="green" key="status">
                        {statusLabels[item.status] ?? item.status}
                      </Tag>,
                    ]}
                  >
                    <List.Item.Meta
                      title={item.service_name ?? 'Услуга'}
                      description={`${item.client_name ?? 'Гость'} • ${dateStr}`}
                    />
                  </List.Item>
                );
              }}
            />
          </Card>
        </Col>
      </Row>


      {/* Модальное окно для списания бонусов по коду */}
      <Modal
        title="Списать бонусы по коду пользователя"
        open={spendModalOpen}
        onCancel={() => {
          setSpendModalOpen(false);
          spendForm.resetFields();
          setCodeSearchResult(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={spendForm}
          layout="vertical"
          onFinish={codeSearchResult ? handleSpendBonuses : handleCodeSearch}
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
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <strong>Имя:</strong> {codeSearchResult.name} {codeSearchResult.surname || ''}
                  </div>
                  <div>
                    <strong>Email:</strong> {codeSearchResult.email}
                  </div>
                  <div>
                    <strong>Код:</strong> <Tag color="blue">{codeSearchResult.unique_code}</Tag>
                  </div>
                  <div>
                    <strong>Текущие бонусы:</strong>{' '}
                    <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                      {codeSearchResult.loyalty_bonuses || 0} бонусов
                    </span>
                  </div>
                </Space>
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
                          <Input placeholder="Например, Spa-путешествие" />
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
                      spendForm.resetFields(['bonuses_delta', 'reason', 'services']);
                    }}
                  >
                    Найти другого пользователя
                  </Button>
                  <Button type="primary" htmlType="submit" loading={spendLoading} block>
                    {servicesTotal > 0 || spendForm.getFieldValue('bonuses_delta') 
                      ? 'Применить изменения' 
                      : 'Списать бонусы'}
                  </Button>
                </Space>
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default DashboardPage;
