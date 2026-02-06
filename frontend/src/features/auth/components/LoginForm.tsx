import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope, faLock, faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { login, clearError } from '../store/authSlice';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

const LoginForm: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const { loading, error } = useAppSelector((state) => state.auth);

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [formErrors, setFormErrors] = useState<{ email?: string; password?: string }>({});

    const validate = () => {
        const errors: { email?: string; password?: string } = {};
        if (!email) errors.email = 'El correo es obligatorio';
        else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Correo inválido';

        if (!password) errors.password = 'La contraseña es obligatoria';

        setFormErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        const result = await dispatch(login({ email, password }));
        if (login.fulfilled.match(result)) {
            navigate('/workspaces');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Bienvenido de nuevo</h3>
                <p className="text-slate-500 text-sm mt-2">Ingresa tus credenciales para acceder a tu espacio.</p>
            </div>

            {error && (
                <div className="p-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-xl font-medium mb-4">
                    {error}
                </div>
            )}

            <Input
                label="Correo Electrónico"
                type="email"
                placeholder="ejemplo@wiselab.com"
                value={email}
                onChange={(e) => {
                    setEmail(e.target.value);
                    if (error) dispatch(clearError());
                }}
                error={formErrors.email}
                icon={<FontAwesomeIcon icon={faEnvelope} />}
            />

            <Input
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                    setPassword(e.target.value);
                    if (error) dispatch(clearError());
                }}
                error={formErrors.password}
                icon={<FontAwesomeIcon icon={faLock} />}
                rightIcon={
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="p-1 focus:outline-none"
                    >
                        <FontAwesomeIcon icon={showPassword ? faEyeSlash : faEye} />
                    </button>
                }
            />

            <div className="flex items-center justify-between mb-6">
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-primary focus:ring-primary" />
                    <span className="text-sm text-slate-600">Recordarme</span>
                </label>
                <button type="button" className="text-sm font-semibold text-primary hover:underline">
                    ¿Olvidaste tu contraseña?
                </button>
            </div>

            <Button type="submit" fullWidth loading={loading}>
                Entrar
            </Button>
        </form>
    );
};

export default LoginForm;
