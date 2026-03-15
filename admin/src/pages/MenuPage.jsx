import {
  Button,
  Card,
  Checkbox,
  Divider,
  Drawer,
  Empty,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Spin,
  Switch,
  Tag,
  Typography,
  Upload,
  message,
} from 'antd';
import { useAuth } from '../context/AuthContext';
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import {
  bulkUpdateServices,
  createCategory,
  createService,
  deleteCategory,
  deleteService,
  fetchMenuTree,
  updateCategory,
  updateService,
  uploadMenuImage,
  reorderCategories,
  reorderServices,
} from '../api/menu';

const { Title, Text } = Typography;

const emptyCategory = {
  id: null,
  name: '',
  description: '',
  image_url: '',
};

const MenuPage = () => {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === 'super_admin';
  const [tree, setTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryModal, setCategoryModal] = useState({ open: false, mode: 'create', parentId: null, initial: emptyCategory });
  const [serviceModal, setServiceModal] = useState({ open: false, mode: 'create', initial: null, categoryId: null });
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedServices, setSelectedServices] = useState([]);
  const [moveModal, setMoveModal] = useState({ open: false });

  const loadTree = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchMenuTree();
      setTree(data);
      const storedId = localStorage.getItem('spa_menu_last_category_id');
      setSelectedCategory((prevSelected) => {
        let nextSelected = null;
        if (storedId) {
          const parsed = Number(storedId);
          if (!Number.isNaN(parsed)) {
            nextSelected = findCategoryById(data, parsed);
          }
        }
        if (!nextSelected && prevSelected) {
          nextSelected = findCategoryById(data, prevSelected.id);
        }
        return nextSelected;
      });
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось загрузить меню');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTree();
  }, [loadTree]);

  const openCategoryModal = (mode, parentId = null, initial = emptyCategory) => {
    setCategoryModal({
      open: true,
      mode,
      parentId,
      initial: initial ?? emptyCategory,
    });
  };

  const openServiceModal = (mode, categoryId, initial = null) => {
    setServiceModal({
      open: true,
      mode,
      categoryId,
      initial,
    });
  };

  const handleDeleteCategory = (category) => {
    // Нельзя удалить виртуальную категорию "Без категории"
    if (category.id === null || category.id === undefined) {
      return;
    }
    Modal.confirm({
      title: 'Удалить раздел?',
      content: 'Подразделы и услуги внутри нужно удалить заранее.',
      okText: 'Удалить',
      okButtonProps: { danger: true },
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteCategory(category.id);
          message.success('Раздел удалён');
          if (selectedCategory?.id === category.id) {
            setSelectedCategory(null);
          }
          loadTree();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить раздел');
        }
      },
    });
  };

  const handleDeleteService = (service) => {
    Modal.confirm({
      title: 'Удалить услугу?',
      okText: 'Удалить',
      okButtonProps: { danger: true },
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await deleteService(service.id);
          message.success('Услуга удалена');
          loadTree();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось удалить услугу');
        }
      },
    });
  };

  const handleCategorySubmit = async (values) => {
    try {
      if (categoryModal.mode === 'create') {
        await createCategory({ ...values, parent_id: categoryModal.parentId });
        message.success('Раздел добавлен');
      } else {
        await updateCategory(categoryModal.initial.id, values);
        message.success('Раздел обновлён');
      }
      setCategoryModal({ ...categoryModal, open: false });
      loadTree();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Ошибка сохранения раздела');
    }
  };

  const handleServiceSubmit = async (values) => {
    const payload = {
      ...values,
      category_id: serviceModal.categoryId ?? values.category_id,
      additional_services: values.additional_services?.map((name) => ({ name })),
      // Сохраняем is_active как есть, если он явно передан, иначе используем значение из initial или true по умолчанию
      is_active: values.is_active !== undefined ? values.is_active : (serviceModal.initial?.is_active ?? true),
    };
    try {
      if (serviceModal.mode === 'create') {
        await createService(payload);
        message.success('Услуга добавлена');
      } else {
        await updateService(serviceModal.initial.id, payload);
        message.success('Услуга обновлена');
      }
      setServiceModal({ ...serviceModal, open: false });
      loadTree();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Ошибка сохранения услуги');
    }
  };

  const categoryCards = useMemo(() => tree ?? [], [tree]);

  const renderServiceCard = (service) => {
    const checked = selectedServices.includes(service.id);
    return (
      <Card
        key={service.id}
        className={`menu-service-card${checked ? ' menu-service-card--selected' : ''}`}
        cover={service.image_url ? <div className="menu-service-cover" style={{ backgroundImage: `url(${service.image_url})` }} /> : null}
        actions={isSuperAdmin ? [
          <Button type="link" onClick={() => openServiceModal('edit', service.category_id ?? serviceModal.categoryId, service)}>
            Редактировать
          </Button>,
          <Button danger type="text" icon={<DeleteOutlined />} onClick={() => handleDeleteService(service)} />,
        ] : []}
      >
        <div className="menu-service-header">
          {isSuperAdmin && selectionMode && (
            <Checkbox
              checked={checked}
              onChange={(e) => toggleServiceSelection(service.id, e.target.checked)}
              style={{ marginRight: 8 }}
            />
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <Title level={5} style={{ marginBottom: 0, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
              {service.name}
            </Title>
            {service.subtitle && (
              <Text type="secondary" style={{ fontSize: 12, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                {service.subtitle}
              </Text>
            )}
          </div>
          <Space size={4}>
            {service.duration && <Tag>{`${service.duration} мин.`}</Tag>}
            <Tag
              color={service.is_active === false ? 'default' : 'green'}
              onClick={isSuperAdmin ? (e) => {
                e.stopPropagation();
                handleToggleServiceActive(service);
              } : undefined}
              style={{ cursor: isSuperAdmin ? 'pointer' : 'default' }}
            >
              {service.is_active === false ? 'Скрыта' : 'Показывается'}
            </Tag>
          </Space>
        </div>
        <Divider style={{ margin: '12px 0' }} />
        <div className="menu-service-footer">
          {service.price ? (
            <Text strong>
              {service.price.toLocaleString('ru-RU')}
              {' '}
              ₽
            </Text>
          ) : <Text type="secondary">Без цены</Text>}
          <Space>
            {service.additional_services?.slice(0, 2).map((item) => (
              <Tag key={item.name}>{item.name}</Tag>
            ))}
          </Space>
        </div>
      </Card>
    );
  };

  const toggleServiceSelection = (serviceId, checked) => {
    setSelectedServices((prev) => {
      if (checked) return [...prev, serviceId];
      return prev.filter((id) => id !== serviceId);
    });
  };

  const clearSelections = () => {
    setSelectedServices([]);
    setSelectionMode(false);
  };

  const handleBulkDelete = () => {
    if (selectedServices.length === 0) return;
    Modal.confirm({
      title: `Удалить ${selectedServices.length} усл.?`,
      content: 'Услуги будут удалены без возможности восстановления. В мобильном приложении они исчезнут сразу.',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await Promise.all(selectedServices.map((id) => deleteService(id)));
          message.success('Удалено');
          clearSelections();
          loadTree();
        } catch (error) {
          message.error('Не удалось удалить выбранные услуги');
        }
      },
    });
  };

  const handleBulkVisibility = (visible) => {
    if (selectedServices.length === 0) return;
    Modal.confirm({
      title: visible ? 'Сделать услуги видимыми?' : 'Скрыть выбранные услуги?',
      content: visible
        ? 'Выбранные услуги станут доступны пользователям в мобильном приложении.'
        : 'Выбранные услуги перестанут отображаться в мобильном приложении, но останутся в админке.',
      onOk: async () => {
        try {
          await bulkUpdateServices({ ids: selectedServices, is_active: visible });
          message.success('Видимость обновлена');
          clearSelections();
          loadTree();
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Не удалось изменить видимость');
        }
      },
    });
  };

  const handleToggleServiceActive = async (service) => {
    try {
      // Переключаем видимость: если скрыта (false) → показываем (true), если показана (true/undefined) → скрываем (false)
      const newIsActive = service.is_active === false;
      await bulkUpdateServices({
        ids: [service.id],
        is_active: newIsActive,
      });
      loadTree();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось изменить видимость услуги');
    }
  };

  const handleOpenMoveModal = () => {
    if (selectedServices.length === 0) return;
    setMoveModal({ open: true });
  };

  const handleMoveSubmit = async (values) => {
    try {
      await bulkUpdateServices({ ids: selectedServices, category_id: values.category_id });
      message.success('Услуги перемещены');
      setMoveModal({ open: false });
      clearSelections();
      loadTree();
    } catch (error) {
      message.error(error?.response?.data?.detail ?? 'Не удалось переместить услуги');
    }
  };

  const handleDragEnd = async (result) => {
    if (!isSuperAdmin) return;
    if (!result.destination || result.destination.index === result.source.index) return;
    if (result.type === 'categories') {
      const parentId = extractParentId(result.source.droppableId);
      const categories = getCategoriesByParent(parentId);
      if (!categories) return;
      const reordered = reorderList(categories, result.source.index, result.destination.index);
      try {
        await reorderCategories(parentId, reordered.map((item, index) => ({ id: item.id, order_index: index })));
        message.success('Порядок разделов обновлён');
        loadTree();
      } catch (error) {
        message.error(error?.response?.data?.detail ?? 'Не удалось сохранить порядок');
      }
    } else if (result.type === 'services') {
      const categoryId = extractParentId(result.source.droppableId);
      if (!categoryId) return;
      const category = findCategoryById(tree, categoryId);
      if (!category) return;
      const reordered = reorderList(category.services, result.source.index, result.destination.index);
      try {
        await reorderServices(categoryId, reordered.map((item, index) => ({ id: item.id, order_index: index })));
        message.success('Порядок услуг обновлён');
        loadTree();
      } catch (error) {
        message.error(error?.response?.data?.detail ?? 'Не удалось сохранить порядок услуг');
      }
    }
  };

  const getCategoriesByParent = (parentId) => {
    if (parentId === null) return tree;
    const parent = findCategoryById(tree, parentId);
    return parent?.children;
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="menu-page">
        <div className="menu-header">
          <div>
            <Title level={3} style={{ marginBottom: 0 }}>SPA-меню</Title>
            <Text type="secondary">Разделы, подразделы и услуги мобильного приложения</Text>
          </div>
          {isSuperAdmin && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openCategoryModal('create')}
            >
              Новый раздел
            </Button>
          )}
        </div>

      {loading ? (
        <div className="menu-loading">
          <Spin size="large" />
        </div>
      ) : categoryCards.length === 0 ? (
        <Empty description="Разделы пока не созданы" />
      ) : (
        <Droppable droppableId="categories-root" direction="horizontal" type="categories">
          {(provided) => (
            <div className="menu-grid" ref={provided.innerRef} {...provided.droppableProps}>
              {categoryCards.map((category, index) => {
                const totalServices = category.services.length;
                const activeCount = category.services.filter((s) => s.is_active !== false).length;
                const hiddenCount = totalServices - activeCount;
                const isEmpty = category.children.length === 0 && totalServices === 0;
                const isUncategorized = category.id === null || category.id === undefined;
                return (
                <Draggable 
                  key={category.id ?? `uncategorized-${index}`} 
                  draggableId={`category-${category.id ?? `uncategorized-${index}`}`} 
                  index={index}
                  isDragDisabled={isUncategorized || !isSuperAdmin} // Нельзя перетаскивать виртуальную категорию или без прав
                >
                  {(dragProvided) => (
                    <Card
                      ref={dragProvided.innerRef}
                      {...dragProvided.draggableProps}
                      {...dragProvided.dragHandleProps}
                      className={`menu-card ${isUncategorized ? 'menu-card--uncategorized' : ''}`}
                      cover={category.image_url ? (
                        <div className="menu-card-cover" style={{ backgroundImage: `url(${category.image_url})` }} />
                      ) : (
                        <div className="menu-card-cover menu-card-cover--empty">
                          <Text>Нет изображения</Text>
                        </div>
                      )}
                      onClick={() => {
                        setSelectedCategory(category);
                        if (category.id) {
                          localStorage.setItem('spa_menu_last_category_id', String(category.id));
                        } else {
                          localStorage.removeItem('spa_menu_last_category_id');
                        }
                        clearSelections();
                      }}
                      actions={isSuperAdmin && !isUncategorized ? [
                        <Button type="text" icon={<EditOutlined />} onClick={(e) => { e.stopPropagation(); openCategoryModal('edit', null, category); }} />,
                        <Button danger type="text" icon={<DeleteOutlined />} onClick={(e) => { e.stopPropagation(); handleDeleteCategory(category); }} />,
                      ] : []}
                    >
                      <Title level={5}>{category.name}</Title>
                      <Space direction="vertical" size={2}>
                        <Text type="secondary">
                          {category.children.length}
                          {' '}
                          подразделов •
                          {' '}
                          {totalServices}
                          {' '}
                          услуг
                        </Text>
                        <Space size={8}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Активных:
                            {' '}
                            {activeCount}
                          </Text>
                          {hiddenCount > 0 && (
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              Скрытых:
                              {' '}
                              {hiddenCount}
                            </Text>
                          )}
                          {isEmpty && (
                            <Tag color="default" style={{ fontSize: 11 }}>
                              Пустой раздел
                            </Tag>
                          )}
                        </Space>
                      </Space>
                    </Card>
                  )}
                </Draggable>
              ); })}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      )}

      <Drawer
        width={780}
        title={selectedCategory?.name}
        onClose={() => {
          setSelectedCategory(null);
          localStorage.removeItem('spa_menu_last_category_id');
          clearSelections();
        }}
        open={!!selectedCategory}
        destroyOnClose
        extra={isSuperAdmin && selectedCategory && selectedCategory.id && (
          <Space>
            <Button onClick={() => openCategoryModal('edit', null, selectedCategory)} icon={<EditOutlined />}>
              Редактировать
            </Button>
            <Button danger icon={<DeleteOutlined />} onClick={() => handleDeleteCategory(selectedCategory)}>
              Удалить
            </Button>
          </Space>
        )}
      >
        {selectedCategory && (
          <div className="category-detail">
            {selectedCategory.image_url && (
              <div className="category-detail-cover" style={{ backgroundImage: `url(${selectedCategory.image_url})` }} />
            )}
            {selectedCategory.description && (
              <>
                <Title level={5}>Описание</Title>
                <Text>{selectedCategory.description}</Text>
                <Divider />
              </>
            )}

            {isSuperAdmin && (
              <div className="category-actions">
                {selectedCategory.id && (
                  <Button icon={<PlusOutlined />} onClick={() => openCategoryModal('create', selectedCategory.id)}>
                    Подраздел
                  </Button>
                )}
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => openServiceModal('create', selectedCategory.id)}
                >
                  Услугу
                </Button>
                <Button
                  type={selectionMode ? 'default' : 'dashed'}
                  onClick={() => {
                    setSelectionMode((prev) => !prev);
                    setSelectedServices([]);
                  }}
                >
                  {selectionMode ? 'Отмена выбора' : 'Выбрать услуги'}
                </Button>
              </div>
            )}

            {selectedCategory.id && (
              <>
                <Divider />
                <Title level={5}>Подразделы</Title>
                {selectedCategory.children.length === 0 ? (
                  <Empty description="Нет подразделов" />
                ) : (
                  <Droppable droppableId={`categories-${selectedCategory.id}`} direction="horizontal" type="categories">
                {(provided) => (
                  <div className="menu-grid" ref={provided.innerRef} {...provided.droppableProps}>
                    {selectedCategory.children.map((child, index) => (
                      <Draggable key={child.id} draggableId={`category-${child.id}`} index={index}>
                        {(dragProvided) => (
                          <Card
                            ref={dragProvided.innerRef}
                            {...dragProvided.draggableProps}
                            {...dragProvided.dragHandleProps}
                            className="menu-card"
                            cover={child.image_url ? (
                              <div className="menu-card-cover" style={{ backgroundImage: `url(${child.image_url})` }} />
                            ) : (
                              <div className="menu-card-cover menu-card-cover--empty">
                                <Text>Нет изображения</Text>
                              </div>
                            )}
                            actions={isSuperAdmin ? [
                              <Button type="text" icon={<EditOutlined />} onClick={() => openCategoryModal('edit', selectedCategory.id, child)} />,
                              <Button danger type="text" icon={<DeleteOutlined />} onClick={() => handleDeleteCategory(child)} />,
                              <Button type="text" icon={<PlusOutlined />} onClick={() => openServiceModal('create', child.id)}>Услуга</Button>,
                            ] : []}
                          >
                            <Title level={5}>{child.name}</Title>
                            <Text type="secondary">
                              {child.services.length}
                              {' '}
                              услуг
                            </Text>
                          </Card>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
                )}
              </>
            )}

            <Divider />
            <Title level={5}>Услуги</Title>
            {isSuperAdmin && selectionMode && (
              <div className="bulk-actions">
                <Text strong>
                  {selectedServices.length > 0
                    ? `Выбрано услуг: ${selectedServices.length}`
                    : 'Выберите одну или несколько услуг для массовых действий'}
                </Text>
                <Space size="middle">
                  <Button
                    danger
                    disabled={selectedServices.length === 0}
                    onClick={handleBulkDelete}
                  >
                    Удалить
                  </Button>
                  <Button
                    disabled={selectedServices.length === 0}
                    onClick={() => handleBulkVisibility(true)}
                  >
                    Показать
                  </Button>
                  <Button
                    disabled={selectedServices.length === 0}
                    onClick={() => handleBulkVisibility(false)}
                  >
                    Скрыть
                  </Button>
                  <Button
                    disabled={selectedServices.length === 0}
                    onClick={handleOpenMoveModal}
                  >
                    Переместить в раздел
                  </Button>
                  <Button onClick={clearSelections}>Сбросить</Button>
                </Space>
              </div>
            )}
            {selectedCategory.services.length === 0 ? (
              <Empty description="Услуг пока нет" />
            ) : (
              <Droppable droppableId={`services-${selectedCategory.id ?? 'uncategorized'}`} type="services">
                {(provided) => (
                  <div className="menu-services-grid" ref={provided.innerRef} {...provided.droppableProps}>
                    {selectedCategory.services.map((service, index) => (
                      <Draggable key={service.id} draggableId={`service-${service.id}`} index={index}>
                        {(dragProvided) => (
                          <div ref={dragProvided.innerRef} {...dragProvided.draggableProps} {...dragProvided.dragHandleProps}>
                            {renderServiceCard(service)}
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            )}
          </div>
        )}
      </Drawer>

      <CategoryModal
        modal={categoryModal}
        onClose={() => setCategoryModal({ ...categoryModal, open: false })}
        onSubmit={handleCategorySubmit}
      />

      <ServiceModal
        modal={serviceModal}
        categories={tree}
        onClose={() => setServiceModal({ ...serviceModal, open: false })}
        onSubmit={handleServiceSubmit}
      />

      <MoveServicesModal
        open={moveModal.open}
        onClose={() => setMoveModal({ open: false })}
        categories={tree}
        onSubmit={handleMoveSubmit}
      />
    </div>
    </DragDropContext>
  );
};

const findCategoryById = (nodes, id) => {
  for (const node of nodes) {
    if (node.id === id) return node;
    const childResult = findCategoryById(node.children ?? [], id);
    if (childResult) return childResult;
  }
  return null;
};

const extractParentId = (droppableId) => {
  const raw = droppableId.replace(/^(categories|services)-/, '');
  if (raw === 'root') return null;
  const parsed = Number(raw);
  return Number.isNaN(parsed) ? null : parsed;
};

const reorderList = (list = [], startIndex, endIndex) => {
  const result = Array.from(list);
  const [removed] = result.splice(startIndex, 1);
  result.splice(endIndex, 0, removed);
  return result;
};

const CategoryModal = ({ modal, onClose, onSubmit }) => {
  const [form] = Form.useForm();
  const imageUrl = Form.useWatch('image_url', form);

  useEffect(() => {
    if (modal.open) {
      form.setFieldsValue({
        name: modal.initial.name,
        description: modal.initial.description,
        image_url: modal.initial.image_url,
        order_index: modal.initial.order_index ?? 0,
        is_active: modal.initial.is_active ?? true,
      });
    } else {
      form.resetFields();
    }
  }, [modal, form]);

  return (
    <Modal
      title={modal.mode === 'create' ? 'Новый раздел' : 'Редактировать раздел'}
      open={modal.open}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Сохранить"
    >
      <Form layout="vertical" form={form} onFinish={onSubmit}>
        <Form.Item label="Название" name="name" rules={[{ required: true, message: 'Введите название' }]}>
          <Input placeholder="Например, Спа-программы" />
        </Form.Item>
        <Form.Item label="Описание" name="description">
          <Input.TextArea rows={3} placeholder="Краткое описание раздела" />
        </Form.Item>
        <Form.Item label="Изображение">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Form.Item name="image_url" noStyle>
              <Input placeholder="https://..." />
            </Form.Item>
            <ImageUploadDropzone onUploaded={(url) => form.setFieldsValue({ image_url: url })} />
            {imageUrl && (
              <img src={imageUrl} alt="preview" style={{ marginTop: 12, width: '100%', borderRadius: 12 }} />
            )}
          </Space>
        </Form.Item>
        <Form.Item label="Порядок" name="order_index" initialValue={0}>
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="Показывать" name="is_active" valuePropName="checked">
          <Switch checkedChildren="Активна" unCheckedChildren="Скрыта" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

const ServiceModal = ({
  modal,
  onClose,
  onSubmit,
  categories,
}) => {
  const [form] = Form.useForm();
  const cardImage = Form.useWatch('image_url', form);
  const detailImage = Form.useWatch('detail_image_url', form);
  const previewName = Form.useWatch('name', form);
  const previewSubtitle = Form.useWatch('subtitle', form);
  const previewPrice = Form.useWatch('price', form);
  const previewDuration = Form.useWatch('duration', form);
  const previewHighlights = Form.useWatch('highlights', form);

  useEffect(() => {
    if (modal.open) {
      const categoryOptions = flattenCategories(categories);
      const initial = modal.initial ?? {};
      form.setFieldsValue({
        name: initial.name,
        subtitle: initial.subtitle,
        description: initial.description,
        price: initial.price,
        duration: initial.duration,
        category_id: modal.categoryId ?? initial.category_id,
        image_url: initial.image_url,
        detail_image_url: initial.detail_image_url,
        order_index: initial.order_index ?? 0,
        highlights: initial.highlights,
        additional_services: initial.additional_services?.map((item) => item.name),
        is_active: initial.is_active ?? true,
      });
      form.setFieldValue('category_id', modal.categoryId ?? initial.category_id ?? categoryOptions[0]?.value);
    } else {
      form.resetFields();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modal.open, modal.categoryId, modal.mode]);

  const categoryOptions = useMemo(() => flattenCategories(categories), [categories]);

  return (
    <Modal
      title={modal.mode === 'create' ? 'Новая услуга' : 'Редактировать услугу'}
      open={modal.open}
      width={720}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Сохранить"
    >
      <Form layout="vertical" form={form} onFinish={onSubmit}>
        <Form.Item label="Название" name="name" rules={[{ required: true, message: 'Введите название' }]}>
          <Input placeholder="ORIGINAL HEAD SPA" />
        </Form.Item>
        <Form.Item label="Подзаголовок" name="subtitle">
          <Input placeholder="оригинальный протокол спа головы" />
        </Form.Item>
        <Form.Item label="Описание" name="description">
          <Input.TextArea rows={4} placeholder="Расскажите о процедуре" />
        </Form.Item>
        <Form.Item label="Категория" name="category_id" rules={[{ required: false, message: 'Выберите категорию' }]}>
          <Select 
            options={categoryOptions} 
            placeholder="Выберите категорию (необязательно)" 
            allowClear
          />
        </Form.Item>
        <Form.Item label="Цена, ₽" name="price">
          <InputNumber min={0} step={100} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="Длительность, минут" name="duration">
          <InputNumber min={0} step={10} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="Изображение карточки">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Form.Item name="image_url" noStyle>
              <Input placeholder="https://..." />
            </Form.Item>
            <ImageUploadDropzone onUploaded={(url) => form.setFieldsValue({ image_url: url })} />
            {cardImage && (
              <img src={cardImage} alt="card" style={{ marginTop: 12, width: '100%', borderRadius: 12 }} />
            )}
          </Space>
        </Form.Item>
        <Form.Item label="Изображение в деталях">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Form.Item name="detail_image_url" noStyle>
              <Input placeholder="https://..." />
            </Form.Item>
            <ImageUploadDropzone onUploaded={(url) => form.setFieldsValue({ detail_image_url: url })} />
            {detailImage && (
              <img src={detailImage} alt="detail" style={{ marginTop: 12, width: '100%', borderRadius: 12 }} />
            )}
          </Space>
        </Form.Item>
        <Form.Item label="Теги/Highlights" name="highlights">
          <Select mode="tags" placeholder="Например, премиум, расслабление" />
        </Form.Item>
        <Form.Item label="Доп. услуги" name="additional_services">
          <Select mode="tags" placeholder="Горячие камни, массаж головы..." />
        </Form.Item>
        <Form.Item label="Показывать в приложении" name="is_active" valuePropName="checked" initialValue>
          <Switch checkedChildren="Опубликована" unCheckedChildren="Черновик" />
        </Form.Item>
        <Form.Item label="Порядок" name="order_index" initialValue={0}>
          <InputNumber min={0} step={1} style={{ width: '100%' }} />
        </Form.Item>
        <Divider />
        <Title level={5}>Предпросмотр карточки</Title>
        <ServicePreview
          data={{
            name: previewName,
            subtitle: previewSubtitle,
            price: previewPrice,
            duration: previewDuration,
            imageUrl: cardImage,
            highlights: previewHighlights,
          }}
        />
      </Form>
    </Modal>
  );
};

const MoveServicesModal = ({
  open,
  onClose,
  categories,
  onSubmit,
}) => {
  const [form] = Form.useForm();
  const categoryOptions = useMemo(() => flattenCategories(categories), [categories]);

  useEffect(() => {
    if (!open) {
      form.resetFields();
    }
  }, [open, form]);

  return (
    <Modal
      title="Переместить услуги в раздел"
      open={open}
      onCancel={onClose}
      onOk={() => form.submit()}
      okText="Переместить"
    >
      <Form layout="vertical" form={form} onFinish={onSubmit}>
        <Form.Item
          label="Новый раздел"
          name="category_id"
          rules={[{ required: true, message: 'Выберите раздел' }]}
        >
          <Select
            options={categoryOptions}
            placeholder="Выберите раздел, в который нужно переместить услуги"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

const flattenCategories = (nodes, depth = 0) => {
  if (!nodes) return [];
  const items = [];
  nodes.forEach((node) => {
    items.push({
      label: `${'— '.repeat(depth)}${node.name}`,
      value: node.id,
    });
    items.push(...flattenCategories(node.children, depth + 1));
  });
  return items;
};

const ImageUploadDropzone = ({ onUploaded }) => {
  const [uploading, setUploading] = useState(false);

  return (
    <Upload.Dragger
      accept="image/*"
      multiple={false}
      showUploadList={false}
      className="image-dropzone"
      customRequest={async ({ file, onSuccess, onError }) => {
        try {
          setUploading(true);
          const { url } = await uploadMenuImage(file);
          onUploaded(url);
          message.success('Изображение загружено');
          onSuccess?.(null, file);
        } catch (error) {
          message.error(error?.response?.data?.detail ?? 'Ошибка загрузки');
          onError?.(error);
        } finally {
          setUploading(false);
        }
      }}
    >
      <p className="ant-upload-drag-icon">
        <UploadOutlined />
      </p>
      <p className="ant-upload-text">Перетащите изображение или нажмите для выбора</p>
      <p className="ant-upload-hint">PNG / JPG до 5 МБ</p>
      {uploading && <Spin size="small" />}
    </Upload.Dragger>
  );
};

const ServicePreview = ({ data }) => (
  <div className="service-preview-card">
    <div className="preview-image" style={{ backgroundImage: `url(${data?.imageUrl || ''})` }}>
      {!data?.imageUrl && <span>Предпросмотр изображения</span>}
      {data?.duration && (
        <span className="badge">
          {data.duration}
          {' '}
          мин.
        </span>
      )}
    </div>
    <div className="preview-body">
      <div className="preview-title">
        <strong>{data?.name || 'Название услуги'}</strong>
        {data?.price && (
          <span>
            {data.price}
            {' '}
            ₽
          </span>
        )}
      </div>
      {data?.subtitle && <p>{data.subtitle}</p>}
      {data?.highlights?.length > 0 && (
        <div className="preview-tags">
          {data.highlights.slice(0, 3).map((item) => (
            <Tag key={item}>{item}</Tag>
          ))}
        </div>
      )}
      <div className="preview-actions">
        <Button type="primary">
          {data?.bookButtonLabel || 'Подробнее'}
        </Button>
      </div>
    </div>
  </div>
);

export default MenuPage;


