import { createContext } from 'react';

export const AuthContext = createContext({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  completeInvite: async () => {},
  refreshProfile: async () => {},
});
