import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
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
  createLoyaltyBonus,
  createLoyaltyLevel,
  deleteLoyaltyBonus,
  deleteLoyaltyLevel,
  fetchLoyaltyBonuses,
  fetchLoyaltyLevels,
  updateLoyaltyBonus,
  updateLoyaltyLevel,
  fetchLoyaltySettings,
  updateLoyaltySettings,
  bulkAwardLoyalty,
} from '../api/loyalty';

const iconOptions = [
  { value: 'eco', label: 'Лист (eco)' },
  { value: 'card_giftcard', label: 'Подарок (card_giftcard)' },
  { value: 'local_offer', label: 'Тег (local_offer)' },
  { value: 'star_outline', label: 'Звезда (star_outline)' },
];

const LoyaltyPage = () => {
  const { user } = useAuth();
  const [levels, setLevels] = useState([]);
  const [levelsLoading, setLevelsLoading] = useState(true);
  const [levelsModalOpen, setLevelsModalOpen] = useState(false);
  const [levelsModalInitial, setLevelsModalInitial] = useState(null);

  const [bonuses, setBonuses] = useState([]);
  const [bonusesLoading, setBonusesLoading] = useState(true);
  const [bonusModalOpen, setBonusModalOpen] = useState(false);
  const [bonusModalInitial, setBonusModalInitial] = useState(null);

  const [settings, setSettings] = useState(null);
  const [settingsLoading, setSettingsLoading] = useState(true);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);

  const [formLevel] = Form.useForm();
  const [formBonus] = Form.useForm();
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

  const loadBonuses = useCallback(async () => {
    try {
      setBonusesLoading(true);
      const data = await fetchLoyaltyBonuses();
      setBonuses(data);
    } catch {
      message.error('Не удалось загрузить бонусы лояльности');
    } finally {
      setBonusesLoading(false);
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
      setBonusesLoading(false);
      setSettingsLoading(false);
      return;
    }
    loadLevels();
    loadBonuses();
    loadSettings();
  }, [isSuperAdmin, loadBonuses, loadLevels, loadSettings]);

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
      formLevel.setFieldsValue({
        icon: 'eco',
        order_index: 0,
        cashback_percent: 3,
        is_active: true,
      });
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
        title: 'Мин. бонусов',
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

  const handleOpenBonusModal = useCallback((record) => {
    setBonusModalInitial(record || null);
    setBonusModalOpen(true);
    if (record) {
      formBonus.setFieldsValue({
        title: record.title,
        description: record.description,
        icon: record.icon,
        min_level_id: record.min_level_id,
        order_index: record.order_index,
      });
    } else {
      formBonus.resetFields();
      formBonus.setFieldsValue({
        icon: 'card_giftcard',
        order_index: 0,
      });
    }
  }, [formBonus]);

  const handleSubmitBonus = async (values) => {
    try {
      if (bonusModalInitial) {
        await updateLoyaltyBonus(bonusModalInitial.id, values);
        message.success('Бонус обновлён');
      } else {
        await createLoyaltyBonus(values);
        message.success('Бонус создан');
      }
      setBonusModalOpen(false);
      setBonusModalInitial(null);
      formBonus.resetFields();
      loadBonuses();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось сохранить бонус');
    }
  };

  const handleDeleteBonus = useCallback((record) => {
    Modal.confirm({
      title: 'Удалить бонус?',
      content: `Бонус "${record.title}" будет удалён и перестанет отображаться пользователям.`,
      okButtonProps: { danger: true },
      okText: 'Удалить',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteLoyaltyBonus(record.id);
          message.success('Бонус удалён');
          loadBonuses();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить бонус');
        }
      },
    });
  }, [loadBonuses]);

  const levelOptions = useMemo(
    () =>
      levels.map((level) => ({
        value: level.id,
        label: `${level.name} (от ${level.min_bonuses} бонусов)`,
      })),
    [levels],
  );

  const bonusColumns = useMemo(
    () => [
      {
        title: 'Название',
        dataIndex: 'title',
      },
      {
        title: 'Описание',
        dataIndex: 'description',
      },
      {
        title: 'Иконка',
        dataIndex: 'icon',
      },
      {
        title: 'Мин. уровень',
        dataIndex: 'min_level_id',
        render: (value) => {
          if (!value) return 'Все уровни';
          const level = levels.find((l) => l.id === value);
          return level ? level.name : value;
        },
      },
      {
        title: 'Порядок',
        dataIndex: 'order_index',
      },
      {
        title: 'Действия',
        render: (_, record) => (
          <Space>
            <Button size="small" type="link" onClick={() => handleOpenBonusModal(record)}>
              Редактировать
            </Button>
            <Button
              size="small"
              type="link"
              danger
              onClick={() => handleDeleteBonus(record)}
            >
              Удалить
            </Button>
          </Space>
        ),
      },
    ],
    [handleDeleteBonus, handleOpenBonusModal, levels],
  );

  const handleOpenSettingsModal = useCallback(() => {
    if (settings) {
      formSettings.setFieldsValue({
        points_per_100_rub: settings.points_per_100_rub,
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
      message.success(`Начисление выполнено: ${result.processed_users} пользователей`);
      formBulk.resetFields();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось начислить бонусы всем');
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
        title="Настройки начисления баллов"
        extra={(
          <Button onClick={handleOpenSettingsModal} disabled={settingsLoading}>
            Изменить
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Баллы начисляются автоматически после завершения записи (статус COMPLETED).
          Ниже указано, сколько баллов пользователь получает за каждые 100 ₽ стоимости услуги.
        </Typography.Paragraph>
        {settingsLoading ? (
          <Typography.Text>Загрузка...</Typography.Text>
        ) : settings ? (
          <Space direction="vertical" size={8}>
            <Typography.Text strong>
              Начисление:
              {' '}
              <Tag color="green">
                {settings.points_per_100_rub}
                {' '}
                баллов за каждые 100 ₽
              </Tag>
            </Typography.Text>
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
          пользователям приложения. Начисление попадёт в историю бонусов и будет действовать
          стандартный срок жизни программы лояльности.
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
          <Button type="primary" onClick={() => handleOpenLevelModal(null)}>
            Новый уровень
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Здесь настраиваются пороги баллов и визуальный стиль уровней (цвета, иконки, порядок).
          Эти уровни используются в мобильном приложении на экранах профиля и лояльности.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={levelsLoading}
          dataSource={levels}
          columns={levelColumns}
          pagination={false}
        />
      </Card>

      <Card
        title="Бонусы и привилегии"
        extra={(
          <Button type="primary" onClick={() => handleOpenBonusModal(null)}>
            Новый бонус
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Описание преимуществ для разных уровней. Эти карточки отображаются на экране
          программы лояльности в приложении.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={bonusesLoading}
          dataSource={bonuses}
          columns={bonusColumns}
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
            <Input placeholder="Например, Silver, Gold, Platinum" />
          </Form.Item>
          <Form.Item
            label="Минимум бонусов"
            name="min_bonuses"
            rules={[{ required: true, message: 'Укажите минимальное количество бонусов' }]}
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
            <Select options={iconOptions} />
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
        title="Настройки начисления баллов"
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
            label="Баллов за каждые 100 ₽"
            name="points_per_100_rub"
            rules={[
              { required: true, message: 'Укажите количество баллов' },
              { type: 'number', min: 0, message: 'Значение не может быть отрицательным' },
            ]}
            extra="Например, 5 — это 5 баллов за каждые 100 рублей стоимости услуги. При записи на услугу 500 ₽ клиент получит 25 баллов."
          >
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
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

      <Modal
        title={bonusModalInitial ? 'Редактировать бонус' : 'Новый бонус'}
        open={bonusModalOpen}
        onCancel={() => {
          setBonusModalOpen(false);
          setBonusModalInitial(null);
          formBonus.resetFields();
        }}
        onOk={() => formBonus.submit()}
        okText="Сохранить"
        destroyOnClose
      >
        <Form
          layout="vertical"
          form={formBonus}
          onFinish={handleSubmitBonus}
        >
          <Form.Item
            label="Название бонуса"
            name="title"
            rules={[{ required: true, message: 'Введите название' }]}
          >
            <Input placeholder="Например, Скидка 10% на массаж" />
          </Form.Item>
          <Form.Item
            label="Описание"
            name="description"
            rules={[{ required: true, message: 'Введите описание бонуса' }]}
          >
            <Input.TextArea rows={3} placeholder="Кратко опишите, что получает гость" />
          </Form.Item>
          <Form.Item
            label="Иконка"
            name="icon"
          >
            <Select options={iconOptions} />
          </Form.Item>
          <Form.Item
            label="Минимальный уровень"
            name="min_level_id"
          >
            <Select
              allowClear
              placeholder="Все уровни"
              options={levelOptions}
            />
          </Form.Item>
          <Form.Item
            label="Порядок отображения"
            name="order_index"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
};

export default LoyaltyPage;
