import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/store/authSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        // Add other reducers here as features are implemented
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
