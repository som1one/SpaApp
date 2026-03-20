import { Card, Col, Empty, Row, Statistic, Typography, message } from 'antd';
import { Column, Pie } from '@ant-design/plots';
import dayjs from '../utils/dayjs';
import { useEffect, useMemo, useState } from 'react';
import apiClient from '../api/client';

const DashboardPage = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const summaryRes = await apiClient.get('/admin/dashboard/summary', { timeout: 10000 });
        setSummary(summaryRes.data);
      } catch (error) {
        console.error('Failed to load dashboard data', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Не удалось загрузить статистику';
        message.error(`Ошибка загрузки данных: ${errorMessage}`);
        setSummary({
          total_users: 0,
          active_users: 0,
          verified_users: 0,
          users_with_bonuses: 0,
          users_with_levels: 0,
          total_bonus_balance: 0,
          monthly_users: [],
          loyalty_level_breakdown: [],
        });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const monthlyUsersData = useMemo(() => {
    if (!summary?.monthly_users) return [];
    return summary.monthly_users.map((item) => ({
      month: dayjs(`${item.month}-01`).tz('Europe/Moscow').format('MMM YY'),
      value: item.count || 0,
    }));
  }, [summary]);

  const loyaltyLevelsData = useMemo(() => (
    summary?.loyalty_level_breakdown?.map((item) => ({
      type: item.level,
      value: item.count,
    })) ?? []
  ), [summary]);

  const usersColumnConfig = {
    data: monthlyUsersData,
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

  const levelsPieConfig = {
    data: loyaltyLevelsData,
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
        content: loyaltyLevelsData.length ? `Всего\n${summary?.users_with_levels ?? 0}` : 'Нет данных',
      },
    },
    padding: [16, 16, 40, 16],
  };

  return (
    <div className="dashboard-page">
      <Typography.Title level={3} style={{ marginBottom: 8 }}>
        Сводка по клиентской базе
      </Typography.Title>
      <Typography.Paragraph type="secondary" style={{ marginBottom: 24 }}>
        На главной теперь только обзор по клиентам и лояльности — без записей и кодов пользователей.
      </Typography.Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="Всего клиентов" value={summary?.total_users ?? 0} valueStyle={{ color: '#722ed1' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="Активные" value={summary?.active_users ?? 0} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="Почта подтверждена" value={summary?.verified_users ?? 0} valueStyle={{ color: '#1890ff' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="С бонусами" value={summary?.users_with_bonuses ?? 0} valueStyle={{ color: '#fa8c16' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="С уровнем" value={summary?.users_with_levels ?? 0} valueStyle={{ color: '#13c2c2' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card loading={loading}>
            <Statistic title="Баланс бонусов" value={summary?.total_bonus_balance ?? 0} valueStyle={{ color: '#415B2F' }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} md={14}>
          <Card title="Новые клиенты по месяцам" loading={loading}>
            {monthlyUsersData.length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Недостаточно данных" />
            ) : (
              <Column {...usersColumnConfig} />
            )}
          </Card>
        </Col>
        <Col xs={24} md={10}>
          <Card title="Распределение по уровням" loading={loading}>
            {loyaltyLevelsData.length === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Нет данных по уровням" />
            ) : (
              <Pie {...levelsPieConfig} />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
