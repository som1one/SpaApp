import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import { useAuth } from '../context/useAuth';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  createLoyaltyLevel,
  deleteLoyaltyLevel,
  fetchLoyaltyLevels,
  updateLoyaltyLevel,
  fetchLoyaltySettings,
  updateLoyaltySettings,
  bulkAwardLoyalty,
  recalculateLoyaltyLevels,
} from '../api/loyalty';

const LoyaltyPage = () => {
  const { user } = useAuth();
  const [levels, setLevels] = useState([]);
  const [levelsLoading, setLevelsLoading] = useState(true);
  const [levelsModalOpen, setLevelsModalOpen] = useState(false);
  const [levelsModalInitial, setLevelsModalInitial] = useState(null);

  const [settings, setSettings] = useState(null);
  const [settingsLoading, setSettingsLoading] = useState(true);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [recalculateLoading, setRecalculateLoading] = useState(false);

  const [formLevel] = Form.useForm();
  const [formSettings] = Form.useForm();
  const [formBulk] = Form.useForm();
  const isSuperAdmin = user?.role === 'super_admin';

  const loadLevels = useCallback(async () => {
    try {
      setLevelsLoading(true);
      const data = await fetchLoyaltyLevels();
      setLevels(data);
    } catch {
      message.error('Не удалось загрузить уровни лояльности');
    } finally {
      setLevelsLoading(false);
    }
  }, []);

  const loadSettings = useCallback(async () => {
    try {
      setSettingsLoading(true);
      const data = await fetchLoyaltySettings();
      setSettings(data);
    } catch {
      message.error('Не удалось загрузить настройки лояльности');
    } finally {
      setSettingsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isSuperAdmin) {
      setLevelsLoading(false);
      setSettingsLoading(false);
      return;
    }
    loadLevels();
    loadSettings();
  }, [isSuperAdmin, loadLevels, loadSettings]);

  const handleOpenLevelModal = useCallback((record) => {
    setLevelsModalInitial(record || null);
    setLevelsModalOpen(true);
    if (record) {
      formLevel.setFieldsValue({
        name: record.name,
        min_bonuses: record.min_bonuses,
        cashback_percent: record.cashback_percent,
        color_start: record.color_start,
        color_end: record.color_end,
        icon: record.icon,
        order_index: record.order_index,
        is_active: record.is_active,
      });
    } else {
      formLevel.resetFields();
      formLevel.setFieldsValue({ order_index: 0, cashback_percent: 3, is_active: true });
    }
  }, [formLevel]);

  const handleSubmitLevel = async (values) => {
    try {
      if (levelsModalInitial) {
        await updateLoyaltyLevel(levelsModalInitial.id, values);
        message.success('Уровень обновлён');
      } else {
        await createLoyaltyLevel(values);
        message.success('Уровень создан');
      }
      setLevelsModalOpen(false);
      setLevelsModalInitial(null);
      formLevel.resetFields();
      loadLevels();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось сохранить уровень');
    }
  };

  const handleDeleteLevel = useCallback((record) => {
    Modal.confirm({
      title: 'Удалить уровень?',
      content: `Уровень "${record.name}" будет удалён. Убедитесь, что он не используется в описаниях.`,
      okButtonProps: { danger: true },
      okText: 'Удалить',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteLoyaltyLevel(record.id);
          message.success('Уровень удалён');
          loadLevels();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить уровень');
        }
      },
    });
  }, [loadLevels]);

  const levelColumns = useMemo(
    () => [
      {
        title: 'Название',
        dataIndex: 'name',
      },
      {
        title: 'Порог трат, ₽',
        dataIndex: 'min_bonuses',
      },
      {
        title: 'Кэшбэк',
        dataIndex: 'cashback_percent',
        render: (value) => <Tag color="green">{value}%</Tag>,
      },
      {
        title: 'Статус',
        dataIndex: 'is_active',
        render: (value) => <Tag color={value ? 'green' : 'red'}>{value ? 'Активен' : 'Скрыт'}</Tag>,
      },
      {
        title: 'Цвет',
        render: (_, record) => (
          <Space>
            <Tag color={record.color_start}>{record.color_start}</Tag>
            <Tag color={record.color_end}>{record.color_end}</Tag>
          </Space>
        ),
      },
      {
        title: 'Иконка',
        dataIndex: 'icon',
        render: (value) => value || 'eco',
      },
      {
        title: 'Порядок',
        dataIndex: 'order_index',
      },
      {
        title: 'Действия',
        render: (_, record) => (
          <Space>
            <Button size="small" type="link" onClick={() => handleOpenLevelModal(record)}>
              Редактировать
            </Button>
            <Button
              size="small"
              type="link"
              danger
              onClick={() => handleDeleteLevel(record)}
            >
              Удалить
            </Button>
          </Space>
        ),
      },
    ],
    [handleDeleteLevel, handleOpenLevelModal],
  );

  const handleOpenSettingsModal = useCallback(() => {
    if (settings) {
      formSettings.setFieldsValue({
        loyalty_enabled: settings.loyalty_enabled,
        welcome_bonus_amount: settings.welcome_bonus_amount,
        bonus_expiry_days: settings.bonus_expiry_days,
        yclients_bonus_field_id: settings.yclients_bonus_field_id,
      });
    }
    setSettingsModalOpen(true);
  }, [formSettings, settings]);

  const handleSubmitSettings = async (values) => {
    try {
      await updateLoyaltySettings(values);
      message.success('Настройки обновлены');
      setSettingsModalOpen(false);
      loadSettings();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось обновить настройки');
    }
  };

  const handleBulkAward = async (values) => {
    try {
      const result = await bulkAwardLoyalty(values);
      message.success(
        `Начисление выполнено: ${result.processed_users} пользователей${
          values.expires_in_days ? `, срок ${values.expires_in_days} дн.` : ''
        }`,
      );
      formBulk.resetFields();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось начислить бонусы всем');
    }
  };

  const handleRecalculateLevels = async () => {
    try {
      setRecalculateLoading(true);
      const result = await recalculateLoyaltyLevels();
      message.success(
        `Уровни пересчитаны: обработано ${result.processed_users}, обновлено ${result.updated_users}`,
      );
      loadLevels();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось пересчитать уровни');
    } finally {
      setRecalculateLoading(false);
    }
  };

  if (!isSuperAdmin) {
    return (
      <Card>
        <Typography.Text>
          Управлять программой лояльности могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card
        title="Настройки начисления бонусов"
        extra={(
          <Button onClick={handleOpenSettingsModal} disabled={settingsLoading}>
            Изменить
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Бонусы начисляются автоматически только после того, как заявка закрылась в YClients
          и попала к нам со статусом `COMPLETED`. Размер начисления считается как процент
          кэшбэка текущего уровня от суммы визита.
        </Typography.Paragraph>
        {settingsLoading ? (
          <Typography.Text>Загрузка...</Typography.Text>
        ) : settings ? (
          <Space direction="vertical" size={8}>
            <Alert
              type="info"
              showIcon
              message="Фиксированная схема «5 бонусов за 100 ₽» больше не используется"
              description="Теперь начисление идёт только по проценту кэшбэка уровня пользователя."
            />
            <Typography.Text type="secondary">
              Программа лояльности:
              {' '}
              {settings.loyalty_enabled ? (
                <Tag color="green">Включена</Tag>
              ) : (
                <Tag color="red">Выключена</Tag>
              )}
            </Typography.Text>
            <Typography.Text type="secondary">
              Приветственный бонус:
              {' '}
              <Tag color="blue">{settings.welcome_bonus_amount} бонусов</Tag>
            </Typography.Text>
            <Typography.Text type="secondary">
              Срок действия бонусов:
              {' '}
              <Tag color="gold">{settings.bonus_expiry_days} дней</Tag>
            </Typography.Text>
            <Typography.Text type="secondary">
              Поле бонусов в YClients:
              {' '}
              {settings.yclients_bonus_field_id ? (
                <Tag color="purple">{settings.yclients_bonus_field_id}</Tag>
              ) : (
                <Tag>Не задано</Tag>
              )}
            </Typography.Text>
          </Space>
        ) : (
          <Typography.Text type="danger">Не удалось загрузить настройки</Typography.Text>
        )}
      </Card>

      <Card title="Массовое начисление бонусов">
        <Typography.Paragraph type="secondary">
          Используйте этот блок, чтобы начислить одинаковое количество бонусов всем активным
          пользователям приложения. Если укажете срок — бонусы будут временными и автоматически сгорят.
        </Typography.Paragraph>
        <Form
          form={formBulk}
          layout="vertical"
          onFinish={handleBulkAward}
        >
          <Form.Item
            label="Количество бонусов"
            name="bonuses_amount"
            rules={[
              { required: true, message: 'Укажите количество бонусов' },
              { type: 'number', min: 1, message: 'Значение должно быть больше 0' },
            ]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="Срок действия временных бонусов (дней, необязательно)"
            name="expires_in_days"
            extra="Оставьте пустым, если начисление должно быть бессрочным."
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="Причина"
            name="reason"
          >
            <Input.TextArea rows={3} placeholder="Например: Подарок к празднику" />
          </Form.Item>
          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            <Alert
              type="info"
              showIcon
              message="Начисление выполняется сразу для всех активных пользователей."
            />
            <Button type="primary" onClick={() => formBulk.submit()}>
              Начислить всем
            </Button>
          </Space>
        </Form>
      </Card>

      <Card
        title="Уровни лояльности"
        extra={(
          <Space>
            <Button onClick={handleRecalculateLevels} loading={recalculateLoading}>
              Пересчитать уровни
            </Button>
            <Button type="primary" onClick={() => handleOpenLevelModal(null)}>
              Новый уровень
            </Button>
          </Space>
        )}
      >
        <Typography.Paragraph type="secondary">
          Здесь настраиваются пороги трат и процент кэшбэка для каждого уровня.
          Если уровни уже были созданы раньше и не проставились пользователям, нажмите
          `Пересчитать уровни`.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={levelsLoading}
          dataSource={levels}
          columns={levelColumns}
          pagination={false}
        />
      </Card>

      <Modal
        title={levelsModalInitial ? 'Редактировать уровень' : 'Новый уровень'}
        open={levelsModalOpen}
        onCancel={() => {
          setLevelsModalOpen(false);
          setLevelsModalInitial(null);
          formLevel.resetFields();
        }}
        onOk={() => formLevel.submit()}
        okText="Сохранить"
        destroyOnClose
      >
        <Form
          layout="vertical"
          form={formLevel}
          onFinish={handleSubmitLevel}
        >
          <Form.Item
            label="Название уровня"
            name="name"
            rules={[{ required: true, message: 'Введите название уровня' }]}
          >
            <Input placeholder="Например, 0 / 1 / 2 / 3 / 4" />
          </Form.Item>
          <Form.Item
            label="Минимальная сумма трат, ₽"
            name="min_bonuses"
            rules={[{ required: true, message: 'Укажите минимальную сумму трат' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        <Form.Item
          label="Кэшбэк (%)"
          name="cashback_percent"
          rules={[{ required: true, message: 'Укажите процент кэшбэка' }]}
        >
          <InputNumber min={0} max={100} style={{ width: '100%' }} />
        </Form.Item>
          <Form.Item
            label="Цвет градиента (начало)"
            name="color_start"
            rules={[{ required: true, message: 'Укажите цвет, например, #4CAF50' }]}
          >
            <Input placeholder="#4CAF50" />
          </Form.Item>
          <Form.Item
            label="Цвет градиента (конец)"
            name="color_end"
            rules={[{ required: true, message: 'Укажите цвет, например, #81C784' }]}
          >
            <Input placeholder="#81C784" />
          </Form.Item>
          <Form.Item
            label="Иконка"
            name="icon"
          >
            <Input placeholder="Например, eco" />
          </Form.Item>
          <Form.Item
            label="Порядок отображения"
            name="order_index"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        <Form.Item
          label="Отображать уровень"
          name="is_active"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Настройки начисления бонусов"
        open={settingsModalOpen}
        onCancel={() => {
          setSettingsModalOpen(false);
          formSettings.resetFields();
        }}
        onOk={() => formSettings.submit()}
        okText="Сохранить"
        destroyOnClose
      >
        <Form
          layout="vertical"
          form={formSettings}
          onFinish={handleSubmitSettings}
        >
          <Form.Item
            label="Приветственный бонус после регистрации"
            name="welcome_bonus_amount"
            rules={[
              { required: true, message: 'Укажите размер приветственного бонуса' },
              { type: 'number', min: 0, message: 'Значение не может быть отрицательным' },
            ]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="Срок действия бонусов (дней)"
            name="bonus_expiry_days"
            rules={[
              { required: true, message: 'Укажите срок действия' },
              { type: 'number', min: 1, message: 'Срок должен быть больше 0' },
            ]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="ID кастомного поля бонусов в YClients"
            name="yclients_bonus_field_id"
            extra="Сюда можно вставить ID/ключ пользовательского поля клиента в YClients, куда будем записывать текущий бонусный баланс."
          >
            <Input placeholder="Например: 123456 или loyalty_balance" />
          </Form.Item>
          <Form.Item
            label="Программа лояльности включена"
            name="loyalty_enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Typography.Text type="secondary">
            Настройки сохраняются в базе данных и применяются сразу.
          </Typography.Text>
        </Form>
      </Modal>
    </Space>
  );
};

export default LoyaltyPage;
