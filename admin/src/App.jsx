import { Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './layouts/AdminLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import InvitesPage from './pages/InvitesPage';
import AcceptInvitePage from './pages/AcceptInvitePage';
import MenuPage from './pages/MenuPage';
import UsersPage from './pages/UsersPage';
import AuditPage from './pages/AuditPage';
import NotificationsPage from './pages/NotificationsPage';
import LoyaltyPage from './pages/LoyaltyPage';
import StaffPage from './pages/StaffPage';
import CustomContentPage from './pages/CustomContentPage';
import BookingsPage from './pages/BookingsPage';
import CancelledBookingsPage from './pages/CancelledBookingsPage';

const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/invite/:token" element={<AcceptInvitePage />} />
    <Route
      path="/"
      element={(
        <ProtectedRoute>
          <AdminLayout />
        </ProtectedRoute>
      )}
    >
      <Route index element={<DashboardPage />} />
      <Route path="bookings" element={<BookingsPage />} />
      <Route path="bookings/cancelled" element={<CancelledBookingsPage />} />
      <Route path="menu" element={<MenuPage />} />
      <Route path="users" element={<UsersPage />} />
      <Route path="invites" element={<InvitesPage />} />
      <Route path="audit" element={<AuditPage />} />
      <Route path="notifications" element={<NotificationsPage />} />
      <Route path="loyalty" element={<LoyaltyPage />} />
      <Route path="staff" element={<StaffPage />} />
      <Route path="custom-content" element={<CustomContentPage />} />
    </Route>
  </Routes>
);

export default App;
