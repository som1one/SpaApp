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
  Table,
  Tag,
  Typography,
  Switch,
  message,
} from 'antd';
import { useAuth } from '../context/useAuth';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchCustomContentBlocks,
  createCustomContentBlock,
  updateCustomContentBlock,
  deleteCustomContentBlock,
} from '../api/customContent';

const blockTypeOptions = [
  { value: 'spa_travel', label: 'Популярные SPA (карусель)' },
  { value: 'spa_therapy_feature', label: 'SPA терапия (3 фиксированные карточки)' },
  { value: 'promotion', label: 'Акция' },
  { value: 'banner', label: 'Баннер' },
  { value: 'custom', label: 'Кастомный' },
];

const spaTherapyTitles = {
  0: 'Подарочные сертификаты',
  1: 'Спа-меню',
  2: 'Каталог товаров',
};

const CustomContentPage = () => {
  const { user } = useAuth();
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalInitial, setModalInitial] = useState(null);
  const [form] = Form.useForm();
  const isSuperAdmin = user?.role === 'super_admin';
  const selectedType = Form.useWatch('block_type', form);
  const selectedOrderIndex = Form.useWatch('order_index', form);
  const isSpaTherapyFeature = selectedType === 'spa_therapy_feature';

  const loadBlocks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchCustomContentBlocks();
      setBlocks(data);
    } catch {
      message.error('Не удалось загрузить блоки контента');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isSuperAdmin) {
      setLoading(false);
      return;
    }
    loadBlocks();
  }, [isSuperAdmin, loadBlocks]);

  useEffect(() => {
    if (!modalOpen || !isSpaTherapyFeature) {
      return;
    }

    const normalizedOrder = Number(selectedOrderIndex ?? 0);
    form.setFieldValue('title', spaTherapyTitles[normalizedOrder] ?? spaTherapyTitles[0]);
    form.setFieldValue('is_active', true);
  }, [form, isSpaTherapyFeature, modalOpen, selectedOrderIndex]);

  const handleOpenModal = useCallback((record) => {
    setModalInitial(record || null);
    setModalOpen(true);
    if (record) {
      form.setFieldsValue({
        title: record.title,
        subtitle: record.subtitle,
        description: record.description,
        image_url: record.image_url,
        action_url: record.action_url,
        action_text: record.action_text,
        block_type: record.block_type,
        order_index: record.order_index,
        is_active: record.is_active,
        background_color: record.background_color,
        text_color: record.text_color,
        gradient_start: record.gradient_start,
        gradient_end: record.gradient_end,
      });
    } else {
      form.resetFields();
      form.setFieldsValue({
        block_type: 'custom',
        order_index: 0,
        is_active: true,
      });
    }
  }, [form]);

  const handleSubmit = async (values) => {
    try {
      const payload = { ...values };
      if (payload.block_type === 'spa_therapy_feature') {
        payload.order_index = Number(payload.order_index ?? 0);
        payload.title = spaTherapyTitles[payload.order_index];
        payload.is_active = true;
      }

      if (modalInitial) {
        await updateCustomContentBlock(modalInitial.id, payload);
        message.success('Блок обновлён');
      } else {
        await createCustomContentBlock(payload);
        message.success('Блок создан');
      }
      setModalOpen(false);
      setModalInitial(null);
      form.resetFields();
      loadBlocks();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось сохранить блок');
    }
  };

  const handleDelete = useCallback((record) => {
    Modal.confirm({
      title: 'Удалить блок?',
      content: `Блок "${record.title}" будет удалён и перестанет отображаться на главном экране.`,
      okButtonProps: { danger: true },
      okText: 'Удалить',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteCustomContentBlock(record.id);
          message.success('Блок удалён');
          loadBlocks();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить блок');
        }
      },
    });
  }, [loadBlocks]);

  const columns = useMemo(
    () => [
      {
        title: 'Заголовок',
        dataIndex: 'title',
        width: 200,
      },
      {
        title: 'Тип',
        dataIndex: 'block_type',
        render: (value) => {
          const option = blockTypeOptions.find((opt) => opt.value === value);
          return <Tag color="blue">{option?.label || value}</Tag>;
        },
      },
      {
        title: 'Порядок',
        dataIndex: 'order_index',
        width: 80,
      },
      {
        title: 'Активен',
        dataIndex: 'is_active',
        width: 100,
        render: (value) => (
          <Tag color={value ? 'green' : 'red'}>{value ? 'Да' : 'Нет'}</Tag>
        ),
      },
      {
        title: 'Действия',
        width: 150,
        render: (_, record) => (
          <Space>
            <Button size="small" type="link" onClick={() => handleOpenModal(record)}>
              Редактировать
            </Button>
            {record.block_type !== 'spa_therapy_feature' && (
              <Button
                size="small"
                type="link"
                danger
                onClick={() => handleDelete(record)}
              >
                Удалить
              </Button>
            )}
          </Space>
        ),
      },
    ],
    [handleDelete, handleOpenModal],
  );

  if (!isSuperAdmin) {
    return (
      <Card>
        <Typography.Text>
          Управлять кастомным контентом могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card
        title="Кастомные блоки контента"
        extra={(
          <Button type="primary" onClick={() => handleOpenModal(null)}>
            Новый блок
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Управление кастомными блоками контента, которые отображаются на главном экране приложения.
          Можно создавать блоки с изображениями, текстом, ссылками и настраивать их внешний вид.
        </Typography.Paragraph>
        <Typography.Paragraph type="secondary">
          Для блока <strong>SPA терапия</strong> используются 3 фиксированные карточки:
          названия и количество слотов менять нельзя, можно редактировать только подписи, ссылки и оформление.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={blocks}
          columns={columns}
          pagination={false}
        />
      </Card>

      <Modal
        title={modalInitial ? 'Редактировать блок' : 'Новый блок'}
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false);
          setModalInitial(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Сохранить"
        destroyOnClose
        width={800}
      >
        <Form
          layout="vertical"
          form={form}
          onFinish={handleSubmit}
        >
          {isSpaTherapyFeature && (
            <Alert
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
              message="SPA терапия — 3 фиксированные карточки"
              description="Слот 0: Подарочные сертификаты, слот 1: Спа-меню, слот 2: Каталог товаров. Удалить, скрыть или переименовать их нельзя."
            />
          )}
          <Form.Item
            label="Заголовок"
            name="title"
            rules={[{ required: true, message: 'Введите заголовок' }]}
            extra={isSpaTherapyFeature ? 'Название фиксируется автоматически по слоту.' : null}
          >
            <Input placeholder="Например, Spa-путешествия" disabled={isSpaTherapyFeature} />
          </Form.Item>
          <Form.Item
            label="Подзаголовок"
            name="subtitle"
          >
            <Input placeholder="Краткое описание" />
          </Form.Item>
          <Form.Item
            label="Описание"
            name="description"
          >
            <Input.TextArea rows={4} placeholder="Подробное описание (может быть HTML)" />
          </Form.Item>
          <Form.Item
            label="URL изображения"
            name="image_url"
          >
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>
          <Form.Item
            label="URL действия (ссылка)"
            name="action_url"
          >
            <Input placeholder="https://example.com" />
          </Form.Item>
          <Form.Item
            label="Текст кнопки действия"
            name="action_text"
          >
            <Input placeholder="Например, Подробнее" />
          </Form.Item>
          <Form.Item
            label="Тип блока"
            name="block_type"
            rules={[{ required: true }]}
          >
            <Select options={blockTypeOptions} />
          </Form.Item>
          <Form.Item
            label="Порядок отображения"
            name="order_index"
          >
            <InputNumber
              min={0}
              max={isSpaTherapyFeature ? 2 : undefined}
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item
            label="Активен"
            name="is_active"
            valuePropName="checked"
          >
            <Switch disabled={isSpaTherapyFeature} />
          </Form.Item>
          <Form.Item
            label="Цвет фона (HEX)"
            name="background_color"
          >
            <Input placeholder="#FFFFFF" />
          </Form.Item>
          <Form.Item
            label="Цвет текста (HEX)"
            name="text_color"
          >
            <Input placeholder="#000000" />
          </Form.Item>
          <Form.Item
            label="Градиент начало (HEX)"
            name="gradient_start"
          >
            <Input placeholder="#4CAF50" />
          </Form.Item>
          <Form.Item
            label="Градиент конец (HEX)"
            name="gradient_end"
          >
            <Input placeholder="#81C784" />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
};

export default CustomContentPage;
