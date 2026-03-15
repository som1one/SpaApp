import { Layout, Menu, Avatar, Dropdown } from 'antd';
import {
  HomeOutlined,
  TeamOutlined,
  BellOutlined,
  LogoutOutlined,
  UserAddOutlined,
  MenuOutlined,
  StarOutlined,
  UserOutlined,
  FileImageOutlined,
} from '@ant-design/icons';
import { useMemo } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const { Header, Sider, Content } = Layout;

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const selectedKeys = useMemo(() => {
    if (location.pathname.startsWith('/bookings/cancelled')) return ['bookings-cancelled'];
    if (location.pathname.startsWith('/bookings')) return ['bookings'];
    if (location.pathname.startsWith('/users')) return ['users'];
    if (location.pathname.startsWith('/invites')) return ['invites'];
    if (location.pathname.startsWith('/menu')) return ['menu'];
    if (location.pathname.startsWith('/loyalty')) return ['loyalty'];
    if (location.pathname.startsWith('/staff')) return ['staff'];
    if (location.pathname.startsWith('/custom-content')) return ['custom-content'];
    if (location.pathname.startsWith('/audit')) return ['audit'];
    if (location.pathname.startsWith('/notifications')) return ['notifications'];
    return ['dashboard'];
  }, [location.pathname]);

  const isSuperAdmin = user?.role === 'super_admin';

  // Обычные админы видят главную, записи и SPA-меню (только просмотр),
  // все остальные разделы доступны только супер-админам.
  const baseMenuItems = [
    { key: 'dashboard', icon: <HomeOutlined />, label: 'Главная' },
    { key: 'bookings', icon: <BellOutlined />, label: 'Записи' },
    { key: 'bookings-cancelled', icon: <BellOutlined />, label: 'Отменённые' },
    { key: 'menu', icon: <MenuOutlined />, label: 'SPA-меню' },
  ];

  const superAdminExtraItems = [
    { key: 'staff', icon: <UserOutlined />, label: 'Мастера' },
    { key: 'loyalty', icon: <StarOutlined />, label: 'Лояльность' },
    { key: 'custom-content', icon: <FileImageOutlined />, label: 'Контент' },
    { key: 'users', icon: <TeamOutlined />, label: 'Пользователи' },
    { key: 'invites', icon: <UserAddOutlined />, label: 'Приглашения' },
    { key: 'audit', icon: <BellOutlined />, label: 'Аудит' },
    { key: 'notifications', icon: <BellOutlined />, label: 'Рассылки' },
  ];

  const menuItems = isSuperAdmin
    ? [...baseMenuItems, ...superAdminExtraItems]
    : baseMenuItems;

  const profileMenu = {
    items: [
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: 'Выйти',
        onClick: () => {
          logout();
          navigate('/login');
        },
      },
    ],
  };

  return (
    <Layout className="admin-layout">
      <Sider breakpoint="lg" collapsedWidth="0" theme="light">
        <div className="brand">
          PRIRODA SPA
        </div>
        <Menu
          mode="inline"
          items={menuItems}
          selectedKeys={selectedKeys}
          onClick={({ key }) => {
            if (key === 'dashboard') navigate('/');
            else if (key === 'bookings') navigate('/bookings');
            else if (key === 'bookings-cancelled') navigate('/bookings/cancelled');
            else navigate(`/${key}`);
          }}
        />
      </Sider>
      <Layout>
        <Header className="admin-header">
          <div className="header-actions">
            <Dropdown menu={profileMenu} placement="bottomRight">
              <div className="profile-chip">
                <Avatar size={36}>
                  {(user?.name || 'Гость').charAt(0).toUpperCase()}
                </Avatar>
                <div>
                  <div className="profile-name">{user?.name ?? 'Администратор'}</div>
                  <div className="profile-role">Админ панель</div>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content className="admin-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;


