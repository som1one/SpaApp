import {
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
import { useAuth } from '../context/AuthContext';
import { useEffect, useMemo, useState } from 'react';
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
} from '../api/loyalty';

const iconOptions = [
  { value: 'eco', label: 'Лист (eco)' },
  { value: 'card_giftcard', label: 'Подарок (card_giftcard)' },
  { value: 'local_offer', label: 'Тег (local_offer)' },
  { value: 'star_outline', label: 'Звезда (star_outline)' },
];

const LoyaltyPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Управлять программой лояльности могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }
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

  const loadLevels = async () => {
    try {
      setLevelsLoading(true);
      const data = await fetchLoyaltyLevels();
      setLevels(data);
    } catch (error) {
      message.error('Не удалось загрузить уровни лояльности');
    } finally {
      setLevelsLoading(false);
    }
  };

  const loadBonuses = async () => {
    try {
      setBonusesLoading(true);
      const data = await fetchLoyaltyBonuses();
      setBonuses(data);
    } catch (error) {
      message.error('Не удалось загрузить бонусы лояльности');
    } finally {
      setBonusesLoading(false);
    }
  };

  const loadSettings = async () => {
    try {
      setSettingsLoading(true);
      const data = await fetchLoyaltySettings();
      setSettings(data);
    } catch (error) {
      message.error('Не удалось загрузить настройки лояльности');
    } finally {
      setSettingsLoading(false);
    }
  };

  useEffect(() => {
    loadLevels();
    loadBonuses();
    loadSettings();
  }, []);

  const handleOpenLevelModal = (record) => {
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
  };

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

  const handleDeleteLevel = (record) => {
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
  };

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
    [],
  );

  const handleOpenBonusModal = (record) => {
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
  };

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

  const handleDeleteBonus = (record) => {
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
  };

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
    [levels],
  );

  const handleOpenSettingsModal = () => {
    if (settings) {
      formSettings.setFieldsValue({
        points_per_100_rub: settings.points_per_100_rub,
        loyalty_enabled: settings.loyalty_enabled,
      });
    }
    setSettingsModalOpen(true);
  };

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
          </Space>
        ) : (
          <Typography.Text type="danger">Не удалось загрузить настройки</Typography.Text>
        )}
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
            label="Программа лояльности включена"
            name="loyalty_enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Typography.Text type="warning">
            ⚠️ Настройка сохраняется временно до перезапуска сервера.
            Для постоянного изменения обновите значение LOYALTY_POINTS_PER_100_RUB в .env файле.
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


