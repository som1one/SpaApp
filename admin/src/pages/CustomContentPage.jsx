import {
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
  ColorPicker,
} from 'antd';
import { useAuth } from '../context/AuthContext';
import { useEffect, useMemo, useState } from 'react';
import {
  fetchCustomContentBlocks,
  createCustomContentBlock,
  updateCustomContentBlock,
  deleteCustomContentBlock,
} from '../api/customContent';

const blockTypeOptions = [
  { value: 'spa_travel', label: 'Spa-путешествия' },
  { value: 'promotion', label: 'Акция' },
  { value: 'banner', label: 'Баннер' },
  { value: 'custom', label: 'Кастомный' },
];

const CustomContentPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Управлять кастомным контентом могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalInitial, setModalInitial] = useState(null);
  const [form] = Form.useForm();

  const loadBlocks = async () => {
    try {
      setLoading(true);
      const data = await fetchCustomContentBlocks();
      setBlocks(data);
    } catch (error) {
      message.error('Не удалось загрузить блоки контента');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBlocks();
  }, []);

  const handleOpenModal = (record) => {
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
  };

  const handleSubmit = async (values) => {
    try {
      if (modalInitial) {
        await updateCustomContentBlock(modalInitial.id, values);
        message.success('Блок обновлён');
      } else {
        await createCustomContentBlock(values);
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

  const handleDelete = (record) => {
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
  };

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
    [],
  );

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
          <Form.Item
            label="Заголовок"
            name="title"
            rules={[{ required: true, message: 'Введите заголовок' }]}
          >
            <Input placeholder="Например, Spa-путешествия" />
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
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="Активен"
            name="is_active"
            valuePropName="checked"
          >
            <Switch />
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

