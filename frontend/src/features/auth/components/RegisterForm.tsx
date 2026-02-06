import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faEnvelope, faLock, faRocket } from '@fortawesome/free-solid-svg-icons';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { register, clearError } from '../store/authSlice';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

const RegisterForm: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const { loading, error } = useAppSelector((state) => state.auth);

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [formErrors, setFormErrors] = useState<Record<string, string>>({});

    const validate = () => {
        const errors: Record<string, string> = {};
        if (!formData.name) errors.name = 'El nombre es obligatorio';
        if (!formData.email) errors.email = 'El correo es obligatorio';
        else if (!/\S+@\S+\.\S+/.test(formData.email)) errors.email = 'Correo inválido';

        if (formData.password.length < 8) errors.password = 'Mínimo 8 caracteres';
        if (formData.password !== formData.confirmPassword) errors.confirmPassword = 'Las contraseñas no coinciden';

        setFormErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        const result = await dispatch(register(formData));
        if (register.fulfilled.match(result)) {
            navigate('/workspaces');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="mb-6">
                <h3 className="text-2xl font-bold text-slate-900">Comienza hoy</h3>
                <p className="text-slate-500 text-sm mt-2">Crea tu cuenta en WiseLab y toma el control.</p>
            </div>

            {error && (
                <div className="p-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-xl font-medium mb-4">
                    {error}
                </div>
            )}

            <Input
                label="Nombre Completo"
                placeholder="Juan Pérez"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                error={formErrors.name}
                icon={<FontAwesomeIcon icon={faUser} />}
            />

            <Input
                label="Correo Electrónico"
                type="email"
                placeholder="juan@ejemplo.com"
                value={formData.email}
                onChange={(e) => {
                    setFormData({ ...formData, email: e.target.value });
                    if (error) dispatch(clearError());
                }}
                error={formErrors.email}
                icon={<FontAwesomeIcon icon={faEnvelope} />}
            />

            <div className="grid grid-cols-2 gap-4">
                <Input
                    label="Contraseña"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    error={formErrors.password}
                    icon={<FontAwesomeIcon icon={faLock} />}
                />
                <Input
                    label="Repetir"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    error={formErrors.confirmPassword}
                    icon={<FontAwesomeIcon icon={faLock} />}
                />
            </div>

            <label className="flex items-center gap-2 cursor-pointer mb-6">
                <input type="checkbox" required className="w-4 h-4 rounded border-slate-300 text-primary focus:ring-primary" />
                <span className="text-xs text-slate-500">
                    Acepto los términos y condiciones de servicio.
                </span>
            </label>

            <Button type="submit" fullWidth loading={loading} className="gap-2">
                <FontAwesomeIcon icon={faRocket} />
                Crear Cuenta
            </Button>
        </form>
    );
};

export default RegisterForm;
