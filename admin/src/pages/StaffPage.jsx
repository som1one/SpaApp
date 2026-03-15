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
  TimePicker,
  message,
  Tabs,
  Typography,
} from 'antd';
import { useAuth } from '../context/AuthContext';
import { useEffect, useState } from 'react';
import {
  createStaff,
  createStaffSchedule,
  createStaffService,
  deleteStaff,
  deleteStaffSchedule,
  deleteStaffService,
  fetchStaff,
  fetchStaffById,
  fetchStaffSchedules,
  updateStaff,
  updateStaffSchedule,
} from '../api/staff';
import { fetchServices } from '../api/services';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

const DAYS_OF_WEEK = [
  { value: 0, label: 'Понедельник' },
  { value: 1, label: 'Вторник' },
  { value: 2, label: 'Среда' },
  { value: 3, label: 'Четверг' },
  { value: 4, label: 'Пятница' },
  { value: 5, label: 'Суббота' },
  { value: 6, label: 'Воскресенье' },
];

const StaffPage = () => {
  const { user } = useAuth();

  if (user?.role !== 'super_admin') {
    return (
      <Card>
        <Typography.Text>
          Управлять мастерами и расписанием могут только супер-администраторы.
        </Typography.Text>
      </Card>
    );
  }
  const [staff, setStaff] = useState([]);
  const [staffLoading, setStaffLoading] = useState(true);
  const [staffModalOpen, setStaffModalOpen] = useState(false);
  const [staffModalInitial, setStaffModalInitial] = useState(null);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [services, setServices] = useState([]);
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false);
  const [scheduleModalInitial, setScheduleModalInitial] = useState(null);

  const [formStaff] = Form.useForm();
  const [formSchedule] = Form.useForm();

  const loadStaff = async () => {
    try {
      setStaffLoading(true);
      const data = await fetchStaff();
      setStaff(data);
    } catch (error) {
      message.error('Не удалось загрузить мастеров');
    } finally {
      setStaffLoading(false);
    }
  };

  const loadServices = async () => {
    try {
      const data = await fetchServices();
      setServices(data);
    } catch (error) {
      message.error('Не удалось загрузить услуги');
    }
  };

  const loadSchedules = async (staffId) => {
    try {
      const data = await fetchStaffSchedules(staffId);
      setSchedules(data);
    } catch (error) {
      message.error('Не удалось загрузить расписание');
    }
  };

  useEffect(() => {
    loadStaff();
    loadServices();
  }, []);

  const handleOpenStaffModal = (record) => {
    setStaffModalInitial(record || null);
    setStaffModalOpen(true);
    if (record) {
      formStaff.setFieldsValue(record);
    } else {
      formStaff.resetFields();
    }
  };

  const handleSubmitStaff = async (values) => {
    try {
      if (staffModalInitial) {
        await updateStaff(staffModalInitial.id, values);
        message.success('Мастер обновлён');
      } else {
        await createStaff(values);
        message.success('Мастер создан');
      }
      setStaffModalOpen(false);
      setStaffModalInitial(null);
      formStaff.resetFields();
      loadStaff();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось сохранить мастера');
    }
  };

  const handleDeleteStaff = (record) => {
    Modal.confirm({
      title: 'Удалить мастера?',
      content: `Мастер "${record.name} ${record.surname || ''}" будет удалён.`,
      okButtonProps: { danger: true },
      okText: 'Удалить',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteStaff(record.id);
          message.success('Мастер удалён');
          loadStaff();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить мастера');
        }
      },
    });
  };

  const handleSelectStaff = async (staffId) => {
    const staffData = await fetchStaffById(staffId);
    setSelectedStaff(staffData);
    loadSchedules(staffId);
  };

  const handleOpenScheduleModal = (record) => {
    setScheduleModalInitial(record || null);
    setScheduleModalOpen(true);
    
    // Определяем staff_id для формы
    const staffId = record?.staff_id || selectedStaff?.id;
    
    if (record) {
      // Редактирование существующего расписания
      formSchedule.setFieldsValue({
        ...record,
        staff_id: staffId,
        start_time: record.start_time ? dayjs(record.start_time, 'HH:mm') : null,
        end_time: record.end_time ? dayjs(record.end_time, 'HH:mm') : null,
        break_start: record.break_start ? dayjs(record.break_start, 'HH:mm') : null,
        break_end: record.break_end ? dayjs(record.break_end, 'HH:mm') : null,
      });
    } else {
      // Создание нового расписания
      formSchedule.resetFields();
      if (staffId) {
        formSchedule.setFieldsValue({ staff_id: staffId });
        console.log('✅ Установлен staff_id в форму:', staffId);
      } else {
        console.warn('⚠️ Внимание: staff_id не установлен! selectedStaff:', selectedStaff);
      }
    }
  };

  const handleSubmitSchedule = async (values) => {
    try {
      // Форматируем время, убеждаясь что dayjs объекты преобразуются в строки
      const formatTime = (timeValue) => {
        if (!timeValue) return null;
        // Если это dayjs объект
        if (typeof timeValue === 'object' && timeValue.format) {
          return timeValue.format('HH:mm');
        }
        // Если это уже строка
        if (typeof timeValue === 'string') {
          return timeValue;
        }
        return null;
      };
      
      // Определяем staff_id из значений формы или selectedStaff
      const staffId = values.staff_id || selectedStaff?.id;
      
      // Проверяем обязательные поля
      if (!staffId) {
        message.error('Ошибка: мастер не выбран. Пожалуйста, выберите мастера сначала.');
        return;
      }
      if (!values.start_time) {
        message.error('Укажите время начала работы');
        return;
      }
      if (!values.end_time) {
        message.error('Укажите время окончания работы');
        return;
      }
      if (values.day_of_week === undefined || values.day_of_week === null) {
        message.error('Выберите день недели');
        return;
      }
      
      const formattedStartTime = formatTime(values.start_time);
      const formattedEndTime = formatTime(values.end_time);
      
      if (!formattedStartTime || !/^\d{2}:\d{2}$/.test(formattedStartTime)) {
        message.error('Неверный формат времени начала работы. Используйте формат HH:MM');
        return;
      }
      if (!formattedEndTime || !/^\d{2}:\d{2}$/.test(formattedEndTime)) {
        message.error('Неверный формат времени окончания работы. Используйте формат HH:MM');
        return;
      }
      
      // Проверяем, что время окончания позже времени начала
      const [startHour, startMin] = formattedStartTime.split(':').map(Number);
      const [endHour, endMin] = formattedEndTime.split(':').map(Number);
      const startMinutes = startHour * 60 + startMin;
      const endMinutes = endHour * 60 + endMin;
      
      if (endMinutes <= startMinutes) {
        message.error('Время окончания работы должно быть позже времени начала');
        return;
      }
      
      const scheduleData = {
        staff_id: Number(staffId),
        day_of_week: Number(values.day_of_week),
        start_time: formattedStartTime,
        end_time: formattedEndTime,
        is_active: values.is_active !== false,
      };
      
      // Добавляем перерывы только если они указаны
      if (values.break_start) {
        const breakStart = formatTime(values.break_start);
        if (breakStart && /^\d{2}:\d{2}$/.test(breakStart)) {
          scheduleData.break_start = breakStart;
        }
      }
      if (values.break_end) {
        const breakEnd = formatTime(values.break_end);
        if (breakEnd && /^\d{2}:\d{2}$/.test(breakEnd)) {
          scheduleData.break_end = breakEnd;
        }
      }
      
      console.log('✅ Отправка данных расписания:', scheduleData);
      console.log('✅ Типы данных:', {
        staff_id: typeof scheduleData.staff_id,
        day_of_week: typeof scheduleData.day_of_week,
        start_time: typeof scheduleData.start_time,
        end_time: typeof scheduleData.end_time,
      });
      
      if (scheduleModalInitial) {
        await updateStaffSchedule(scheduleModalInitial.id, scheduleData);
        message.success('Расписание обновлено');
      } else {
        await createStaffSchedule(scheduleData);
        message.success('Расписание создано');
      }
      setScheduleModalOpen(false);
      setScheduleModalInitial(null);
      formSchedule.resetFields();
      if (selectedStaff) {
        loadSchedules(selectedStaff.id);
      }
    } catch (error) {
      console.error('❌ Ошибка при сохранении расписания:', error);
      console.error('❌ Детали ошибки:', error?.response?.data);
      console.error('❌ Полный объект ошибки:', error);
      
      let errorMessage = 'Не удалось сохранить расписание';
      
      // Используем сообщение из axios interceptor, если есть
      if (error?.message) {
        errorMessage = error.message;
      } else if (error?.response?.data) {
        const errorData = error.response.data;
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Форматируем ошибки валидации более понятно
            const messages = errorData.detail.map((e) => {
              const field = e.loc?.slice(1).join('.') || 'неизвестное поле'; // убираем 'body' из пути
              const msg = e.msg || 'ошибка';
              const value = e.input !== undefined ? ` (значение: ${JSON.stringify(e.input)})` : '';
              return `${field}: ${msg}${value}`;
            });
            errorMessage = messages.join('\n');
          } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      }
      
      // Показываем ошибку в модальном окне для лучшей читаемости
      message.error({
        content: errorMessage,
        duration: 8,
        style: { whiteSpace: 'pre-line' }, // Поддержка переносов строк
      });
    }
  };

  const handleDeleteSchedule = (scheduleId) => {
    Modal.confirm({
      title: 'Удалить расписание?',
      okButtonProps: { danger: true },
      okText: 'Удалить',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteStaffSchedule(scheduleId);
          message.success('Расписание удалено');
          if (selectedStaff) {
            loadSchedules(selectedStaff.id);
          }
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить расписание');
        }
      },
    });
  };

  const staffColumns = [
    {
      title: 'Имя',
      dataIndex: 'name',
    },
    {
      title: 'Фамилия',
      dataIndex: 'surname',
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
    },
    {
      title: 'Специализация',
      dataIndex: 'specialization',
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      render: (value) => (
        <Tag color={value ? 'green' : 'red'}>{value ? 'Активен' : 'Неактивен'}</Tag>
      ),
    },
    {
      title: 'Действия',
      render: (_, record) => (
        <Space>
          <Button size="small" type="link" onClick={() => handleSelectStaff(record.id)}>
            Подробнее
          </Button>
          <Button size="small" type="link" onClick={() => handleOpenStaffModal(record)}>
            Редактировать
          </Button>
          <Button size="small" type="link" danger onClick={() => handleDeleteStaff(record)}>
            Удалить
          </Button>
        </Space>
      ),
    },
  ];

  const scheduleColumns = [
    {
      title: 'День недели',
      dataIndex: 'day_of_week',
      render: (value) => DAYS_OF_WEEK.find((d) => d.value === value)?.label || value,
    },
    {
      title: 'Время работы',
      render: (_, record) => `${record.start_time} - ${record.end_time}`,
    },
    {
      title: 'Перерыв',
      render: (_, record) =>
        record.break_start && record.break_end
          ? `${record.break_start} - ${record.break_end}`
          : 'Нет',
    },
    {
      title: 'Действия',
      render: (_, record) => (
        <Space>
          <Button size="small" type="link" onClick={() => handleOpenScheduleModal(record)}>
            Редактировать
          </Button>
          <Button
            size="small"
            type="link"
            danger
            onClick={() => handleDeleteSchedule(record.id)}
          >
            Удалить
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card
        title="Мастера"
        extra={(
          <Button type="primary" onClick={() => handleOpenStaffModal(null)}>
            Новый мастер
          </Button>
        )}
      >
        <Table
          rowKey="id"
          loading={staffLoading}
          dataSource={staff}
          columns={staffColumns}
          pagination={false}
        />
      </Card>

      {selectedStaff && (
        <Card title={`Расписание мастера: ${selectedStaff.name} ${selectedStaff.surname || ''}`}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Button
              type="primary"
              onClick={() => handleOpenScheduleModal(null)}
            >
              Добавить расписание
            </Button>
            <Table
              rowKey="id"
              dataSource={schedules}
              columns={scheduleColumns}
              pagination={false}
            />
          </Space>
        </Card>
      )}

      {/* Модальное окно для мастера */}
      <Modal
        title={staffModalInitial ? 'Редактировать мастера' : 'Новый мастер'}
        open={staffModalOpen}
        onCancel={() => {
          setStaffModalOpen(false);
          setStaffModalInitial(null);
          formStaff.resetFields();
        }}
        onOk={() => formStaff.submit()}
        okText="Сохранить"
        destroyOnClose
        width={600}
      >
        <Form layout="vertical" form={formStaff} onFinish={handleSubmitStaff}>
          <Form.Item label="Имя" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Фамилия" name="surname">
            <Input />
          </Form.Item>
          <Form.Item label="Телефон" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="email">
            <Input type="email" />
          </Form.Item>
          <Form.Item label="Специализация" name="specialization">
            <Input />
          </Form.Item>
          <Form.Item label="Описание" name="description">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item label="Порядок" name="order_index">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Модальное окно для расписания */}
      <Modal
        title={scheduleModalInitial ? 'Редактировать расписание' : 'Новое расписание'}
        open={scheduleModalOpen}
        onCancel={() => {
          setScheduleModalOpen(false);
          setScheduleModalInitial(null);
          formSchedule.resetFields();
        }}
        onOk={() => formSchedule.submit()}
        okText="Сохранить"
        destroyOnClose
      >
        <Form layout="vertical" form={formSchedule} onFinish={handleSubmitSchedule}>
          {/* Скрытое поле для staff_id */}
          <Form.Item name="staff_id" hidden>
            <Input type="hidden" />
          </Form.Item>
          
          <Form.Item 
            label="День недели" 
            name="day_of_week" 
            rules={[{ required: true, message: 'Выберите день недели' }]}
          >
            <Select placeholder="Выберите день недели">
              {DAYS_OF_WEEK.map((day) => (
                <Option key={day.value} value={day.value}>
                  {day.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item 
            label="Начало работы" 
            name="start_time" 
            rules={[{ required: true, message: 'Укажите время начала работы' }]}
          >
            <TimePicker format="HH:mm" style={{ width: '100%' }} placeholder="Выберите время" />
          </Form.Item>
          <Form.Item 
            label="Конец работы" 
            name="end_time" 
            rules={[{ required: true, message: 'Укажите время окончания работы' }]}
          >
            <TimePicker format="HH:mm" style={{ width: '100%' }} placeholder="Выберите время" />
          </Form.Item>
          <Form.Item label="Начало перерыва" name="break_start">
            <TimePicker format="HH:mm" style={{ width: '100%' }} placeholder="Опционально" />
          </Form.Item>
          <Form.Item label="Конец перерыва" name="break_end">
            <TimePicker format="HH:mm" style={{ width: '100%' }} placeholder="Опционально" />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
};

export default StaffPage;

