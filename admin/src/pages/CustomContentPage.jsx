import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Upload,
  Table,
  Tag,
  Typography,
  Switch,
  message,
  Image,
} from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useAuth } from '../context/useAuth';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchCustomContentBlocks,
  createCustomContentBlock,
  updateCustomContentBlock,
  deleteCustomContentBlock,
  uploadCustomContentImage,
} from '../api/customContent';

const blockTypeOptions = [
  { value: 'spa_travel', label: 'Спа-терапия (карусель на главной)' },
  { value: 'promotion', label: 'Акция' },
  { value: 'banner', label: 'Баннер' },
  { value: 'custom', label: 'Кастомный' },
];

const CustomContentPage = () => {
  const { user } = useAuth();
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalInitial, setModalInitial] = useState(null);
  const [form] = Form.useForm();
  const isSuperAdmin = user?.role === 'super_admin';
  const selectedBlockType = Form.useWatch('block_type', form);
  const currentImageUrl = Form.useWatch('image_url', form);

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

  const trimOrNull = (v) => {
    if (v === undefined || v === null) return null;
    if (typeof v === 'string') {
      const t = v.trim();
      return t === '' ? null : t;
    }
    return v;
  };

  const handleSubmit = async (values) => {
    const base = values.block_type === 'spa_travel'
      ? {
          ...values,
          description: null,
          action_text: null,
          background_color: null,
          text_color: null,
          gradient_start: null,
          gradient_end: null,
        }
      : { ...values };

    const payload = {
      ...base,
      subtitle: trimOrNull(base.subtitle),
      description: trimOrNull(base.description),
      image_url: trimOrNull(base.image_url),
      action_url: trimOrNull(base.action_url),
      action_text: trimOrNull(base.action_text),
      background_color: trimOrNull(base.background_color),
      text_color: trimOrNull(base.text_color),
      gradient_start: trimOrNull(base.gradient_start),
      gradient_end: trimOrNull(base.gradient_end),
    };

    try {
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

  const handleImageUpload = useCallback(async ({ file, onSuccess, onError }) => {
    try {
      const result = await uploadCustomContentImage(file);
      form.setFieldValue('image_url', result.url);
      message.success('Изображение загружено');
      onSuccess?.(result);
    } catch (error) {
      const detail = error?.response?.data?.detail ?? 'Не удалось загрузить изображение';
      message.error(detail);
      onError?.(new Error(detail));
    }
  }, [form]);

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
            <Button
              size="small"
              type="link"
              danger
              onClick={() => handleDelete(record)}
            >
              Удалить
            </Button>
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

  const spaTherapyBlocks = blocks.filter((block) => block.block_type === 'spa_travel');
  const otherBlocks = blocks.filter((block) => block.block_type !== 'spa_travel');

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card
        title="Спа-терапия на главной"
        extra={(
          <Button
            type="primary"
            onClick={() => {
              handleOpenModal(null);
              form.setFieldValue('block_type', 'spa_travel');
            }}
          >
            Новая карточка
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Здесь настраивается именно карусель с ездящими карточками на главной странице приложения.
          Для каждой карточки можно менять текст, ссылку, фото и порядок.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={spaTherapyBlocks}
          columns={columns}
          pagination={false}
          locale={{ emptyText: 'Карточки для блока «Спа-терапия» ещё не созданы' }}
        />
      </Card>

      <Card
        title="Кастомные блоки контента"
        extra={(
          <Button type="primary" onClick={() => handleOpenModal(null)}>
            Новый блок
          </Button>
        )}
      >
        <Typography.Paragraph type="secondary">
          Остальные блоки контента для главного экрана приложения. Спа-терапия вынесена в отдельный блок выше.
        </Typography.Paragraph>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={otherBlocks}
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
          <Form.Item
            label={selectedBlockType === 'spa_travel' ? 'Текст карточки' : 'Заголовок'}
            name="title"
            rules={[{ required: true, message: 'Введите заголовок' }]}
          >
            <Input placeholder={selectedBlockType === 'spa_travel' ? 'Например, Head Spa Ritual' : 'Например, Spa-путешествия'} />
          </Form.Item>
          <Form.Item
            label={selectedBlockType === 'spa_travel' ? 'Подпись' : 'Подзаголовок'}
            name="subtitle"
          >
            <Input placeholder={selectedBlockType === 'spa_travel' ? 'Короткая подпись под карточкой' : 'Краткое описание'} />
          </Form.Item>
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Описание"
              name="description"
            >
              <Input.TextArea rows={4} placeholder="Подробное описание (может быть HTML)" />
            </Form.Item>
          )}
          <Form.Item
            label={selectedBlockType === 'spa_travel' ? 'Фото карточки' : 'Изображение'}
            name="image_url"
          >
            <Input placeholder="/uploads/custom-content/example.jpg" />
          </Form.Item>
          <Form.Item label={selectedBlockType === 'spa_travel' ? 'Загрузить фото карточки' : 'Загрузить изображение'}>
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Upload
                accept="image/*"
                showUploadList={false}
                customRequest={handleImageUpload}
              >
                <Button icon={<UploadOutlined />}>Загрузить изображение</Button>
              </Upload>
              {currentImageUrl ? (
                <Image
                  src={currentImageUrl}
                  alt="Превью"
                  width={220}
                  style={{ borderRadius: 12, objectFit: 'cover' }}
                />
              ) : (
                <Typography.Text type="secondary">
                  Пока изображение не выбрано
                </Typography.Text>
              )}
            </Space>
          </Form.Item>
          <Form.Item
            label={selectedBlockType === 'spa_travel' ? 'Ссылка по нажатию (необязательно)' : 'URL действия / ссылка (необязательно)'}
            name="action_url"
          >
            <Input placeholder="Оставьте пустым, если переход не нужен" />
          </Form.Item>
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Текст кнопки действия"
              name="action_text"
            >
              <Input placeholder="Например, Подробнее" />
            </Form.Item>
          )}
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
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="Активен"
            name="is_active"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Цвет фона (HEX)"
              name="background_color"
            >
              <Input placeholder="#FFFFFF" />
            </Form.Item>
          )}
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Цвет текста (HEX)"
              name="text_color"
            >
              <Input placeholder="#000000" />
            </Form.Item>
          )}
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Градиент начало (HEX)"
              name="gradient_start"
            >
              <Input placeholder="#4CAF50" />
            </Form.Item>
          )}
          {selectedBlockType !== 'spa_travel' && (
            <Form.Item
              label="Градиент конец (HEX)"
              name="gradient_end"
            >
              <Input placeholder="#81C784" />
            </Form.Item>
          )}
          {selectedBlockType === 'spa_travel' && (
            <Typography.Text type="secondary">
              Для карточек «Спа-терапии» используется только изображение, текст и ссылка.
              Цвета и градиенты здесь не применяются.
            </Typography.Text>
          )}
        </Form>
      </Modal>
    </Space>
  );
};

export default CustomContentPage;
