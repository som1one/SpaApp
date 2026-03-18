import { useEffect, useState } from 'react';
import { fetchCurrentUser, login as apiLogin, logout as apiLogout } from '../api/auth';
import { acceptInvite as acceptInviteApi } from '../api/invites';
import { AuthContext } from './auth-context';

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        // Используем Promise.race для таймаута
        const profilePromise = fetchCurrentUser();
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 5000)
        );
        
        const profile = await Promise.race([profilePromise, timeoutPromise]);
        if (profile?.is_authenticated) {
          setUser(profile);
        }
      } catch (error) {
        // Игнорируем ошибки при инициализации - пользователь может быть не авторизован
        console.debug('Auth init error (ignored):', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const refreshProfile = async () => {
    const profile = await fetchCurrentUser();
    if (!profile?.is_authenticated) {
      throw new Error('Недостаточно прав для доступа');
    }
    setUser(profile);
    return profile;
  };

  const login = async (email, password) => {
    await apiLogin(email, password);
    return refreshProfile();
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  const completeInvite = async (token, password) => {
    const response = await acceptInviteApi(token, password);
    setUser(response.profile);
    return response.profile;
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      completeInvite,
      refreshProfile,
    }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export { AuthProvider };
